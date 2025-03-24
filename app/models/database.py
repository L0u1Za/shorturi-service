import psycopg2

import app.config

conn = psycopg2.connect(
    dbname=app.config.DB_NAME,
    user=app.config.DB_USER,
    password=app.config.DB_PASSWORD,
    host=app.config.DB_HOST,
    port=app.config.DB_PORT
)
cursor = conn.cursor()

def create_tables():
    """Создает таблицы в базе данных, если они еще не созданы."""

    create_user_table = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        hashed_password VARCHAR(255) NOT NULL
    );
    """
    create_links_table = """
    CREATE TABLE IF NOT EXISTS links (
        id SERIAL PRIMARY KEY,
        short_code VARCHAR(255) UNIQUE NOT NULL,
        original_url TEXT NOT NULL,
        custom_alias VARCHAR(255) UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP,
        usage_count INTEGER DEFAULT 0,
        last_used TIMESTAMP,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
    );
    """

    cursor.execute(create_user_table)
    cursor.execute(create_links_table)
    conn.commit()

