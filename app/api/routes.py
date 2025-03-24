from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

from app.models.schemas import ShortenRequest, UpdateLinkRequest, UserCreate, UserLogin, Token
from app.services import link_shortener
from app.services.auth import create_user, authenticate_user, create_access_token, verify_token


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

@router.post("/register", response_model=UserCreate)
def register(user: UserCreate):
    create_user(user)
    return user

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: UserLogin):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"id": user["id"]})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me")
def read_users_me(token: str = Depends(oauth2_scheme)):
    user_data = verify_token(token)
    return user_data

@router.post("/links/shorten")
def shorten_link(request: ShortenRequest, token: Optional[str] = Depends(oauth2_scheme)):
    if token:
        user_id = verify_token(token)["id"]
    else:
        user_id = None
    return link_shortener.create_short_link(request, user_id)

@router.get("/{short_code}")
def redirect(short_code: str):
    return RedirectResponse(url=link_shortener.get_original_url(short_code))

@router.delete("/links/{short_code}")
def delete_link(short_code: str, token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="You need to be logged in to delete")

    user_data = verify_token(token)
    return link_shortener.delete_short_link(short_code, user_data["id"])

@router.put("/links/{short_code}")
def update_link(short_code: str, request: UpdateLinkRequest, token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="You need to be logged in to update")

    user_data = verify_token(token)
    return link_shortener.update_short_link(short_code, request, user_data["id"])

@router.get("/links/{short_code}/stats")
def get_stats(short_code: str):
    return link_shortener.get_link_stats(short_code)

@router.get("/links/search")
def search_link(original_url: str = Query(..., description="Оригинальный URL для поиска")):
    return link_shortener.search_link(original_url)
