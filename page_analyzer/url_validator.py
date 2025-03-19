from urllib.parse import urlparse

import validators


def normalize_url(url: str) -> str:
    '''
    :param url:
    :return: normalized URL including only the scheme and host.
    example: normalize_url("https://ru.hexlet.io/projects/83/members/44838")
    will return "https://ru.hexlet.io"
    '''
    p = urlparse(url)
    result = p.scheme + '://' + p.hostname
    return result


def validate_url(url):
    errors = {}

    if not validators.url(url):
        errors['url'] = 'Некорректный формат URL'
    if url == "":
        errors['url'] = 'URL не может быть пустым'
    if len(url) > 255:
        errors['url'] = 'Слишком длинный URL (должен быть короче 255 символов)'

    return errors