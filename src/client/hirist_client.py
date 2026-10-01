import logging
import re
from typing import Optional
from urllib.parse import urlencode

import requests

logger = logging.getLogger(__name__)

HIRIST_LOGIN_URL = "https://gladiator.hirist.tech/user/login"
HIRIST_APPLY_URL = "https://user-api.hirist.com/v2/apply"
HIRIST_HOST_MARKERS = ("hirist.tech", "hirist.com")


class HiristError(Exception):
    """Hirist login/apply failures."""


def is_hirist_url(url: str | None) -> bool:
    if not url:
        return False
    lowered = url.lower()
    return any(marker in lowered for marker in HIRIST_HOST_MARKERS)


def extract_hirist_job_id(url: str) -> Optional[str]:
    """Extract Hirist jobcode from common URL shapes."""
    if not url:
        return None

    patterns = [
        r"/j/[^/?#]*-(\d+)(?:[/?#]|$)",
        r"[?&]jobcode=(\d+)",
        r"/job/(\d+)(?:[/?#]|$)",
        r"/jobs?/(\d+)(?:[/?#]|$)",
        r"-(\d{5,})(?:[/?#]|$)",
    ]
    for pattern in patterns:
        match = re.search(pattern, url, re.I)
        if match:
            return match.group(1)
    return None


def find_hirist_url(payload) -> Optional[str]:
    """Recursively find the first Hirist URL inside a nested API payload."""
    if isinstance(payload, str):
        if is_hirist_url(payload):
            return payload
        return None

    if isinstance(payload, dict):
        preferred_keys = (
            "companyApplyUrl",
            "applyRedirectUrl",
            "redirectUrl",
            "redirectionUrl",
            "applyUrl",
            "companyUrl",
            "jdURL",
            "url",
            "link",
        )
        for key in preferred_keys:
            value = payload.get(key)
            found = find_hirist_url(value)
            if found:
                return found
        for value in payload.values():
            found = find_hirist_url(value)
            if found:
                return found
        return None

    if isinstance(payload, list):
        for item in payload:
            found = find_hirist_url(item)
            if found:
                return found

    return None


class HiristClient:
    """Minimal Hirist jobseeker client: password login + apply by jobcode."""

    def __init__(self, email: str, password: str):
        if not email or not password:
            raise HiristError("Hirist email/password missing")
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.token: Optional[str] = None
        self._logged_in = False

    def _headers(self, auth: bool = False) -> dict:
        headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://www.hirist.tech",
            "referer": "https://www.hirist.tech/login",
            "user-agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            "x-url": "https://www.hirist.tech/login",
            "x-referer": "https://www.hirist.tech/",
            "x-href": "https://www.hirist.tech/login",
        }
        if auth and self.token:
            headers["authorization"] = f"Bearer {self.token}"
            headers["content-type"] = "application/json"
        return headers

    def _extract_token(self, payload) -> Optional[str]:
        if not isinstance(payload, dict):
            return None
        for key in ("token", "accessToken", "authToken", "jwt"):
            value = payload.get(key)
            if isinstance(value, str) and value:
                return value
        data = payload.get("data")
        if isinstance(data, dict):
            return self._extract_token(data)
        user = payload.get("user")
        if isinstance(user, dict):
            return self._extract_token(user)
        return None

    def login(self) -> dict:
        body = urlencode(
            {
                "email": self.email,
                "password": self.password,
                "recaptchaToken": "",
            }
        )
        res = self.session.post(
            HIRIST_LOGIN_URL,
            headers=self._headers(auth=False),
            data=body,
            timeout=30,
        )

        try:
            payload = res.json()
        except Exception:
            payload = {"raw": res.text}

        if not res.ok:
            message = (
                payload.get("error", {}).get("message")
                if isinstance(payload.get("error"), dict)
                else payload.get("message") or res.text
            )
            raise HiristError(f"Hirist login failed ({res.status_code}): {message}")

        self.token = self._extract_token(payload)
        if not self.token:
            # Some responses only set auth cookies; allow cookie-only session.
            cookies = self.session.cookies.get_dict()
            if not cookies:
                raise HiristError("Hirist login succeeded but no token/cookies returned")

        self._logged_in = True
        logger.info("Hirist login successful for %s", self.email)
        return payload if isinstance(payload, dict) else {"ok": True}

    def ensure_login(self) -> None:
        if not self._logged_in:
            self.login()

    def apply_by_jobcode(self, jobcode: str, extra: dict | None = None) -> dict:
        self.ensure_login()
        if not jobcode:
            raise HiristError("Missing Hirist jobcode")

        url = f"{HIRIST_APPLY_URL}?jobcode={jobcode}"
        headers = self._headers(auth=True)
        payload = extra or {}
        res = self.session.post(url, headers=headers, json=payload, timeout=30)

        try:
            data = res.json()
        except Exception:
            data = {"raw": res.text}

        if not res.ok:
            raise HiristError(f"Hirist apply failed ({res.status_code}): {data}")

        return data if isinstance(data, dict) else {"ok": True, "data": data}

    def apply_from_url(self, url: str) -> dict:
        if not is_hirist_url(url):
            raise HiristError(f"Not a Hirist URL: {url}")
        jobcode = extract_hirist_job_id(url)
        if not jobcode:
            raise HiristError(f"Could not extract Hirist jobcode from URL: {url}")
        result = self.apply_by_jobcode(jobcode)
        result["hirist_url"] = url
        result["hirist_jobcode"] = jobcode
        return result
