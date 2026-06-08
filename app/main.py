from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import DATA_DIR
from app.database.session import engine, SessionLocal
from app.models import Base
from app.schemas.user import UserCreate
from app.services.user_service import get_user_by_username, create_user
from app.core.config import ADMIN_USERNAME, ADMIN_PASSWORD

app = FastAPI(title='Family Alib')
app.include_router(api_router)
app.mount('/static', StaticFiles(directory='app/static'), name='static')


def create_database() -> None:
    Base.metadata.create_all(bind=engine)


def create_default_admin() -> None:
    db = SessionLocal()
    try:
        if get_user_by_username(db, ADMIN_USERNAME) is None:
            create_user(db, UserCreate(username=ADMIN_USERNAME, password=ADMIN_PASSWORD), is_admin=True)
    finally:
        db.close()


@app.on_event('startup')
def startup_event():
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    create_database()
    create_default_admin()


@app.get('/health')
def health_check():
    return {'status': 'ok'}
