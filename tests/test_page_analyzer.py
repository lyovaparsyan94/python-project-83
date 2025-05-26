import pytest
import psycopg2
from page_analyzer.app import app

blobfish_url = 'https://ru.wikipedia.org/wiki/Psychrolutes_marcidus'
invalid_url = 'kjdho72417ojef'

@pytest.fixture
def setup_db():
    conn = psycopg2.connect(app.config['DATABASE_URL'])
    with conn.cursor() as cur:
        with open('database.sql', 'r') as f:
            cur.execute(f.read())
        conn.commit()
        yield
    with conn.cursor() as cur:
        cur.execute('TRUNCATE TABLE url_checks CASCADE')
        cur.execute('TRUNCATE TABLE urls CASCADE')
        conn.commit()
        conn.close()

@pytest.fixture
def client():
    app.config['TESTING'] = True
    return app.test_client()

def test_main_page(client):
    response = client.get('/')
    assert response.status_code == 200

def test_urls_post_invalid(client, setup_db):
    response = client.post('/urls', data={'url': invalid_url})
    assert response.status_code == 422

def test_urls_post_valid(client, setup_db):
    response = client.post('/urls', data={'url': blobfish_url})
    assert response.status_code == 302



