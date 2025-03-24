from app.models.database import cursor, conn
from app.utils.cache import cache_set
import asyncio

# Функция для автоматического удаления истекших ссылок
async def delete_expired_links():
    while True:
        cursor.execute("DELETE FROM links WHERE expires_at IS NOT NULL AND expires_at < NOW()")
        conn.commit()
        await asyncio.sleep(600)

# Сохраняем самые популярные ссылки в cache
async def add_popular_links_to_cache():
    while True:
        cursor.execute("SELECT short_code, original_url FROM links ORDER BY usage_count DESC LIMIT 50")
        popular_links = cursor.fetchall()
        for link in popular_links:
            cache_set(link[0], link[1])
        await asyncio.sleep(600)