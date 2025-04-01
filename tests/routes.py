import pytest
import os

os.environ["ENV"] = ".env.test"

from fastapi.testclient import TestClient
from app.main import app
from app.models.database import conn, cursor
client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def clear_database():
    """Фикстура для очистки базы данных перед каждым тестом."""

    try:
        # Отключаем ограничения внешних ключей
        cursor.execute("SET session_replication_role = 'replica';")

        # Удаляем данные из всех таблиц
        cursor.execute("""
            DO $$ DECLARE
                r RECORD;
            BEGIN
                FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                    EXECUTE 'TRUNCATE TABLE ' || quote_ident(r.tablename) || ' CASCADE;';
                END LOOP;
            END $$;
        """)

        # Включаем ограничения внешних ключей обратно
        cursor.execute("SET session_replication_role = 'origin';")
    finally:
        pass

@pytest.fixture
def auth_token():
    """Фикстура для получения токена авторизации."""
    register_data = {"username": "testuser", "password": "testpassword", "email": "testuser@example.com"}
    client.post("/auth/register", json=register_data)
    login_data = {"username": "testuser", "password": "testpassword"}
    response = client.post("/auth/token", json=login_data)
    return response.json()["access_token"]

def test_root_endpoint():
    """Тест корневого эндпоинта."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "URL Shortener Service is running!"}

def test_register_user():
    """Тест регистрации нового пользователя."""
    response = client.post("/auth/register", json={
        "username": "newuser",
        "password": "newpassword",
        "email": "newuser@example.com"
    })
    assert response.status_code == 200
    assert response.json()["username"] == "newuser"

def test_login_for_access_token():
    """Тест получения токена доступа."""
    response = client.post("/auth/token", json={
        "username": "newuser",
        "password": "newpassword"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_shorten_link( auth_token):
    """Тест создания короткой ссылки с мокированием."""
    
    response = client.post("/links/shorten", json={
        "original_url": "https://example.com",
        "custom_alias": "abc123"
    }, headers={"Authorization": f"Bearer {auth_token}"})
    
    assert response.status_code == 200
    assert response.json() == {"short_code": "abc123"}

def test_redirect_link():
    """Тест перенаправления по короткому коду с мокированием."""
    
    response = client.get("/abc123")
    
    assert response.status_code == 200
    assert response.url == "https://example.com/"

def test_update_link( auth_token):
    """Тест обновления короткой ссылки с мокированием."""
    
    response = client.put("/links/abc123", json={
        "new_url": "https://updated-example.com"
    }, headers={"Authorization": f"Bearer {auth_token}"})
    
    assert response.status_code == 200
    assert response.json() == {"message": "Link updated successfully"}

def test_get_link_stats( auth_token):
    """Тест получения статистики по короткой ссылке с мокированием."""
    response = client.get("/links/abc123/stats", headers={"Authorization": f"Bearer {auth_token}"})
    
    assert response.status_code == 200
    assert "usage_count" in response.json()

def test_search_link( auth_token):
    """Тест поиска короткой ссылки по оригинальному URL с мокированием."""
    response = client.get("/links/search", params={"original_url": "https://updated-example.com/"}, headers={"Authorization": f"Bearer {auth_token}"})
    
    assert response.status_code == 200
    assert response.json() == {"short_codes": [["abc123"]]}

def test_shorten_link_invalid_url(auth_token):
    """Тест создания короткой ссылки с невалидным URL."""
    response = client.post("/links/shorten", json={
        "original_url": "invalid-url"
    }, headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 422  # Unprocessable Entity
    assert "detail" in response.json()

def test_redirect_invalid_short_code():
    """Тест перенаправления по несуществующему короткому коду с мокированием."""
    response = client.get("/invalidcode")
    
    assert response.status_code == 404  # Not Found
    assert response.json() == {"detail": "Short link not found"}

def test_delete_invalid_short_code( auth_token):
    """Тест удаления несуществующей короткой ссылки с мокированием."""
    response = client.delete("/links/invalidcode", headers={"Authorization": f"Bearer {auth_token}"})
    
    assert response.status_code == 403

def test_update_invalid_short_code( auth_token):
    """Тест обновления несуществующей короткой ссылки с мокированием."""
    response = client.put("/links/invalidcode", json={
        "new_url": "https://example.com"
    }, headers={"Authorization": f"Bearer {auth_token}"})
    
    assert response.status_code == 403
    
def test_delete_link( auth_token):
    """Тест удаления короткой ссылки с мокированием."""
    
    response = client.delete("/links/abc123", headers={"Authorization": f"Bearer {auth_token}"})
    
    assert response.status_code == 200
    assert response.json() == {"message": "Link deleted successfully"}