from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.books import router as books_router
from app.api.progress import router as progress_router
from app.api.favorites import router as favorites_router
from app.api.media import router as media_router
from app.api.users import router as users_router
from app.api.views import router as views_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(books_router)
api_router.include_router(progress_router)
api_router.include_router(favorites_router)
api_router.include_router(media_router)
api_router.include_router(users_router)
api_router.include_router(views_router)
