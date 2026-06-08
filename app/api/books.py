from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from typing import List

from app.api.dependencies import get_current_user, get_db, get_current_user_optional
from app.schemas.book import BookCreate, BookRead, BookUpdate
from app.services.book_service import get_book, get_books, create_book, update_book, delete_book

router = APIRouter(prefix='/books', tags=['books'])


@router.get('', response_model=List[BookRead])
def list_books(db: Session = Depends(get_db), current_user=Depends(get_current_user_optional)):
    return get_books(db, current_user)


@router.get('/{book_id}', response_model=BookRead)
def read_book(book_id: int, db: Session = Depends(get_db)):
    book = get_book(db, book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Book not found')
    return book


from app.schemas.chapter import ChapterRead

@router.get('/{book_id}/chapters', response_model=List[ChapterRead])
def read_chapters(book_id: int, db: Session = Depends(get_db)):
    book = get_book(db, book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Book not found')
    return [
        chapter
        for chapter in sorted(book.chapters, key=lambda chapter: chapter.chapter_number)
    ]


def _parse_bool_form(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() not in ('false', '0', 'no', 'off')
    return bool(value)


@router.post('', response_model=BookRead)
def create_new_book(
    title: str = Form(...),
    author_name: str = Form(...),
    series_name: str | None = Form(None),
    series_order: int | None = Form(None),
    description: str | None = Form(None),
    cover: UploadFile = File(...),
    chapters: List[UploadFile] = File(...),
    show_to_all: bool | str = Form(True),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    payload = BookCreate(
        title=title,
        author_name=author_name,
        series_name=series_name,
        series_order=series_order,
        description=description,
    )
    if hasattr(payload, 'show_to_all'):
        payload.show_to_all = _parse_bool_form(show_to_all)
    return create_book(db, payload, cover, chapters, uploader=current_user)


@router.put('/{book_id}', response_model=BookRead)
def edit_book(
    book_id: int,
    title: str = Form(...),
    author_name: str = Form(...),
    series_name: str | None = Form(None),
    series_order: int | None = Form(None),
    description: str | None = Form(None),
    show_to_all: bool | str = Form(True),
    cover: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    book = get_book(db, book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Book not found')
    if not (current_user.is_admin or book.uploader_id == current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Permission denied')
    payload = BookUpdate(
        title=title,
        author_name=author_name,
        series_name=series_name,
        series_order=series_order,
        description=description,
        show_to_all=_parse_bool_form(show_to_all),
    )
    return update_book(db, book, payload, cover_file=cover)


@router.delete('/{book_id}')
def remove_book(book_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    book = get_book(db, book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Book not found')
    # allow admin or uploader to delete
    if not (current_user.is_admin or book.uploader_id == current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Permission denied')
    delete_book(db, book)
    return {'detail': 'Book deleted'}
