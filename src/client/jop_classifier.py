import json
import os
import re
import requests





class JobFilterPipeline2:

    # ── your stack — AI scores against this ──────────────────────────────────
    MY_STACK = [
        # ── Leadership / role ────────────────────────────────────────
        "devops", "devsecops", "sre", "site reliability", "platform",
        "platform engineering", "engineering manager", "architect",
        "cloud architect", "devops manager", "sre manager",

        # ── Cloud & infra ────────────────────────────────────────────
        "aws", "gcp", "azure", "docker", "kubernetes", "cka", "eks",
        "aks", "gke", "ci/cd", "github actions", "jenkins", "terraform",
        "ansible", "linux", "nginx", "helm", "argocd", "prometheus",
        "grafana", "vault", "cyberark", "finops", "observability",
        "ec2", "s3", "lambda", "cloudwatch", "iam",

        # ── Delivery / security ──────────────────────────────────────
        "devops", "devsecops", "security", "hitRUST", "hipaa",
        "incident management", "slo", "on-call", "reliability",

        # ── Automation & platform tooling ────────────────────────────
        "python", "bash", "powershell", "react", "typescript",
        "artifactory", "jfrog", "xray", "mcp", "rag",
    ]

    # ── hard veto BEFORE ai — title only, zero ambiguity ────────────────────
    VETO_TITLES = [
        "walk-in", "walkin", "walk in",
        "android developer", "ios developer", "flutter developer",
        "frontend developer", "front-end developer",
        "founder", "tutor", "trainer",
        "data scientist", "ml engineer", "data engineer", "intern", "internship",
        "etl engineer", "prompt engineer",
        "analyst", "associate is engineer",
    ]


    VETO_COMPANIES = {
    "accenture", "wipro", "infosys", "tcs", "cognizant",
    "capgemini", "hcl", "tech mahindra", "mphasis", "hexaware",
    "ltimindtree", "persistent", "birlasoft",
}

    # ── red flag sniff on description (cheap, pre-ai) ───────────────────────
    # Only the things AI genuinely can't infer from tags alone
    DESC_RED_FLAGS = {
        "walk-in":      r"walk.?in|walkin",
        "venue listed": r"venue\s*:|interview venue|bring your resume|carry your resume",
    }




    SOFTWARE_KEYWORDS = {
        "software", "developer", "engineer", "engineering",
        "devops", "devsecops", "cloud", "sre", "platform",
        "architect", "manager", "reliability", "infrastructure",
        "kubernetes", "terraform", "aws", "azure", "gcp",
        "tech lead", "sde", "swe",
    }

    # if ANY of these appear in title → drop it
    FRONTEND_VETO_KEYWORDS = {
        "frontend", "front-end", "front end",
        "angular", "vue", "ui developer", "ui engineer",
        "android", "ios", "flutter", "mobile", "kotlin", "swift",
        "embedded", "firmware",
        "ml engineer", "data engineer", "data scientist", "intern", "internship",
        "golang developer", "java developer", "php developer",
    }

    def __init__(
        self,
        openai_api_key,
        cache_file="score_cache.json",
        daily_apply_limit=50,
        min_apply_score=50,
        ai_score_limit=300,
        batch_size=50,
    ):
        self.api_key           = openai_api_key
        self.url               = "https://api.openai.com/v1/chat/completions"
        self.cache_file        = cache_file
        self.daily_apply_limit = daily_apply_limit
        self.min_apply_score   = min_apply_score
        self.ai_score_limit    = ai_score_limit
        self.batch_size        = batch_size
        self.cache             = self._load_cache()

    # =========================================================
    # MAIN
    # =========================================================
    def run(self, jobs):
        print("\nRAW JOBS:", len(jobs))

        jobs = self.normalize_jobs(jobs)
        print("AFTER NORMALIZE:", len(jobs))

        jobs = self.dedup(jobs)
        print("AFTER DEDUP:", len(jobs))

        jobs = self.hard_veto(jobs)
        print("AFTER HARD VETO:", len(jobs))

        jobs = self.experience_filter(jobs)
        print("AFTER EXP FILTER:", len(jobs))

        jobs = self.desc_red_flag_check(jobs)
        print("AFTER RED FLAG CHECK:", len(jobs))

        jobs=self.title_filter(jobs)
        print("AFTER TITLE FILTER:", len(jobs))

        jobs = self.company_veto(jobs)        # ← add here
        print("AFTER COMPANY VETO:", len(jobs))


        jobs = self.tag_presort(jobs)

        jobs = jobs[:self.ai_score_limit]
        print("AFTER LIMIT:", len(jobs))

        jobs = self.ai_score_batch(jobs)

        jobs = self.rank(jobs)
        print("AFTER RANK:", len(jobs))

        jobs = self.select(jobs)
        print("FINAL SELECTED:", len(jobs))

        for j in jobs:
            print(f"  {j.get('ai_score'):>3}  {j.get('title')} @ {j.get('company')}"
                  f"  |  {j.get('ai_reason', '')}")

        return jobs

    # =========================================================
    # NORMALIZE  — tags are the star, keep them clean
    # =========================================================
    def normalize_jobs(self, jobs):
        normalized = []

        for j in jobs:
            job = j if isinstance(j, dict) else j.__dict__

            # days old
            posted   = (job.get("posted_date") or "").lower()
            days_old = 7
            if "today" in posted or "hour" in posted or "just now" in posted:
                days_old = 0
            elif "yesterday" in posted:
                days_old = 1
            else:
                m = re.search(r"(\d+)\s*day", posted)
                if m:
                    days_old = int(m.group(1))
                else:
                    m = re.search(r"(\d+)\s*week", posted)
                    if m:
                        days_old = int(m.group(1)) * 7

            # experience range
            exp = job.get("experience") or ""
            exp_min, exp_max = 0, 10
            nums = re.findall(r"\d+", exp)
            if len(nums) >= 2:
                exp_min, exp_max = int(nums[0]), int(nums[1])
            elif len(nums) == 1:
                exp_min = exp_max = int(nums[0])

            # tags — normalize once, use everywhere
            raw_tags = job.get("tags") or job.get("skills") or []
            if isinstance(raw_tags, str):
                raw_tags = re.split(r"[,;|]", raw_tags)
            tags = [t.strip().lower() for t in raw_tags if t.strip()]

            normalized.append({
                "job_id":         job.get("job_id"),
                "title":          (job.get("title")       or "").strip(),
                "company":        (job.get("company")     or "").strip(),
                "location":       (job.get("location")    or "").strip(),
                "description":    (job.get("description") or "").strip(),
                "tags":           tags,
                "mandatory_tags": tags[:2],   # site signals these as primary
                "optional_tags":  tags[2:],
                "days_old":       days_old,
                "experience_min": exp_min,
                "experience_max": exp_max,
            })

        return normalized

    # =========================================================
    # DEDUP
    # =========================================================
    def dedup(self, jobs):
        seen, result = set(), []
        for j in jobs:
            job_id = j.get("job_id")
            if job_id is None:
                result.append(j)  # can't dedup without an id, just keep it
                continue
            if job_id in seen:
                continue
            seen.add(job_id)
            result.append(j)
        return result

    # =========================================================
    # HARD VETO  — title only, no ambiguity allowed
    # =========================================================
    def hard_veto(self, jobs):
        clean = []
        for j in jobs:
            title = (j.get("title") or "").lower()
            if any(kw in title for kw in self.VETO_TITLES):
                print(f"  [VETO] {j.get('title')}")
                continue
            clean.append(j)
        return clean

    # =========================================================
    # EXPERIENCE FILTER
    # =========================================================
    def experience_filter(self, jobs):
        # Target senior roles around 8 years. Keep jobs whose band overlaps 6-12.
        return [
            j for j in jobs
            if j.get("experience_min", 0) <= 10
            and j.get("experience_max", 10) >= 6
        ]

    # =========================================================
    # DESC RED FLAG CHECK  — one cheap regex pass, nothing more
    # =========================================================
    def desc_red_flag_check(self, jobs):
        clean = []
        for j in jobs:
            desc = (j.get("description") or "").lower()
            flagged = [
                label for label, pat in self.DESC_RED_FLAGS.items()
                if re.search(pat, desc)
            ]
            if flagged:
                print(f"  [RED FLAG {flagged}] {j.get('title')}")
                continue
            clean.append(j)
        return clean

    # =========================================================
    # TAG PRESORT  — rough stack overlap count, no AI cost
    # Keeps best candidates at the front before we hit the limit
    # =========================================================

    def title_filter(self, jobs):
        result = []
        for j in jobs:
            title = (j.get("title") or "").lower()

            # must have at least one software keyword
            if not any(kw in title for kw in self.SOFTWARE_KEYWORDS):
                print(f"  [TITLE FILTER - not software] {j.get('title')}")
                continue

            # must NOT be frontend/mobile/ml
            if any(kw in title for kw in self.FRONTEND_VETO_KEYWORDS):
                print(f"  [TITLE FILTER - frontend/mobile] {j.get('title')}")
                continue

            result.append(j)
        return result


    def company_veto(self, jobs):
        clean = []
        for j in jobs:
            company = (j.get("company") or "").lower()
            if any(vc in company for vc in self.VETO_COMPANIES):
                print(f"  [COMPANY VETO] {j.get('title')} @ {j.get('company')}")
                continue
            clean.append(j)
        return clean

    def tag_presort(self, jobs):
        my_stack = set(self.MY_STACK)

        def overlap(j):
            tags     = set(j.get("tags", []))
            mandatory_hit = sum(1 for t in j.get("mandatory_tags", []) if t in my_stack)
            total_hit     = len(tags & my_stack)
            recency_bonus = max(0, 7 - j.get("days_old", 7))
            # mandatory tags weighted 3x — they represent the job's core ask
            return mandatory_hit * 3 + total_hit + recency_bonus

        return sorted(jobs, key=overlap, reverse=True)

    # =========================================================
    # AI SCORING  — tags go in, score + reason come out
    # =========================================================
    def ai_score_batch(self, jobs):
        result = []
        for i in range(0, len(jobs), self.batch_size):
            batch  = jobs[i:i + self.batch_size]
            scores = self._call_ai(batch)
            for idx, job in enumerate(batch):
                jid  = str(job.get("job_id") or "")
                data = self.cache.get(jid) if jid else None

                if not data:
                    data = scores.get(str(idx), {"score": 0, "reason": "no response"})
                    if not isinstance(data.get("score"), int):
                        data = {"score": 0, "reason": "parse error"}
                    if jid:
                        self.cache[jid] = data

                job["ai_score"]  = data.get("score", 0)
                job["ai_reason"] = data.get("reason", "")
                result.append(job)

        self._save_cache()
        return result

    def _call_ai(self, jobs):
        job_block = ""
        for i, j in enumerate(jobs):
            mandatory = ", ".join(j.get("mandatory_tags", [])) or "none"
            optional  = ", ".join(j.get("optional_tags",  [])) or "none"
            exp       = f"{j.get('experience_min', 0)}-{j.get('experience_max', 10)} yrs"

            job_block += (
                f"Job {i}:\n"
                f"  Title:     {j.get('title')}\n"
                f"  Company:   {j.get('company')}\n"
                f"  Mandatory: {mandatory}\n"
                f"  Optional:  {optional}\n"
                f"  Exp:       {exp}\n"
                f"  Days old:  {j.get('days_old', 7)}\n"
                f"---\n"
            )
        



        prompt = f"""
You are scoring job listings for a senior DevSecOps / SRE / Platform / Engineering Manager candidate. Score each job 0-100.

CANDIDATE:
- 8+ years experience
- Targeting: DevOps Manager, DevSecOps Manager, SRE Manager, Platform Engineering Manager,
  Cloud/DevOps Architect, Engineering Manager (infra/platform), Senior DevOps/SRE
- Core stack: AWS, Azure, GCP, Kubernetes, Terraform, Jenkins, CI/CD, Vault/CyberArk,
  observability, FinOps, DevSecOps, incident/SLO ownership
- Also knows: Python automation, React/TypeScript developer-portal work, Artifactory/Xray, MCP/RAG tooling
- Looking for senior leadership / architecture / platform ownership roles

SCORING:

85-100 — apply immediately
  Clear DevOps/SRE/Platform/Architecture/EM ownership, senior experience band around 6-12 yrs,
  cloud+kubernetes/terraform or leadership of infra teams.

60-84 — good fit, apply
  Strong DevOps/SRE/platform overlap, or EM/architect title with infra ownership signals.

35-59 — decent, worth applying
  Partial stack overlap or slightly junior/senior mismatch, but still infra/platform adjacent.

10-34 — weak match, skip unless desperate
  App-dev heavy with little infra/platform ownership.

0 — do not apply
  Pure frontend/mobile/data-science/walk-in, or zero DevOps/SRE/platform signal.

COMMON SENSE RULES:
- Engineering Manager + DevOps/Platform/SRE is a strong fit.
- Cloud Architect / DevOps Architect is a strong fit.
- Pure Java/React IC roles with no infra ownership should score low.
- Recency matters: jobs 0-1 days old get +5 bonus mentally.

Return ONLY valid JSON, no explanation outside it:
{{
  "0": {{"score": 90, "reason": "DevOps Manager, 8-12 yrs, Kubernetes/AWS"}},
  "1": {{"score": 0,  "reason": "Frontend-only role"}}
}}

Jobs:
{job_block}
"""

        try:
            res = requests.post(
                self.url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type":  "application/json",
                },
                json={
                    "model":       "gpt-4o-mini",
                    "messages":    [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                },
                timeout=90,
            )

            if res.status_code != 200:
                print("AI HTTP ERROR:", res.status_code, res.text[:200])
                return {}

            content = res.json()["choices"][0]["message"]["content"]
            content = re.sub(r"```json|```", "", content).strip()
            match   = re.search(r"\{.*\}", content, re.S)
            if not match:
                print("AI PARSE ERROR — raw:", content[:300])
                return {}

            data = json.loads(match.group(0))
            return data if isinstance(data, dict) else {}

        except Exception as e:
            print("AI call error:", e)
            return {}

    # =========================================================
    # RANK  — ai score + small recency bump
    # =========================================================
    def rank(self, jobs):
        return sorted(
            jobs,
            key=lambda j: j.get("ai_score", 0) + max(0, 3 - j.get("days_old", 7)),
            reverse=True,
        )

    # =========================================================
    # SELECT
    # =========================================================
    def select(self, jobs):
        apply_list  = [j for j in jobs if j.get("ai_score", 0) >= self.min_apply_score]
        review_list = [j for j in jobs if 10 <= j.get("ai_score", 0) < self.min_apply_score]

        if review_list:
            print(f"\n── REVIEW MANUALLY ({len(review_list)}) ──")
            for j in review_list:
                print(f"  score={j.get('ai_score')}  {j.get('title')} @ {j.get('company')}"
                      f"  |  {j.get('ai_reason', '')}")

        return apply_list[:self.daily_apply_limit]

    # =========================================================
    # CACHE
    # =========================================================
    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file) as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_cache(self):
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f, indent=2)