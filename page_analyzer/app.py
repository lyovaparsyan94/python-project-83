import os

import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from page_analyzer.data_base import UrlRepository
from page_analyzer.parser import get_data
from page_analyzer.url_validator import normalize_url, validate_url

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


@app.route('/')
def index():
    return render_template(
        'index.html',
    )


@app.route('/urls', methods=['POST'])
def urls_index():
    url = request.form.to_dict()
    errors = validate_url(url['url'])

    if errors:
        flash('Некорректный URL', 'danger')
        return render_template(
            'index.html',
        ), 422

    normalized_url = normalize_url(url['url'])
    repo = UrlRepository(DATABASE_URL)
    url_info = repo.find_url(normalized_url)
    if url_info is not None:
        flash('Страница уже существует', 'warning')
        return redirect(url_for('get_url', id=url_info.get('id')))
    id = repo.add_url(normalized_url)
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('get_url', id=id))


@app.route('/urls/<int:id>')
def get_url(id):
    repo = UrlRepository(DATABASE_URL)
    url_info = repo.find_id(id)

    if not url_info:
        abort(404)

    return render_template(
        'url.html',
        url_info=url_info,
    )


@app.route('/urls/<int:id>/checks', methods=['POST'])
def get_url_data(id):
    repo = UrlRepository(DATABASE_URL)
    url_info = repo.find_id(id)

    try:
        response = requests.get(url_info.get('name'), timeout=0.3)
        response.raise_for_status()
    except requests.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('get_url', id=id))

    status = response.status_code
    data = get_data(response)
    data['status'] = status
    repo.add_url_check(data, url_info)
    flash('Страница успешно проверена', 'success')
    url_checks = repo.get_url_checks(id)
    return render_template(
        'url.html',
        url_info=url_info,
        url_checks=url_checks,
    )


@app.route('/urls', methods=['GET'])
def get_urls():
    repo = UrlRepository(DATABASE_URL)
    all_urls_checks = repo.get_all_urls_checks()
    return render_template(
        'urls.html',
        all_urls_checks=all_urls_checks,
    )


@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500