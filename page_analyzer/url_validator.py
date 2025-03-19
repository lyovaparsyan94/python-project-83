from urllib.parse import urlparse


def normalize_url(url):
    p = urlparse(url)
    result = p.scheme + '://' + p.hostname
    return result


def validate_url(url):
    errors = []
    if not validators.url(url) or len(url) > 255:
        errors.append(('Некорректный URL', 'danger'))
    return errors