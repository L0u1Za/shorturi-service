from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from datetime import timedelta, datetime
import jwt

from app.models.schemas import UserCreate, UserLogin, Token
from app.models.database import conn, cursor
from app.config import SECRET_KEY, ALGORITHM

ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Время жизни токена

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(user: UserCreate):
    # Проверка, существует ли пользователь с таким именем
    cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (user.username, user.email,))
    existing_user = cursor.fetchone()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email is already taken")

    hashed_password = pwd_context.hash(user.password)
    cursor.execute("""
        INSERT INTO users (username, email, hashed_password)
        VALUES (%s, %s, %s) RETURNING id;
        """, (user.username, user.email, hashed_password))

    user_id = cursor.fetchone()[0]
    conn.commit()
    return {"id": user_id, "hashed_password": hashed_password}


def authenticate_user(username: str, password: str):
    cursor.execute("SELECT id, username, email, hashed_password FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    if user is None:
        return False
    if not pwd_context.verify(password, user[3]):
        return False
    return {"id": user[0], "username": user[1], "email": user[2], "hashed_password": user[3]}


def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.exceptions.PyJWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
