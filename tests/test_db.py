import pytest
from page_analyzer.db import (
    get_connection, 
    normalize_url, 
    is_valid_url, 
    add_url, 
    get_url_by_id, 
    get_url_by_name, 
    add_url_check, 
    get_url_checks
)

@pytest.fixture(autouse=True)
def clean_db():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM url_checks")
            cur.execute("DELETE FROM urls")
            conn.commit()
    finally:
        conn.close()
    yield

def test_add_url(clean_db):
    url = "https://example.com"
    url_id = add_url(url)
    assert url_id is not None
    
    url_from_db = get_url_by_id(url_id)
    assert url_from_db["name"] == normalize_url(url)
    
    same_url = get_url_by_name(url)
    assert same_url["id"] == url_id

def test_add_existing_url(clean_db):
    url = "https://example.com"
    first_id = add_url(url)
    second_id = add_url(url)
    
    assert first_id is not None
    assert second_id == first_id

def test_add_url_check(clean_db):
    url = "https://example.com"
    url_id = add_url(url)
    assert url_id is not None
    
    check_id = add_url_check(url_id, 200, "Test Title", "Test H1", "Test Description")
    assert check_id is not None
    
    checks = get_url_checks(url_id)
    assert len(checks) == 1
    assert checks[0]["status_code"] == 200
    assert checks[0]["h1"] == "Test Title"

def test_db_connection():
    conn = get_connection()
    assert conn is not None
    conn.close()

def test_normalize_url():
    assert normalize_url("https://example.com/path") == "https://example.com"
    assert normalize_url("https://example.com:443") == "https://example.com:443"
    assert normalize_url("http://example.com:80/path") == "http://example.com:80"

def test_is_valid_url():
    assert is_valid_url("https://example.com") is True
    assert is_valid_url("http://sub.example.com/path?query=test") is False
    assert is_valid_url("not-a-url") is False
    assert is_valid_url("") is False
    assert is_valid_url("https://" + "a" * 256) is False