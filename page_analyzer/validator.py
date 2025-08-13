from urllib.parse import urlparse
from validators import url as validate_url


def is_valid_url(url_input):
    return url_input and validate_url(url_input) and len(url_input) <= 255


def normalize_url(url_input):
    parsed = urlparse(url_input)
    return f"{parsed.scheme}://{parsed.netloc}"
