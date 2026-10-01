import re

STATIC_JS_BASE = "https://static.naukimg.com/s/5/105/j/"

APP_JS_RE = re.compile(
    r'src="((?:https?:)?//static\.naukimg\.com/s/5/105/j/app_v\d+\.min\.js)"'
)

MNJ_VERSION_RE = re.compile(
    r'\bmnj\s*:\s*"(_v\d+)"'
)

MNJ_FALLBACK_VERSIONS = (
    "_v323",
    "_v299",
)


def app_js_url(profile_html: str) -> str | None:
    match = APP_JS_RE.search(profile_html)

    if not match:
        return None

    url = match.group(1)

    if url.startswith("//"):
        return "https:" + url

    return url


def mnj_version_from_app_js(app_js: str) -> str | None:
    match = MNJ_VERSION_RE.search(app_js)
    return match.group(1) if match else None


def mnj_url(version: str) -> str:
    return f"{STATIC_JS_BASE}mnj{version}.min.js"


def candidate_mnj_urls(profile_html: str, fetch_text):
    urls = []

    app_url = app_js_url(profile_html)

    if app_url:
        try:
            version = mnj_version_from_app_js(
                fetch_text(app_url)
            )

            if version:
                urls.append(mnj_url(version))

        except Exception:
            pass

    for version in MNJ_FALLBACK_VERSIONS:
        url = mnj_url(version)

        if url not in urls:
            urls.append(url)

    return urls