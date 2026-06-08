from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.services.progress_service import toggle_favorite, get_favorites

router = APIRouter(prefix='/favorite', tags=['favorite'])


@router.post('/{book_id}')
def toggle_book_favorite(book_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    progress = toggle_favorite(db, current_user.id, book_id)
    return {'book_id': book_id, 'is_favorite': progress.is_favorite}


@router.get('', tags=['favorite'])
def list_favorites(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return [
        {
            'book_id': p.book_id,
            'current_chapter_id': p.current_chapter_id,
            'current_position_seconds': p.current_position_seconds,
            'completion_percent': p.completion_percent,
            'is_favorite': p.is_favorite,
            'is_finished': p.is_finished,
        }
        for p in get_favorites(db, current_user.id)
    ]
