import shutil
from pathlib import Path
from typing import List, Tuple

from mutagen import File as MutagenFile
from fastapi import UploadFile

from app.core.config import BOOKS_DIR


SUPPORTED_AUDIO_EXTENSIONS = {'.mp3', '.m4a', '.m4b'}


def get_book_directory(book_id: int) -> Path:
    directory = BOOKS_DIR / str(book_id)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def get_book_cover_path(book_id: int) -> Path:
    return get_book_directory(book_id) / 'cover.jpg'


def save_cover(book_id: int, cover_file: UploadFile) -> str:
    destination = get_book_cover_path(book_id)
    with destination.open('wb') as buffer:
        shutil.copyfileobj(cover_file.file, buffer)
    return destination.relative_to(BOOKS_DIR.parent).as_posix()


def _get_audio_extension(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED_AUDIO_EXTENSIONS:
        raise ValueError('Unsupported audio file type')
    return ext


def save_chapters(book_id: int, chapter_files: List[UploadFile]) -> List[Tuple[str, int, str]]:
    results = []
    folder = get_book_directory(book_id)
    for index, upload in enumerate(sorted(chapter_files, key=lambda f: f.filename)):
        ext = _get_audio_extension(upload.filename)
        file_name = f'{index + 1:02d}{ext}'
        destination = folder / file_name
        with destination.open('wb') as buffer:
            shutil.copyfileobj(upload.file, buffer)
        duration = get_audio_duration_seconds(destination)
        results.append((upload.filename or file_name, index + 1, destination.relative_to(BOOKS_DIR.parent).as_posix(), duration))
    return results


def get_audio_duration_seconds(path: Path) -> int:
    audio = MutagenFile(path)
    if audio is None or not hasattr(audio, 'info') or not getattr(audio.info, 'length', None):
        return 0
    return int(audio.info.length)


def remove_cover(book_id: int) -> None:
    cover_path = get_book_cover_path(book_id)
    if cover_path.exists():
        cover_path.unlink()


def remove_book_files(book_id: int) -> None:
    folder = get_book_directory(book_id)
    if folder.exists():
        shutil.rmtree(folder)
