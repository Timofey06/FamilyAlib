from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate
from app.services.auth_service import get_password_hash


def get_user_by_username(db: Session, username: str):
    statement = select(User).where(User.username == username)
    return db.scalar(statement)


def get_user(db: Session, user_id: int):
    return db.get(User, user_id)


def get_users(db: Session):
    statement = select(User).order_by(User.id)
    return db.scalars(statement).all()


def delete_user(db: Session, user: User):
    db.delete(user)
    db.commit()


def create_user(db: Session, user_in: UserCreate, is_admin: bool = False) -> User:
    user = User(
        username=user_in.username,
        password_hash=get_password_hash(user_in.password),
        is_admin=is_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user_password(db: Session, user: User, new_password: str):
    user.password_hash = get_password_hash(new_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
