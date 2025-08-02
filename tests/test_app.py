import pytest
import requests
from page_analyzer.db import get_url_checks, get_url_by_id
from flask import get_flashed_messages
from page_analyzer import app as app_module

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert 'Анализатор страниц' in response.text

def test_add_url(client):
    response = client.post('/urls', data={'url': 'https://example.com'})
    assert response.status_code == 302
    assert '/urls/' in response.location

def test_check_url(client):
    response = client.post('/urls', data={'url': 'https://example.com'})
    url_id = response.location.split('/')[-1]
    
    response = client.post(f'/urls/{url_id}/checks')
    assert response.status_code == 302
    assert response.location.endswith(f'/urls/{url_id}')

def test_add_invalid_url(client):
    response = client.post('/urls', data={'url': ''})
    assert response.status_code == 422
    assert 'Некорректный URL' in response.text
    
    response = client.post('/urls', data={'url': 'ftp://example.com'})
    assert response.status_code == 422
    assert 'Некорректный URL' in response.text
    
    long_url = 'https://' + 'a' * 300
    response = client.post('/urls', data={'url': long_url})
    assert response.status_code == 422
    assert 'Некорректный URL' in response.text

def test_add_existing_url(client):
    client.post('/urls', data={'url': 'https://example.com'})
    
    response = client.post('/urls', data={'url': 'https://example.com'}, follow_redirects=True)
    assert response.status_code == 200
    assert 'Страница уже существует' in response.text

def test_show_nonexistent_url(client):
    response = client.get('/urls/999999', follow_redirects=True)
    assert response.status_code == 200
    assert 'Страница не найдена' in response.text

def test_check_nonexistent_url(client):
    response = client.post('/urls/999999/checks', follow_redirects=True)
    assert response.status_code == 200
    assert 'Страница не найдена' in response.text

def test_check_url_timeout(client, monkeypatch):
    response = client.post('/urls', data={'url': 'https://example.com'})
    url_id = response.location.split('/')[-1]
    
    def mock_get(*args, **kwargs):
        raise requests.exceptions.Timeout("Test timeout")
    
    monkeypatch.setattr(requests, 'get', mock_get)
    
    client.post(f'/urls/{url_id}/checks')
    response = client.get(f'/urls/{url_id}', follow_redirects=True)
    assert response.status_code == 200
    assert 'Таймаут при проверке сайта' in response.text

def test_check_url_ssl_error(client, monkeypatch):
    response = client.post('/urls', data={'url': 'https://example.com'})
    url_id = response.location.split('/')[-1]
    
    def mock_get(*args, **kwargs):
        raise requests.exceptions.SSLError("Test SSL error")
    
    monkeypatch.setattr(requests, 'get', mock_get)
    
    client.post(f'/urls/{url_id}/checks')
    response = client.get(f'/urls/{url_id}', follow_redirects=True)
    assert response.status_code == 200
    assert 'Ошибка SSL сертификата' in response.text

def test_check_url_without_meta(client, monkeypatch):
    response = client.post('/urls', data={'url': 'https://example.com'})
    url_id = response.location.split('/')[-1]
    
    class MockResponse:
        def __init__(self):
            self.status_code = 200
            self.text = "<html><title>Test</title><h1>Header</h1></html>"
            self.content = self.text.encode('utf-8')
            self.history = []
            self.headers = {'Content-Type': 'text/html'}
        
        def raise_for_status(self):
            pass

    def mock_get(*args, **kwargs):
        return MockResponse()
    
    monkeypatch.setattr(requests, 'get', mock_get)
    
    client.post(f'/urls/{url_id}/checks')
    
    checks = get_url_checks(int(url_id))
    assert len(checks) > 0
    assert checks[0]["h1"] == "Header"
    assert checks[0]["title"] == "Test"
    assert checks[0]["description"] is None