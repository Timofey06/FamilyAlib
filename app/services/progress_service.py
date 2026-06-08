from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.progress import UserBookProgress
from app.schemas.progress import ProgressCreate


def get_user_progress(db: Session, user_id: int, book_id: int):
    statement = select(UserBookProgress).where(
        UserBookProgress.user_id == user_id,
        UserBookProgress.book_id == book_id,
    )
    return db.scalar(statement)


def get_user_progress_list(db: Session, user_id: int):
    statement = select(UserBookProgress).where(UserBookProgress.user_id == user_id)
    return db.scalars(statement).all()


def create_or_update_progress(db: Session, user_id: int, progress_in: ProgressCreate):
    progress = get_user_progress(db, user_id, progress_in.book_id)
    if progress is None:
        progress = UserBookProgress(
            user_id=user_id,
            book_id=progress_in.book_id,
            current_chapter_id=progress_in.current_chapter_id,
            current_position_seconds=progress_in.current_position_seconds,
            completion_percent=progress_in.completion_percent,
            is_finished=progress_in.is_finished,
        )
        db.add(progress)
    else:
        progress.current_chapter_id = progress_in.current_chapter_id
        progress.current_position_seconds = progress_in.current_position_seconds
        progress.completion_percent = progress_in.completion_percent
        progress.is_finished = progress_in.is_finished
    db.commit()
    db.refresh(progress)
    return progress


def toggle_favorite(db: Session, user_id: int, book_id: int):
    progress = get_user_progress(db, user_id, book_id)
    if progress is None:
        progress = UserBookProgress(
            user_id=user_id,
            book_id=book_id,
            current_chapter_id=None,
            current_position_seconds=0,
            completion_percent=0,
            is_finished=False,
            is_favorite=True,
        )
        db.add(progress)
    else:
        progress.is_favorite = not progress.is_favorite
    db.commit()
    db.refresh(progress)
    return progress


def get_favorites(db: Session, user_id: int):
    statement = select(UserBookProgress).where(
        UserBookProgress.user_id == user_id,
        UserBookProgress.is_favorite == True,
    )
    return db.scalars(statement).all()
