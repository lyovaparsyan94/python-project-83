import os
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    url_for,
)
from validators import url as validate

from .ceo_analysis import get_ceo
from .checks_repo import CheckRepository
from .urls_repo import SiteRepository

# Attempt to load .env
# In Hexlet's environment, the .env file is typically at /project/code/.env
# The WORKDIR in Dockerfile is /project.
# The application code is expected to be in /project/code/page_analyzer/
dotenv_path = "/project/code/.env"  # Absolute path in the container
load_dotenv(dotenv_path=dotenv_path, override=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

# Ensure db_url passed to repositories is not None
if app.config.get('DATABASE_URL') is None:
    # This will cause Gunicorn to fail loading the app, which is informative
    raise ValueError("DATABASE_URL is None in app.config before initializing repositories. "  # noqa
                     "Halting application startup.")

url_repo = SiteRepository(app.config['DATABASE_URL'])
check_repo = CheckRepository(app.config['DATABASE_URL'])


def normalize_root(url: str) -> str:
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    return f"{scheme}://{netloc}"


@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template('main.html', messages=messages, url='')


@app.route('/urls', methods=['POST'])
def urls_post():
    user_data = request.form.to_dict()
    urls = url_repo.get_content()

    urls_names = []
    for url in urls:
        urls_names.append(url['name'])

    is_valid = validate(user_data['url'])
    if is_valid is not True:
        flash('Некорректный URL', 'alert-danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            'main.html',
            messages=messages,
            url=user_data['url'],

        ), 422

    if len(user_data['url']) > 255:
        flash('URL превышает 255 символов', 'alert-danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            'main.html',
            messages=messages,
            url=user_data['url'],
        ), 422

    user_data['url'] = normalize_root(user_data['url'])
    if user_data['url'] in urls_names:
        flash('Страница уже существует', 'alert-info')
        id = url_repo.find_by_name(user_data['url'])['id']
        return redirect(url_for('urls_show', id=id), code=302)

    id = url_repo.save(user_data)
    flash('Страница успешно добавлена', 'alert-success')
    return redirect(url_for('urls_show', id=id), code=302)


@app.route('/urls')
def urls_get():
    urls = url_repo.get_content()
    urls_with_last_check = []
    for url in urls:
        url_with_last_check = url
        last_check = check_repo.get_last_check_date_by_id(url["id"])
        last_status_code = check_repo.get_last_status_code_by_id(url["id"])
        url_with_last_check["last_check"] = last_check
        url_with_last_check["status_code"] = last_status_code
        urls_with_last_check.append(url_with_last_check)
    return render_template(
        'urls.html',
        urls=urls_with_last_check
    )


@app.route('/urls/<id>')
def urls_show(id):
    url = url_repo.find(id)
    template = 'url.html' if url else 'incorrect_id.html'
    messages = get_flashed_messages(with_categories=True)
    checks = check_repo.get_content_by_url_id(id)
    return render_template(
        template,
        url=url,
        messages=messages,
        checks=checks
    )


@app.route('/urls/<id>/checks', methods=['POST'])
def create_check(id):
    url_row = url_repo.find(id)
    url = url_row['name']
    try:
        r = requests.get(url, timeout=10)
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'alert-danger')
        return redirect(url_for('urls_show', id=id))

    status_code = r.status_code
    if str(status_code)[0] in ('4', '5'):
        flash('Произошла ошибка при проверке', 'alert-danger')
        return redirect(url_for('urls_show', id=id))

    h1, title, desc = get_ceo(r.text)

    check_repo.save(id, status_code, h1, title, desc)
    flash('Страница успешно проверена', 'alert-success')
    return redirect(url_for('urls_show', id=id))
