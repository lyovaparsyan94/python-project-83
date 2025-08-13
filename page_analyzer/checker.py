import re
import requests


class CheckerError(Exception):
    pass


TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
DESC_RE = re.compile(
    r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']',
    re.IGNORECASE,
)


def check_url(url: str):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as err:
        raise CheckerError from err

    html = resp.text
    status_code = resp.status_code

    h1_match = H1_RE.search(html)
    h1 = h1_match.group(1).strip() if h1_match else ""

    title_matches = TITLE_RE.findall(html)
    title = title_matches[-1].strip() if title_matches else ""

    desc_match = DESC_RE.search(html)
    description = desc_match.group(1).strip() if desc_match else ""

    return status_code, h1, title, description
