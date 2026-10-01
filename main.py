
# from src.client.naukri_client import NaukriLoginClient
# from src.client.job_client import NaukriJobClient
# from src.client.hirist_client import HiristClient, HiristError, find_hirist_url
# from dotenv import load_dotenv
# from colorama import Fore, Style, init
# from datetime import datetime
# import os
# load_dotenv()
# import time

# init(autoreset=True)

# if __name__ == "__main__":
#     # ---------------------------------------------------------------
#     # Load credentials from .env file
#     # ---------------------------------------------------------------
#     username = os.getenv("N_USERNAME")
#     password = os.getenv("N_PASSWORD")

#     # ---------------------------------------------------------------
#     # 1. Login — authenticates and stores session + bearer token
#     # ---------------------------------------------------------------
#     client = NaukriLoginClient(username, password)
#     client.login()
#     hirist = HiristClient(username, password)

#     # ---------------------------------------------------------------
#     # 2. Resume upload — uploads a new PDF resume to your profile
#     # ---------------------------------------------------------------
#     print(client.update_resume(r"ShivamCV.pdf"))

#     # ---------------------------------------------------------------
#     # 3. Profile update — update headline and summary independently
#     # ---------------------------------------------------------------
#     print(client.update_profile(headline="DevSecOps Manager & Platform / SRE Lead | Helping enterprises solve cloud cost, security, reliability and delivery bottlenecks | 2x AWS Certified | CKA | ex-KPMG, Infosys, Ericsson."
#     ))

#     print(client.update_profile(summary="CKA and AWS Certified Senior DevOps, SRE, and Platform Engineering leader with 8+ years owning CI/CD platforms and large scale cloud reliability across healthcare, banking, and telecommunications. Administers Jenkins, JFrog Artifactory and XRay. Builds automation and Developer Portal plugins (React, TypeScript) and leads SRE/DevOps engineers through Scrum-based operations, incident and change governance, stakeholder alignment, SLO ownership, on-call incident command, and cross-functional delivery. Operates cloud platforms on AWS, Azure, and GCP spanning Kubernetes, Terraform, Vault/CyberArk secrets, DevSecOps, SRE, FinOps, and LLM tooling including MCP and RAG. Delivered 75% infrastructure cost reduction, 142% increase in deployment frequency, and 92% lower MTTR. Supported HIPAA/HITRUST and ONC certification through audit remediation and penetration-test finding closure."))

#     # ---------------------------------------------------------------
#     # 5. Recommended jobs + targeted senior DevOps/SRE/Platform search
#     # ---------------------------------------------------------------
#     jc = NaukriJobClient(client)
#     jobs = jc.get_recommended_jobs()

#     print("Searching jobs...")
#     search_queries = [
#         "DevOps Manager",
#         "DevSecOps Manager",
#         "SRE Manager",
#         "Site Reliability Engineering Manager",
#         "Platform Engineering Manager",
#         "Platform Engineering Lead",
#         "Cloud Engineering Manager",
#         "Infrastructure Engineering Manager",
#         "Cloud Architect",
#         "Cloud Platform Architect",
#         "DevOps Architect",
#         "DevSecOps Architect",
#         "Platform Architect",
#         "Engineering Manager DevOps",
#         "Engineering Manager SRE",
#         "Senior DevOps Engineer",
#         "Senior DevSecOps Engineer",
#         "Senior SRE",
#         "Senior Site Reliability Engineer",
#         "Senior Platform Engineer",
#         "Staff DevOps Engineer",
#         "Staff SRE",
#         "Staff Platform Engineer",
#         "Principal DevOps Engineer",
#         "Principal SRE",
#         "Principal Platform Engineer",
#     ]

#     seen_ids = set()
#     combined = []
#     for keyword in search_queries:
#         try:
#             found = jc.search_jobs(keyword=keyword, experience=8, page=1, job_age=3)
#             for job in found:
#                 if job.job_id and job.job_id not in seen_ids:
#                     seen_ids.add(job.job_id)
#                     combined.append(job)
#             time.sleep(1.0)
#         except Exception as e:
#             print(f"{Fore.RED}Search failed for {keyword}: {e}{Style.RESET_ALL}")

#     # Prefer search results for apply; fall back to recommended if search empty.
#     jobs = combined or jobs

#     if not jobs:
#         print(f"{Fore.YELLOW}  No jobs found.{Style.RESET_ALL}")
#     else:
#         print(f"{Fore.GREEN}Found {len(jobs)} jobs{Style.RESET_ALL}")

#         for job in jobs:
#             print(f"\n{Fore.CYAN}{'─'*50}{Style.RESET_ALL}")
#             print(f"{Fore.WHITE}  Title   : {Fore.YELLOW}{job.title}")
#             print(f"{Fore.WHITE}  Company : {Fore.YELLOW}{job.company}")
#             print(f"{Fore.WHITE}  Job ID  : {Fore.YELLOW}{job.job_id}")
#             print(f"{Fore.WHITE}  Tags    : {Fore.YELLOW}{job.tags}")

#             mandatory = ["DevOps", "Kubernetes"]
#             optional  = ["AWS", "Terraform", "SRE", "CI/CD"]

#             try:
#                 external_info = jc.get_external_apply_info(job.job_id)
#                 if external_info.get("is_hirist") and external_info.get("hirist_url"):
#                     hirist.apply_from_url(external_info["hirist_url"])
#                     print(f"{Fore.GREEN}  ✅ Applied via Hirist: {external_info['hirist_url']}{Style.RESET_ALL}")
#                     time.sleep(3)
#                     continue

#                 if external_info.get("external"):
#                     print(f"{Fore.YELLOW}   Skipped — external company apply{Style.RESET_ALL}")
#                     continue

#                 result = jc.apply_job(
#                     job,
#                     mandatory_skills=mandatory,
#                     optional_skills=optional,
#                     source="recommended",
#                 )

#                 hirist_url = find_hirist_url(result)
#                 if hirist_url:
#                     hirist.apply_from_url(hirist_url)
#                     print(f"{Fore.GREEN}  ✅ Applied via Hirist: {hirist_url}{Style.RESET_ALL}")
#                     time.sleep(3)
#                     continue

#                 job_result = (result.get("jobs") or [{}])[0]
#                 if job_result.get("questionnaire"):
#                     print(f"{Fore.YELLOW}   Questionnaire detected — answering automatically{Style.RESET_ALL}")
#                     sid = datetime.utcnow().strftime("%Y%m%d%H%M%S") + "0000000"
#                     questionnaire_result = jc.handle_static_questionnaire_and_apply(
#                         job,
#                         questionnaire=job_result["questionnaire"],
#                         sid=sid,
#                         mandatory_skills=mandatory,
#                         optional_skills=optional,
#                         source="recommended",
#                     )
#                     if questionnaire_result.get("success") is False:
#                         print(f"{Fore.RED}   Failed to answer questionnaire: {questionnaire_result.get('error')}{Style.RESET_ALL}")
#                         continue

#                 print(f"{Fore.GREEN}  ✅ Applied successfully!{Style.RESET_ALL}")

#             except HiristError as e:
#                 print(f"{Fore.RED}   Hirist failed: {e}{Style.RESET_ALL}")
#             except Exception as e:
#                 print(f"{Fore.RED}   Failed: {e}{Style.RESET_ALL}")

#             time.sleep(3)


import os
import re
import time
from datetime import datetime, timezone

from colorama import Fore, Style, init
from dotenv import load_dotenv

from src.client.hirist_client import (
    HiristClient,
    HiristError,
    find_hirist_url,
)
from src.client.job_client import NaukriJobClient
from src.client.naukri_client import NaukriLoginClient


# =============================================================================
# CONFIGURATION
# =============================================================================

load_dotenv()
init(autoreset=True)

RESUME_FILE = "ShivamCV.pdf"

# Maximum number of successful applications per run.
MAX_APPLICATIONS = 30

# Search only recent jobs.
JOB_AGE_DAYS = 2

# Naukri search experience filter.
MIN_EXPERIENCE = 8

# Salary target.
# IMPORTANT:
#   Known salary below 50 LPA -> skip
#   Salary not disclosed       -> keep
#   Salary 50+ LPA             -> keep
TARGET_SALARY_LPA = 50

# Company size target.
# IMPORTANT:
#   Known company size below 1000 -> skip
#   Unknown company size           -> keep
#   1000+ employees                -> keep
TARGET_COMPANY_SIZE = 1000

# Do not print every rejected title.
# Set to True when debugging filtering behavior.
SHOW_SKIPS = False

# Search only roles relevant to your background.
TARGET_ROLE_QUERIES = [
    # -------------------------------------------------------------------------
    # Management / leadership
    # -------------------------------------------------------------------------
    "DevOps Manager",
    "DevSecOps Manager",
    "SRE Manager",
    "Site Reliability Engineering Manager",
    "Platform Engineering Manager",
    "Platform Engineering Lead",
    "Cloud Engineering Manager",
    "Cloud Infrastructure Manager",
    "Infrastructure Engineering Manager",
    "Engineering Manager DevOps",
    "Engineering Manager SRE",
    "Director DevOps",
    "Director DevSecOps",
    "Director SRE",
    "Director Platform Engineering",
    "Head of DevOps",
    "Head of DevSecOps",
    "Head of SRE",
    "Head of Platform Engineering",

    # -------------------------------------------------------------------------
    # Architecture
    # -------------------------------------------------------------------------
    "Cloud Architect",
    "Cloud Platform Architect",
    "Cloud Infrastructure Architect",
    "DevOps Architect",
    "DevSecOps Architect",
    "Platform Architect",
    "Infrastructure Architect",
    "Solutions Architect Cloud",

    # -------------------------------------------------------------------------
    # Senior / Staff / Principal
    # -------------------------------------------------------------------------
    "Senior DevOps Engineer",
    "Senior DevSecOps Engineer",
    "Senior SRE",
    "Senior Site Reliability Engineer",
    "Senior Platform Engineer",
    "Senior Cloud Engineer",
    "Staff DevOps Engineer",
    "Staff DevSecOps Engineer",
    "Staff SRE",
    "Staff Platform Engineer",
    "Staff Cloud Engineer",
    "Principal DevOps Engineer",
    "Principal DevSecOps Engineer",
    "Principal SRE",
    "Principal Platform Engineer",
    "Principal Cloud Engineer",
]


# =============================================================================
# COMPANY FILTER
# =============================================================================

# Companies you explicitly do not want.
EXCLUDED_COMPANY_PATTERNS = [
    r"\btata consultancy services\b",
    r"\btcs\b",
    r"\binfosys\b",
    r"\baccenture\b",
    r"\bwipro\b",
    r"\bhcltech\b",
    r"\bhcl technologies\b",
]


def normalize_text(value) -> str:
    """Safely normalize arbitrary text."""
    if value is None:
        return ""

    return re.sub(
        r"\s+",
        " ",
        str(value),
    ).strip().lower()


def is_excluded_company(company: str) -> bool:
    """Return True for companies explicitly excluded."""
    company = normalize_text(company)

    if not company:
        return False

    return any(
        re.search(pattern, company)
        for pattern in EXCLUDED_COMPANY_PATTERNS
    )


# =============================================================================
# TITLE FILTER
# =============================================================================

# Obvious non-target seniority/role indicators.
EXCLUDED_TITLE_PATTERNS = [
    r"\bintern\b",
    r"\binternship\b",
    r"\btrainee\b",
    r"\bfresher\b",
    r"\bjunior\b",
    r"\bentry[- ]level\b",
    r"\bgraduate\b",

    # Non-engineering management tracks.
    r"\bsales\b",
    r"\bpre[- ]sales\b",
    r"\bpresales\b",
    r"\bbusiness development\b",
    r"\bproduct owner\b",
    # r"\bproduct manager\b",
    # r"\bprogram manager\b",
    # r"\bprogramme manager\b",
    # r"\bproject manager\b",

    # Clearly different domains.
    r"\bhr\b",
    r"\bhuman resources\b",
    r"\bfinance\b",
    r"\bmarketing\b",
    r"\bpublic relations\b",
]


# IMPORTANT:
# If a title contains any of these, it is directly relevant.
#
# Example:
#   DevOps Lead
#   Senior DevOps Engineer
#   Technical Lead - DevOps
#   SRE Lead
#   Senior SRE
#   Principal Site Reliability Engineer
#   DevSecOps Architect
#
# All pass the title filter.
DIRECT_TARGET_KEYWORDS = [
    "devops",
    "devsecops",
    "sre",
    "site reliability",
    'platform',
]


# For Platform / Cloud / Infrastructure roles, require seniority or
# architecture/leadership context.
SECONDARY_DOMAIN_KEYWORDS = [
    # "platform",
    "cloud",
    "infrastructure",
]


SENIORITY_OR_ARCHITECTURE_KEYWORDS = [
    "senior",
    "staff",
    "principal",
    "lead",
    "manager",
    "director",
    "head",
    "architect",
]


# Prevent specialized application/product-cloud roles from being considered
# just because their title contains "Cloud Architect".
SPECIALIZED_CLOUD_EXCLUSIONS = [
    "salesforce",
    "genesys",
    "sap",
    # "servicenow",
    "workday",
    "dynamics",
    "crm",
    "erp",
    "snowflake",
]


def is_target_role(title: str) -> bool:
    """
    Target logic:

    1. Any DevOps / DevSecOps / SRE / Site Reliability title passes.
    2. Platform / Cloud / Infrastructure passes when accompanied by
       senior/leadership/architecture context.
    3. Junior/non-target/business/product roles are rejected.
    """

    title = normalize_text(title)

    if not title:
        return False

    # -------------------------------------------------------------------------
    # Reject obvious non-target titles first.
    # -------------------------------------------------------------------------
    for pattern in EXCLUDED_TITLE_PATTERNS:
        if re.search(pattern, title):
            return False

    # -------------------------------------------------------------------------
    # Direct target:
    # Any DevOps / DevSecOps / SRE / Site Reliability title passes.
    # -------------------------------------------------------------------------
    if any(
        keyword in title
        for keyword in DIRECT_TARGET_KEYWORDS
    ):
        return True

    # -------------------------------------------------------------------------
    # Avoid application-specific Cloud Architect roles.
    # Example:
    #   Salesforce Health Cloud Architect -> reject
    #   Genesys Cloud Architect          -> reject
    # -------------------------------------------------------------------------
    if any(
        keyword in title
        for keyword in SPECIALIZED_CLOUD_EXCLUSIONS
    ):
        return False

    # -------------------------------------------------------------------------
    # Secondary target:
    # Platform / Cloud / Infrastructure roles require seniority.
    # -------------------------------------------------------------------------
    has_secondary_domain = any(
        keyword in title
        for keyword in SECONDARY_DOMAIN_KEYWORDS
    )

    if not has_secondary_domain:
        return False

    has_seniority = any(
        keyword in title
        for keyword in SENIORITY_OR_ARCHITECTURE_KEYWORDS
    )

    return has_seniority


# =============================================================================
# JOB FIELD HELPERS
# =============================================================================

def get_job_field(job, field_names):
    """
    Return the first populated attribute from the Job object.

    Unknown values remain unknown. We do not assume salary/company size.
    """
    for field in field_names:
        value = getattr(job, field, None)

        if value is not None and str(value).strip():
            return value

    return None


# =============================================================================
# SALARY
# =============================================================================

def extract_salary_range_lpa(job):
    """
    Return (minimum_lpa, maximum_lpa).

    Examples:
        50 LPA           -> (50, 50)
        50-70 LPA        -> (50, 70)
        25-60 Lakhs      -> (25, 60)
        5000000-7000000  -> (50, 70)

    Returns None when salary is unavailable or cannot be parsed.
    """

    raw = get_job_field(
        job,
        [
            "salary",
            "salary_text",
            "salary_range",
            "ctc",
            "package",
            "salaryInfo",
        ],
    )

    if raw is None:
        return None

    text = normalize_text(raw)
    text = text.replace(",", "")

    # -------------------------------------------------------------------------
    # Range: 50-70 LPA
    # -------------------------------------------------------------------------
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*[-–—to]+\s*"
        r"(\d+(?:\.\d+)?)\s*lpa\b",
        text,
    )

    if match:
        low = float(match.group(1))
        high = float(match.group(2))
        return low, high

    # -------------------------------------------------------------------------
    # Range: 50-70 lakhs
    # -------------------------------------------------------------------------
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*[-–—to]+\s*"
        r"(\d+(?:\.\d+)?)\s*(?:lakhs?|lacs?)\b",
        text,
    )

    if match:
        low = float(match.group(1))
        high = float(match.group(2))
        return low, high

    # -------------------------------------------------------------------------
    # Single: 50 LPA
    # -------------------------------------------------------------------------
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*lpa\b",
        text,
    )

    if match:
        value = float(match.group(1))
        return value, value

    # -------------------------------------------------------------------------
    # Single: 50 Lakhs
    # -------------------------------------------------------------------------
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:lakhs?|lacs?)\b",
        text,
    )

    if match:
        value = float(match.group(1))
        return value, value

    # -------------------------------------------------------------------------
    # Raw annual salary:
    # 5000000-7000000 -> 50-70 LPA
    # -------------------------------------------------------------------------
    annual_salary_numbers = [
        float(value)
        for value in re.findall(
            r"\d+(?:\.\d+)?",
            text,
        )
        if float(value) >= 1_000_000
    ]

    if annual_salary_numbers:
        annual_salary_numbers.sort()

        return (
            annual_salary_numbers[0] / 100_000,
            annual_salary_numbers[-1] / 100_000,
        )

    return None


def salary_filter_result(job):
    """
    Return:

        known_above   -> known salary >= 50 LPA
        known_crosses -> salary range crosses 50 LPA
        known_below   -> maximum salary < 50 LPA
        unknown       -> salary not disclosed
    """

    salary_range = extract_salary_range_lpa(job)

    if salary_range is None:
        return "unknown"

    low, high = salary_range

    if high < TARGET_SALARY_LPA:
        return "known_below"

    if low >= TARGET_SALARY_LPA:
        return "known_above"

    return "known_crosses"


def format_salary(job) -> str:
    salary_range = extract_salary_range_lpa(job)

    if salary_range is None:
        return "Not disclosed"

    low, high = salary_range

    if low == high:
        return f"{low:g} LPA"

    return f"{low:g}-{high:g} LPA"


# =============================================================================
# COMPANY SIZE
# =============================================================================

def extract_company_size_range(job):
    """
    Return (minimum_employees, maximum_employees).

    Examples:

        1000             -> (1000, 1000)
        1000-5000        -> (1000, 5000)
        5001-10000       -> (5001, 10000)
        10000+           -> (10000, 10000)

    Returns None when unavailable.
    """

    raw = get_job_field(
        job,
        [
            "company_size",
            "employee_count",
            "employees",
            "company_employees",
            "company_employee_count",
            "employeeCount",
        ],
    )

    if raw is None:
        return None

    text = normalize_text(raw)
    text = text.replace(",", "")

    numbers = [
        int(value)
        for value in re.findall(
            r"\d+",
            text,
        )
    ]

    if not numbers:
        return None

    # 10000+
    if "+" in text:
        return numbers[0], numbers[0]

    # 1000-5000
    if len(numbers) >= 2:
        return (
            min(numbers[0], numbers[1]),
            max(numbers[0], numbers[1]),
        )

    return numbers[0], numbers[0]


def company_size_filter_result(job):
    """
    Return:

        known_above
        known_crosses
        known_below
        unknown
    """

    size_range = extract_company_size_range(job)

    if size_range is None:
        return "unknown"

    low, high = size_range

    if high < TARGET_COMPANY_SIZE:
        return "known_below"

    if low >= TARGET_COMPANY_SIZE:
        return "known_above"

    return "known_crosses"


def format_company_size(job) -> str:
    company_range = extract_company_size_range(job)

    if company_range is None:
        return "Unknown"

    low, high = company_range

    if low == high:
        return f"{low:,}"

    return f"{low:,}-{high:,}"


# =============================================================================
# PRIORITY
# =============================================================================

def job_priority_score(job) -> int:
    """
    Higher score = process earlier.

    This is ordering only. It does not make a job eligible.
    Eligibility is handled separately.
    """

    score = 0
    title = normalize_text(getattr(job, "title", ""))

    # -------------------------------------------------------------------------
    # Leadership / seniority
    # -------------------------------------------------------------------------
    if "head" in title:
        score += 70

    if "director" in title:
        score += 65

    if "manager" in title:
        score += 60

    if "architect" in title:
        score += 55

    if "principal" in title:
        score += 45

    if "staff" in title:
        score += 40

    if "lead" in title:
        score += 35

    if "senior" in title:
        score += 25

    # -------------------------------------------------------------------------
    # Strongest domain alignment
    # -------------------------------------------------------------------------
    if "devsecops" in title:
        score += 20

    if "devops" in title:
        score += 20

    if "sre" in title:
        score += 20

    if "site reliability" in title:
        score += 20

    if "platform" in title:
        score += 10

    if "infrastructure" in title:
        score += 10

    if "cloud" in title:
        score += 5

    # -------------------------------------------------------------------------
    # Salary
    # -------------------------------------------------------------------------
    salary_range = extract_salary_range_lpa(job)

    if salary_range is not None:
        low, high = salary_range

        if low >= 75:
            score += 50
        elif low >= 60:
            score += 40
        elif low >= 50:
            score += 30
        elif high >= 50:
            score += 15

    # -------------------------------------------------------------------------
    # Company size
    # -------------------------------------------------------------------------
    company_range = extract_company_size_range(job)

    if company_range is not None:
        low, high = company_range

        if low >= 10_000:
            score += 40
        elif low >= 5_000:
            score += 30
        elif low >= 1_000:
            score += 20
        elif high >= 1_000:
            score += 5

    return score


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":

    # -------------------------------------------------------------------------
    # 1. Credentials
    # -------------------------------------------------------------------------
    username = os.getenv("N_USERNAME")
    password = os.getenv("N_PASSWORD")

    if not username or not password:
        raise RuntimeError(
            "N_USERNAME and N_PASSWORD must be present in .env"
        )

    # -------------------------------------------------------------------------
    # 2. Login
    # -------------------------------------------------------------------------
    print(
        f"{Fore.CYAN}"
        "Logging into Naukri..."
        f"{Style.RESET_ALL}"
    )

    client = NaukriLoginClient(
        username,
        password,
    )

    client.login()

    hirist = HiristClient(
        username,
        password,
    )

    print(
        f"{Fore.GREEN}"
        "Naukri login successful"
        f"{Style.RESET_ALL}"
    )

    # -------------------------------------------------------------------------
    # 3. Resume upload
    # -------------------------------------------------------------------------
    print(
        f"{Fore.CYAN}"
        f"Uploading resume: {RESUME_FILE}"
        f"{Style.RESET_ALL}"
    )

    print(
        client.update_resume(
            RESUME_FILE
        )
    )

    # -------------------------------------------------------------------------
    # 4. Profile update
    # -------------------------------------------------------------------------
    print(
        f"{Fore.CYAN}"
        "Updating profile headline..."
        f"{Style.RESET_ALL}"
    )

    print(
        client.update_profile(
            headline=(
                "DevSecOps Manager & Platform / SRE Lead | "
                "Helping enterprises solve cloud cost, security, reliability "
                "and delivery bottlenecks | 2x AWS Certified | CKA | "
                "ex-KPMG, Infosys, Ericsson."
            )
        )
    )

    print(
        f"{Fore.CYAN}"
        "Updating profile summary..."
        f"{Style.RESET_ALL}"
    )

    print(
        client.update_profile(
            summary=(
                "CKA and AWS Certified Senior DevOps, SRE, and Platform "
                "Engineering leader with 8+ years owning CI/CD platforms "
                "and large scale cloud reliability across healthcare, "
                "banking, and telecommunications. Administers Jenkins, "
                "JFrog Artifactory and XRay. Builds automation and "
                "Developer Portal plugins (React, TypeScript) and leads "
                "SRE/DevOps engineers through Scrum-based operations, "
                "incident and change governance, stakeholder alignment, "
                "SLO ownership, on-call incident command, and "
                "cross-functional delivery. Operates cloud platforms on "
                "AWS, Azure, and GCP spanning Kubernetes, Terraform, "
                "Vault/CyberArk secrets, DevSecOps, SRE, FinOps, and "
                "LLM tooling including MCP and RAG. Delivered 75% "
                "infrastructure cost reduction, 142% increase in "
                "deployment frequency, and 92% lower MTTR. Supported "
                "HIPAA/HITRUST and ONC certification through audit "
                "remediation and penetration-test finding closure."
            )
        )
    )

    # -------------------------------------------------------------------------
    # 5. Job client
    # -------------------------------------------------------------------------
    jc = NaukriJobClient(client)

    print()
    print(
        f"{Fore.CYAN}"
        "Searching targeted senior roles..."
        f"{Style.RESET_ALL}"
    )

    print(
        f"{Fore.WHITE}"
        f"Salary target       : {TARGET_SALARY_LPA}+ LPA"
        f"{Style.RESET_ALL}"
    )

    print(
        f"{Fore.WHITE}"
        f"Company-size target : {TARGET_COMPANY_SIZE}+ employees"
        f"{Style.RESET_ALL}"
    )

    print(
        f"{Fore.WHITE}"
        f"Experience          : {MIN_EXPERIENCE}+ years"
        f"{Style.RESET_ALL}"
    )

    print(
        f"{Fore.WHITE}"
        f"Job age             : {JOB_AGE_DAYS} days"
        f"{Style.RESET_ALL}"
    )

    print(
        f"{Fore.WHITE}"
        f"Maximum applications: {MAX_APPLICATIONS}"
        f"{Style.RESET_ALL}"
    )

    # -------------------------------------------------------------------------
    # 6. Search
    # -------------------------------------------------------------------------
    seen_ids = set()
    combined = []

    total_seen = 0
    skipped_duplicate = 0
    skipped_title = 0
    skipped_salary = 0
    skipped_company = 0

    for keyword in TARGET_ROLE_QUERIES:

        try:
            print(
                f"{Fore.CYAN}"
                f"Searching: {keyword}"
                f"{Style.RESET_ALL}"
            )

            found = jc.search_jobs(
                keyword=keyword,
                experience=MIN_EXPERIENCE,
                page=1,
                job_age=JOB_AGE_DAYS,
            )

            query_seen = 0
            query_kept = 0

            for job in found:

                total_seen += 1
                query_seen += 1

                # -------------------------------------------------------------
                # Job ID
                # -------------------------------------------------------------
                if not job.job_id:
                    continue

                if job.job_id in seen_ids:
                    skipped_duplicate += 1
                    continue

                # -------------------------------------------------------------
                # Company exclusion
                # -------------------------------------------------------------
                if is_excluded_company(job.company):
                    skipped_company += 1

                    if SHOW_SKIPS:
                        print(
                            f"{Fore.YELLOW}"
                            f"  Skip company: {job.company}"
                            f"{Style.RESET_ALL}"
                        )

                    continue

                # -------------------------------------------------------------
                # Title
                # -------------------------------------------------------------
                if not is_target_role(job.title):
                    skipped_title += 1

                    if SHOW_SKIPS:
                        print(
                            f"{Fore.YELLOW}"
                            f"  Skip title: {job.title}"
                            f"{Style.RESET_ALL}"
                        )

                    continue

                # -------------------------------------------------------------
                # Salary
                # -------------------------------------------------------------
                salary_status = salary_filter_result(job)

                if salary_status == "known_below":
                    skipped_salary += 1

                    if SHOW_SKIPS:
                        print(
                            f"{Fore.YELLOW}"
                            f"  Skip salary: {job.title} | "
                            f"{format_salary(job)}"
                            f"{Style.RESET_ALL}"
                        )

                    continue

                # -------------------------------------------------------------
                # Company size
                # -------------------------------------------------------------
                company_status = company_size_filter_result(job)

                if company_status == "known_below":
                    skipped_company += 1

                    if SHOW_SKIPS:
                        print(
                            f"{Fore.YELLOW}"
                            f"  Skip company size: {job.title} | "
                            f"{format_company_size(job)} employees"
                            f"{Style.RESET_ALL}"
                        )

                    continue

                # -------------------------------------------------------------
                # Accepted
                # -------------------------------------------------------------
                seen_ids.add(job.job_id)
                combined.append(job)
                query_kept += 1

            print(
                f"{Fore.WHITE}"
                f"  Results: {query_seen} | "
                f"Accepted: {query_kept}"
                f"{Style.RESET_ALL}"
            )

            time.sleep(1.0)

        except Exception as e:
            print(
                f"{Fore.RED}"
                f"Search failed for {keyword}: {e}"
                f"{Style.RESET_ALL}"
            )

    # -------------------------------------------------------------------------
    # 7. Rank
    # -------------------------------------------------------------------------
    combined.sort(
        key=job_priority_score,
        reverse=True,
    )

    jobs = combined

    print()
    print(
        f"{Fore.CYAN}"
        f"{'=' * 70}"
        f"{Style.RESET_ALL}"
    )

    print(
        f"{Fore.GREEN}"
        f"Matching jobs: {len(jobs)}"
        f"{Style.RESET_ALL}"
    )

    print(
        f"{Fore.WHITE}"
        f"Total search results : {total_seen}"
    )

    print(
        f"{Fore.WHITE}"
        f"Skipped duplicates   : {skipped_duplicate}"
    )

    print(
        f"{Fore.WHITE}"
        f"Skipped titles       : {skipped_title}"
    )

    print(
        f"{Fore.WHITE}"
        f"Skipped salary <50   : {skipped_salary}"
    )

    print(
        f"{Fore.WHITE}"
        f"Skipped companies    : {skipped_company}"
    )

    print(
        f"{Fore.CYAN}"
        f"{'=' * 70}"
        f"{Style.RESET_ALL}"
    )

    if not jobs:
        print(
            f"{Fore.YELLOW}"
            "No jobs matched the target criteria."
            f"{Style.RESET_ALL}"
        )
        raise SystemExit(0)

    # -------------------------------------------------------------------------
    # 8. Application configuration
    # -------------------------------------------------------------------------
    applications_done = 0

    mandatory = [
        "DevOps",
        "Kubernetes",
    ]

    optional = [
        "AWS",
        "Terraform",
        "SRE",
        "CI/CD",
    ]

    # -------------------------------------------------------------------------
    # 9. Apply
    # -------------------------------------------------------------------------
    for job in jobs:

        if applications_done >= MAX_APPLICATIONS:
            print()
            print(
                f"{Fore.YELLOW}"
                f"Reached application limit: {MAX_APPLICATIONS}"
                f"{Style.RESET_ALL}"
            )
            break

        salary = format_salary(job)
        company_size = format_company_size(job)
        priority = job_priority_score(job)

        print()
        print(
            f"{Fore.CYAN}"
            f"{'─' * 70}"
            f"{Style.RESET_ALL}"
        )

        print(
            f"{Fore.WHITE}"
            f"  Title     : {Fore.YELLOW}{job.title}"
        )

        print(
            f"{Fore.WHITE}"
            f"  Company   : {Fore.YELLOW}{job.company}"
        )

        print(
            f"{Fore.WHITE}"
            f"  Job ID    : {Fore.YELLOW}{job.job_id}"
        )

        print(
            f"{Fore.WHITE}"
            f"  Salary    : {Fore.YELLOW}{salary}"
        )

        print(
            f"{Fore.WHITE}"
            f"  Employees : {Fore.YELLOW}{company_size}"
        )

        print(
            f"{Fore.WHITE}"
            f"  Priority  : {Fore.YELLOW}{priority}"
        )

        print(
            f"{Fore.WHITE}"
            f"  Tags      : {Fore.YELLOW}{job.tags}"
        )

        try:

            # -----------------------------------------------------------------
            # Check external application route
            # -----------------------------------------------------------------
            external_info = jc.get_external_apply_info(
                job.job_id
            )

            # -----------------------------------------------------------------
            # Hirist
            # -----------------------------------------------------------------
            if (
                external_info.get("is_hirist")
                and external_info.get("hirist_url")
            ):
                hirist.apply_from_url(
                    external_info["hirist_url"]
                )

                applications_done += 1

                print(
                    f"{Fore.GREEN}"
                    f"  Applied via Hirist: "
                    f"{external_info['hirist_url']}"
                    f"{Style.RESET_ALL}"
                )

                time.sleep(3)
                continue

            # -----------------------------------------------------------------
            # Other external application
            # -----------------------------------------------------------------
            if external_info.get("external"):
                print(
                    f"{Fore.YELLOW}"
                    "  Skipped — external company apply"
                    f"{Style.RESET_ALL}"
                )

                time.sleep(2)
                continue

            # -----------------------------------------------------------------
            # Naukri application
            # -----------------------------------------------------------------
            result = jc.apply_job(
                job,
                mandatory_skills=mandatory,
                optional_skills=optional,
                source="search",
            )

            # -----------------------------------------------------------------
            # Application redirected to Hirist
            # -----------------------------------------------------------------
            hirist_url = find_hirist_url(result)

            if hirist_url:
                hirist.apply_from_url(
                    hirist_url
                )

                applications_done += 1

                print(
                    f"{Fore.GREEN}"
                    f"  Applied via Hirist: "
                    f"{hirist_url}"
                    f"{Style.RESET_ALL}"
                )

                time.sleep(3)
                continue

            # -----------------------------------------------------------------
            # Questionnaire
            # -----------------------------------------------------------------
            job_result = (
                result.get("jobs") or [{}]
            )[0]

            if job_result.get("questionnaire"):

                print(
                    f"{Fore.YELLOW}"
                    "  Questionnaire detected — "
                    "answering automatically"
                    f"{Style.RESET_ALL}"
                )

                sid = (
                    datetime.now(timezone.utc)
                    .strftime("%Y%m%d%H%M%S")
                    + "0000000"
                )

                questionnaire_result = (
                    jc.handle_static_questionnaire_and_apply(
                        job,
                        questionnaire=job_result["questionnaire"],
                        sid=sid,
                        mandatory_skills=mandatory,
                        optional_skills=optional,
                        source="search",
                    )
                )

                if questionnaire_result.get("success") is False:
                    print(
                        f"{Fore.RED}"
                        "  Questionnaire/application failed: "
                        f"{questionnaire_result.get('error')}"
                        f"{Style.RESET_ALL}"
                    )

                    time.sleep(3)
                    continue

            # -----------------------------------------------------------------
            # Success
            # -----------------------------------------------------------------
            applications_done += 1

            print(
                f"{Fore.GREEN}"
                f"  Applied successfully!"
                f" ({applications_done}/{MAX_APPLICATIONS})"
                f"{Style.RESET_ALL}"
            )

        except HiristError as e:

            print(
                f"{Fore.RED}"
                f"  Hirist failed: {e}"
                f"{Style.RESET_ALL}"
            )

        except Exception as e:

            print(
                f"{Fore.RED}"
                f"  Failed: {e}"
                f"{Style.RESET_ALL}"
            )

        time.sleep(3)

    # -------------------------------------------------------------------------
    # 10. Final summary
    # -------------------------------------------------------------------------
    print()
    print(
        f"{Fore.CYAN}"
        f"{'=' * 70}"
        f"{Style.RESET_ALL}"
    )

    print(
        f"{Fore.GREEN}"
        f"Applications completed: {applications_done}"
        f"{Style.RESET_ALL}"
    )

    print(
        f"{Fore.WHITE}"
        f"Matching jobs found : {len(jobs)}"
        f"{Style.RESET_ALL}"
    )

    print(
        f"{Fore.WHITE}"
        f"Application limit   : {MAX_APPLICATIONS}"
        f"{Style.RESET_ALL}"
    )

    print(
        f"{Fore.CYAN}"
        f"{'=' * 70}"
        f"{Style.RESET_ALL}"
    )

