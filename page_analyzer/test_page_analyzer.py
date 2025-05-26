import pytest
import psycopg2
import os
from .app import app

blobfish_url = 'https://ru.wikipedia.org/wiki/Psychrolutes_marcidus'
invalid_url = 'kjdho72417ojef'

@pytest.fixture
def setup_db():
    print(f"DEBUG in setup_db (new location): DATABASE_URL from app.config = {app.config.get('DATABASE_URL')}")
    conn = psycopg2.connect(app.config['DATABASE_URL'])
    with conn.cursor() as cur:
        db_sql_path = os.path.join(os.path.dirname(__file__), '../database.sql')
        print(f"DEBUG in setup_db (new location): Attempting to open {db_sql_path}")
        with open(db_sql_path, 'r') as f:
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