import os
import requests

from dotenv import load_dotenv
from flask import Flask, render_template, request

from page_analyzer.parser import get_data
from page_analyzer.url_validator import normalize_url

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


# conn = psycopg2.connect(DATABASE_URL)


@app.route('/')
def index():
    return render_template(
        'index.html',
    )


@app.route('/urls/', methods=['POST'])
def urls_index():
    user_url = request.form.to_dict()['url']
    url = normalize_url(user_url)
    url_response = requests.get(url)
    url_response.raise_for_status()
    url_data = get_data(url_response)
    return render_template(
        'url.html',
        url=url,
        url_data=url_data
    )
