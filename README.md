# URL Shortener API

## 📌 Описание
Этот сервис позволяет сокращать длинные ссылки, управлять ими, получать статистику и устанавливать время жизни.

## 🚀 Функционал API

### 🔹 Основные возможности:
- Сокращение длинных ссылок.
- Перенаправление по короткой ссылке.
- Статистика по использованию ссылок.
- Удаление и обновление ссылок.
- Поиск ссылок по оригинальному URL.
- Регистрация и авторизация пользователей.
- Ограничение управления ссылками только владельцем.

### 🔹 Технологии:
- **FastAPI** (основной веб-фреймворк).
- **PostgreSQL** (основное хранилище данных).
- **Redis** (кэширование популярных ссылок).
- **Docker** (разворачивание контейнеров с БД и API).

## 📜 Эндпоинты

### 🔹 Аутентификация
#### 🔑 Регистрация пользователя
```
POST /auth/register
{
  "username": "user",
  "password": "securepassword"
  "email": "youremail@gmail.com"
}
```
#### 🔑 Авторизация и получение токена
```
POST /auth/token
{
  "username": "user",
  "password": "securepassword"
}
```

### 🔹 Работа с ссылками
#### 🔗 Создать короткую ссылку (доступно для всех)
```
POST /links/shorten
{
  "original_url": "https://example.com"
}
```
#### 🔗 Создать ссылку с кастомным alias
```
POST /links/shorten
{
  "original_url": "https://example.com",
  "custom_alias": "myalias"
}
```
#### 🔗 Создать ссылку с временем жизни
```
POST /links/shorten
{
  "original_url": "https://example.com",
  "expires_at": 1234567890
}
```

#### 🔗 Создать ссылку после авторизации
```
POST /links/shorten Authorization: Bearer <Token>
{
  "original_url": "https://example.com"
}
```

#### 🔗 Получить статистику по ссылке
```
GET /links/{short_code}/stats
```
#### 🔗 Удалить свою ссылку (только для владельца)
```
DELETE /links/{short_code} Authorization: Bearer <Token>
```

#### 🔗 Изменить свою ссылку (только для владельца)
```
PUT /links/{short_code} Authorization: Bearer <Token>
{
  "original_url": "https://example2.com"
}
```

#### 🔗 Поиск ссылки по оригинальному URL
```
GET /links/search?original_url=https://example.com
```

### 🔹 Перенаправление
```
GET /{short_code}
```

## 🛠 Инструкция по запуску

### 🔹 1. Клонируем репозиторий
```bash
git clone https://github.com/L0u1Za/shorturi-service.git
cd shorturi-service
```

### 🔹 2. Настраиваем переменные окружения
Создай файл `.env` и заполни его:
```ini
DB_USER=...
DB_PASSWORD=...
DB_NAME=...
DB_HOST=...
DB_PORT=...
REDIS_HOST=...
REDIS_PORT=...
SECRET_KEY=...
ALGORITHM=...
```

### 🔹 3. Запускаем контейнеры
```bash
docker-compose up --build
```

## 📂 Структура БД

| Таблица  | Описание |
|----------|-----------|
| users | Пользователи (id, username, hashed_password, email) |
| links | Ссылки (оригинальный URL, short_code, владелец, время жизни, количество использований, время последнего использования, дата создания) |

## Redis

В кеше хранятся самые популярные ссылки.

key: short_code, value: original_url



# Тестирование

Для запуска тестов сначала поднимите тестовые базу данных и кеш:

```bash
docker-compose up postgres redis
```

## Unit тестирование

```bash
pytest tests --disable-warnings
coverage run -m pytest
coverage html
```

## Функциональное тестирование

```bash
pytest tests/routes.py
```

## Нагрузочное тестирование

```bash
locust -f locustfile.py --host http://localhost:8000
```

![Report](image.png)