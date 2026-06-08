from datetime import datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from app.schemas.token import TokenPayload

pwd_context = CryptContext(schemes=['pbkdf2_sha256'], deprecated='auto')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: str, username: str, is_admin: bool) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        'sub': str(subject),
        'username': username,
        'is_admin': is_admin,
        'exp': expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenPayload(
            sub=payload.get('sub'),
            username=payload.get('username'),
            is_admin=payload.get('is_admin', False),
        )
    except JWTError as error:
        raise ValueError(str(error))
