from typing import Generator

from fastapi import Depends, Cookie, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.schemas.token import TokenPayload
from app.services.auth_service import decode_access_token
from app.services.user_service import get_user


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    authorization: str | None = Header(default=None),
    booklistener_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    auth_header = authorization or (f'Bearer {booklistener_token}' if booklistener_token else None)
    if not auth_header:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Missing authorization')
    token = auth_header.replace('Bearer ', '')
    try:
        payload: TokenPayload = decode_access_token(token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')
    user = get_user(db, int(payload.sub))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')
    return user


def get_current_user_optional(
    authorization: str | None = Header(default=None),
    booklistener_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    auth_header = authorization or (f'Bearer {booklistener_token}' if booklistener_token else None)
    if not auth_header:
        return None
    token = auth_header.replace('Bearer ', '')
    try:
        payload: TokenPayload = decode_access_token(token)
    except Exception:
        return None
    user = get_user(db, int(payload.sub))
    return user


def get_current_admin_user(current_user=Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Admin access required')
    return current_user
