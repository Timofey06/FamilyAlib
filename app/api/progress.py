from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.schemas.progress import ProgressCreate, ProgressRead
from app.services.progress_service import create_or_update_progress, get_user_progress, get_user_progress_list

router = APIRouter(prefix='/progress', tags=['progress'])


@router.post('', response_model=ProgressRead)
def update_progress(progress_in: ProgressCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return create_or_update_progress(db, current_user.id, progress_in)


@router.get('', response_model=List[ProgressRead])
def list_progress(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return get_user_progress_list(db, current_user.id)


@router.get('/{book_id}', response_model=ProgressRead)
def read_progress(book_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    progress = get_user_progress(db, current_user.id, book_id)
    if progress is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Progress not found')
    return progress
