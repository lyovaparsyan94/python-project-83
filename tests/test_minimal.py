def test_app_import():
    from page_analyzer.app import app
    assert app is not None

def test_db_import():
    from page_analyzer.db import get_connection
    conn = get_connection()
    assert conn is not None
    conn.close()