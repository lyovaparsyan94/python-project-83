import os
import datetime
import requests
from flask import (
    Flask, render_template, request, 
    redirect, url_for, flash, get_flashed_messages
)
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from .db import (
    add_url, get_url_by_id, get_url_by_name,
    get_all_urls, add_url_check, get_url_checks,
    is_valid_url, normalize_url
)

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

@app.context_processor
def inject_current_year():
    return {'current_year': datetime.datetime.now().year}

@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    app.logger.debug(f"Flash messages on index: {messages}")
    return render_template('index.html', messages=messages)

@app.route('/urls', methods=['POST'])
def add_url_handler():
    url = request.form.get('url')
    
    if not is_valid_url(url):
        flash('Некорректный URL', 'danger')
        return render_template('index.html', url=url), 422
    
    normalized_url = normalize_url(url)
    existing_url = get_url_by_name(normalized_url)
    
    if existing_url:
        flash('Страница уже существует', 'info')
        return redirect(url_for('show_url', id=existing_url['id']))
    
    try:
        url_id = add_url(normalized_url)
        flash('Страница успешно добавлена', 'success')
        return redirect(url_for('show_url', id=url_id))
    except Exception as e:
        app.logger.error(f"Database error: {str(e)}")
        flash('Ошибка при добавлении страницы', 'danger')
        return redirect(url_for('index'))

@app.route('/urls')
def list_urls():
    urls = get_all_urls()
    return render_template('urls/index.html', urls=urls)

@app.route('/urls/<int:id>')
def show_url(id):
    url = get_url_by_id(id)
    if not url:
        flash('Страница не найдена', 'danger')
        return redirect(url_for('index'))
    
    checks = get_url_checks(id)
    messages = get_flashed_messages(with_categories=True)
    return render_template('urls/show.html', url=url, checks=checks, messages=messages)

@app.post('/urls/<int:id>/checks')
def check_url(id):
    url_data = get_url_by_id(id)
    if not url_data:
        flash('Страница не найдена', 'danger')
        return redirect(url_for('index'))
    
    url_name = url_data['name']
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        response = requests.get(
            url_name,
            headers=headers,
            timeout=10,
            allow_redirects=True
        )
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        h1_tag = soup.find('h1')
        h1 = h1_tag.text.strip() if h1_tag else None
        
        title_tag = soup.find('title')
        title = title_tag.text.strip() if title_tag else None
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc['content'].strip() if meta_desc and meta_desc.get('content') else None
        
        if description and len(description) > 255:
            description = description[:252] + '...'
        
        add_url_check(id, response.status_code, h1, title, description)
        flash('Страница успешно проверена', 'success')
        
    except requests.exceptions.RequestException as e:
        if isinstance(e, requests.exceptions.Timeout):
            error_msg = 'Таймаут при проверке сайта'
        elif isinstance(e, requests.exceptions.TooManyRedirects):
            error_msg = 'Слишком много перенаправлений'
        elif isinstance(e, requests.exceptions.SSLError):
            error_msg = 'Ошибка SSL сертификата'
        else:
            error_msg = f'Ошибка при проверке: {str(e)}'
        
        flash(error_msg, 'danger')
    
    except Exception as e:
        flash(f'Неизвестная ошибка: {str(e)}', 'danger')
    
    return redirect(url_for('show_url', id=id))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)