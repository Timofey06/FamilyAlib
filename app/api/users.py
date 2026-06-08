from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_admin_user, get_db
from app.schemas.user import PasswordUpdate, UserCreate, UserRead
from app.services.user_service import create_user, delete_user, get_user, get_user_by_username, get_users, update_user_password

router = APIRouter(prefix='/api/users', tags=['users'])


@router.get('', response_model=List[UserRead])
def list_users(db: Session = Depends(get_db), current_user=Depends(get_current_admin_user)):
    return get_users(db)


@router.post('', response_model=UserRead)
def create_new_user(user_in: UserCreate, db: Session = Depends(get_db), current_user=Depends(get_current_admin_user)):
    existing = get_user_by_username(db, user_in.username)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username already taken')
    return create_user(db, user_in)


@router.delete('/{user_id}')
def remove_user(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_admin_user)):
    user = get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    if user.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot delete yourself')
    delete_user(db, user)
    return {'detail': 'User deleted'}


@router.put('/{user_id}/password')
def change_user_password(
    user_id: int,
    password_in: PasswordUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user),
):
    user = get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    if not password_in.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Password must not be empty')
    update_user_password(db, user, password_in.password)
    return {'detail': 'Password updated'}
