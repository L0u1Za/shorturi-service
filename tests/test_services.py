import pytest
import os

os.environ["ENV"] = ".env.test"

from datetime import datetime, timedelta

from app.services.auth import create_user, authenticate_user, create_access_token
from app.services.background_tasks import delete_expired_links, add_popular_links_to_cache
from app.services.link_shortener import (
    create_short_link,
    get_original_url,
    delete_short_link,
    update_short_link,
    get_link_stats,
)
from app.models.schemas import ShortenRequest, UpdateLinkRequest, UserCreate

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from app.utils.cache import redis_client
from app.models.database import conn, cursor

@pytest.fixture(scope="function", autouse=True)
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

@pytest.fixture(scope="function", autouse=True)
def clear_redis():
    """Фикстура для очистки Redis перед каждым тестом."""
    redis_client.flushdb()
    yield
    redis_client.flushdb()

# Unit Tests for auth.py
def test_create_user():
    """Test user registration."""
    user_data = UserCreate(username="testuser", password="testpassword", email="testuser@example.com")
    result = create_user(user_data)
    assert result["id"] is not None

def test_authenticate_user():
    """Test user authentication."""
    user_data = UserCreate(username="testuser", password="testpassword", email="testuser@example.com")
    create_user(user_data)

    user = authenticate_user(username="testuser", password="testpassword")
    assert user is not None
    assert user["username"] == "testuser"

def test_create_access_token():
    """Test access token creation."""
    token = create_access_token(data={"sub": "testuser"})
    assert isinstance(token, str)

# Unit Tests for link_shortener.py
def test_create_short_link():
    """Test creating a short link."""
    request = ShortenRequest(original_url="https://example.com/", custom_alias=None, expires_at=None)
    result = create_short_link(request, user_id=None)
    assert "short_code" in result

def test_get_original_url():
    """Test retrieving the original URL from a short code."""
    request = ShortenRequest(original_url="https://example.com/", custom_alias=None, expires_at=None)
    result = create_short_link(request, user_id=None)
    short_code = result["short_code"]

    original_url = get_original_url(short_code)
    assert original_url == "https://example.com/"

def test_delete_short_link():
    """Test deleting a short link."""
    # Регистрируем пользователя
    user_data = UserCreate(username="testuser", password="testpassword", email="testuser@example.com")
    user = create_user(user_data)
    
    request = ShortenRequest(original_url="https://example.com", custom_alias=None, expires_at=None)
    result = create_short_link(request, user_id=user["id"])
    short_code = result["short_code"]

    delete_result = delete_short_link(short_code, user_id=user["id"])
    assert delete_result == {"message": "Link deleted successfully"}

def test_update_short_link():
    """Test updating a short link."""
    # Регистрируем пользователя
    user_data = UserCreate(username="testuser", password="testpassword", email="testuser@example.com")
    user = create_user(user_data)
    
    request = ShortenRequest(original_url="https://example.com/", custom_alias=None, expires_at=None)
    result = create_short_link(request, user_id=user["id"])
    short_code = result["short_code"]

    update_request = UpdateLinkRequest(new_url="https://updated-example.com/")
    update_result = update_short_link(short_code, update_request, user_id=user["id"])
    assert update_result == {"message": "Link updated successfully"}

def test_get_link_stats():
    """Test retrieving statistics for a short link."""
    request = ShortenRequest(original_url="https://example.com/", custom_alias=None, expires_at=None)
    result = create_short_link(request, user_id=None)
    short_code = result["short_code"]

    stats = get_link_stats(short_code)
    assert stats["original_url"] == "https://example.com/"
    assert stats["usage_count"] == 0