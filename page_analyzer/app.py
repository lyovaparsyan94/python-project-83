import os
from dotenv import load_dotenv

# Attempt to load .env
# In Hexlet's environment, the .env file is typically at /project/code/.env
# The WORKDIR in Dockerfile is /project.
# The application code is expected to be in /project/code/page_analyzer/
dotenv_path = "/project/code/.env" # Absolute path in the container
print(f"DEBUG app.py: Attempting to load .env from: {dotenv_path}")
found_dotenv = load_dotenv(dotenv_path=dotenv_path, override=True)
print(f"DEBUG app.py: load_dotenv found_dotenv = {found_dotenv}") # Should be True if file was found

# Print key environment variables immediately after load_dotenv
DATABASE_URL_FROM_ENV = os.getenv('DATABASE_URL')
SECRET_KEY_FROM_ENV = os.getenv('SECRET_KEY')
print(f"DEBUG app.py: After load_dotenv: DATABASE_URL='{DATABASE_URL_FROM_ENV}', SECRET_KEY='{SECRET_KEY_FROM_ENV}'")

from urllib.parse import urlparse # Imports after load_dotenv
import requests
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

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY_FROM_ENV
app.config['DATABASE_URL'] = DATABASE_URL_FROM_ENV

if not app.config['DATABASE_URL']:
    print("CRITICAL ERROR from app.py: DATABASE_URL is not set in app.config after os.getenv!")
elif 'db:5432' not in app.config['DATABASE_URL'] and app.config['DATABASE_URL'] is not None: # Check if not None before string operation
    print(f"WARNING from app.py: DATABASE_URL ('{app.config['DATABASE_URL']}') does not look like it's pointing to the 'db' service on port 5432.")

print(f"DEBUG app.py: Final app.config: DATABASE_URL='{app.config.get('DATABASE_URL')}', SECRET_KEY='{app.config.get('SECRET_KEY')}'")

# Ensure db_url passed to repositories is not None
if app.config.get('DATABASE_URL') is None: # Use .get() for safety
    # This will cause Gunicorn to fail loading the app, which is informative
    raise ValueError("DATABASE_URL is None in app.config before initializing repositories. Halting application startup.")

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