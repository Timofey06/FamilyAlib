from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.token import Token
from app.schemas.user import UserCreate, UserRead
from app.services.auth_service import verify_password, create_access_token
from app.services.user_service import get_user_by_username
from app.api.dependencies import get_current_user, get_db

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/login', response_model=Token)
def login(user_in: UserCreate, db: Session = Depends(get_db)):
    user = get_user_by_username(db, user_in.username)
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
    access_token = create_access_token(subject=str(user.id), username=user.username, is_admin=user.is_admin)
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.get('/me', response_model=UserRead)
def me(current_user=Depends(get_current_user)):
    return current_user
