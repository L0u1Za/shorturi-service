import uuid
from fastapi import HTTPException

from app.models.schemas import ShortenRequest, UpdateLinkRequest
from app.models.database import cursor, conn
from app.utils.cache import cache_get, cache_delete, cache_update

def create_short_link(request: ShortenRequest, user_id: int | None):
    short_code = request.custom_alias if request.custom_alias else str(uuid.uuid4())[:8]
    cursor.execute("SELECT * FROM links WHERE short_code = %s", (short_code,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Custom alias already exists")
    cursor.execute(
        "INSERT INTO links (short_code, original_url, expires_at, user_id) VALUES (%s, %s, %s, %s)",
        (short_code, str(request.original_url), request.expires_at, user_id)
    )
    conn.commit()
    return {"short_code": short_code}

def get_original_url(short_code: str):
    cached_url = cache_get(short_code)
    if cached_url:
        increase_usage_count(short_code)
        return cached_url

    cursor.execute("SELECT original_url FROM links WHERE short_code = %s", (short_code,))
    result = cursor.fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="Short link not found")
    increase_usage_count(short_code)
    return result[0]

def increase_usage_count(short_code: str):
    cursor.execute("UPDATE links SET usage_count = usage_count + 1, last_used = NOW() WHERE short_code = %s", (short_code,))
    conn.commit()
    return

def check_if_link_owner(short_code, user_id):
    cursor.execute("SELECT * FROM links WHERE user_id = %s AND short_code = %s", (user_id, short_code))
    return cursor.fetchone()

def delete_short_link(short_code: str, user_id: int):
    if not check_if_link_owner(short_code, user_id):
        raise HTTPException(status_code=403, detail="You are not authorized/have no rights to update this link")

    cursor.execute("DELETE FROM links WHERE short_code = %s", (short_code,))
    conn.commit()
    cache_delete(short_code)
    return {"message": "Link deleted successfully"}

def update_short_link(short_code: str, request: UpdateLinkRequest, user_id: int):
    if not check_if_link_owner(short_code, user_id):
        raise HTTPException(status_code=403, detail="You are not authorized/have no rights to update this link")

    cursor.execute("UPDATE links SET original_url = %s WHERE short_code = %s", (str(request.new_url), short_code))
    conn.commit()
    cache_update(short_code, str(request.new_url))
    return {"message": "Link updated successfully"}

def get_link_stats(short_code: str):
    cursor.execute("SELECT original_url, created_at, usage_count, last_used FROM links WHERE short_code = %s", (short_code,))
    result = cursor.fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="Short link not found")
    return {
        "original_url": result[0],
        "created_at": result[1],
        "usage_count": result[2],
        "last_used": result[3]
    }

def search_link(original_url: str):
    cursor.execute("SELECT short_code FROM links WHERE original_url = %s", (original_url,))
    result = cursor.fetchall()
    if not result:
        raise HTTPException(status_code=404, detail="Short link not found")
    return {
        "short_codes": result
    }
