from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.book import Book
from app.models.chapter import Chapter
from app.schemas.book import BookCreate, BookUpdate
from app.services.file_service import save_cover, save_chapters, remove_cover, remove_book_files


def get_book(db: Session, book_id: int) -> Optional[Book]:
    statement = select(Book).options(joinedload(Book.uploader)).where(Book.id == book_id)
    return db.scalars(statement).one_or_none()


def get_books(db: Session, current_user=None) -> List[Book]:
    # If no authenticated user, only show books with show_to_all == True
    if current_user is None:
        statement = select(Book).options(joinedload(Book.uploader)).where(Book.show_to_all == True).order_by(Book.created_at.desc())
        return db.scalars(statement).all()
    # Admin sees everything
    if getattr(current_user, 'is_admin', False):
        statement = select(Book).options(joinedload(Book.uploader)).order_by(Book.created_at.desc())
        return db.scalars(statement).all()
    # Regular user sees public books and those they uploaded
    statement = select(Book).options(joinedload(Book.uploader)).where((Book.show_to_all == True) | (Book.uploader_id == current_user.id)).order_by(Book.created_at.desc())
    return db.scalars(statement).all()


def create_book(db: Session, book_in: BookCreate, cover_file, chapter_files, uploader=None) -> Book:
    book = Book(
        title=book_in.title,
        author_name=book_in.author_name,
        series_name=book_in.series_name,
        series_order=book_in.series_order,
        description=book_in.description or '',
        cover_path='',
        show_to_all=getattr(book_in, 'show_to_all', True),
        uploader_id=getattr(uploader, 'id', None),
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    cover_path = save_cover(book.id, cover_file)
    chapter_data = save_chapters(book.id, chapter_files)
    total_seconds = 0
    chapters = []
    for chapter_title, chapter_number, file_path, duration in chapter_data:
        total_seconds += duration
        chapters.append(Chapter(
            book_id=book.id,
            title=chapter_title,
            chapter_number=chapter_number,
            duration_seconds=duration,
            file_path=file_path,
        ))
    book.chapters = chapters
    book.cover_path = cover_path
    book.total_duration_seconds = total_seconds
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def update_book(db: Session, book: Book, data: BookUpdate, cover_file=None) -> Book:
    for field, value in data.model_dump().items():
        setattr(book, field, value)

    if cover_file is not None:
        remove_cover(book.id)
        book.cover_path = save_cover(book.id, cover_file)

    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def delete_book(db: Session, book: Book) -> None:
    remove_book_files(book.id)
    db.delete(book)
    db.commit()
