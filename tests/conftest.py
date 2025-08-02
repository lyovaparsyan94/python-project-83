import os
import pytest
from page_analyzer.app import app as flask_app
from page_analyzer.db import get_connection
from page_analyzer.db import add_url

@pytest.fixture
def app():
    app = flask_app
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = "test_secret_key"
    return app

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        pytest.skip("DATABASE_URL not set, skipping database setup")
        return

    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        with open('database.sql', 'r') as f:
            sql_script = f.read()
            
            commands = sql_script.split(';')
            for command in commands:
                if command.strip():
                    cur.execute(command)
        
        conn.commit()
    except Exception as e:
        pytest.fail(f"Database setup failed: {str(e)}")
    finally:
        if conn:
            conn.close()

@pytest.fixture
def client(app):
    return app.test_client()

def test_url(app):
    with app.app_context():
        url_id = add_url("https://example.com")
        return url_id
