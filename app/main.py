from fastapi import FastAPI
import asyncio
from contextlib import asynccontextmanager

from app.api.routes import router
from app.models.database import create_tables
from app.services.background_tasks import delete_expired_links, add_popular_links_to_cache


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Глобальный event handler для запуска фоновых задач"""

    cleanup_task = asyncio.create_task(delete_expired_links())  # Запускаем удаление истекших ссылок
    cache_task = asyncio.create_task(add_popular_links_to_cache())  # Запускаем кэширование популярных ссылок

    create_tables()

    yield

    cleanup_task.cancel()
    cache_task.cancel()

    try:
        await cleanup_task
        await cache_task
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)
app.include_router(router)

@app.get("/")
def root():
    return {"message": "URL Shortener Service is running!"}
