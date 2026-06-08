import mimetypes
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse

from app.core.config import BOOKS_DIR

router = APIRouter(tags=['media'])


@router.get('/media/books/{book_id}/{filename}')
def media_book_file(book_id: int, filename: str, request: Request):
    book_dir = BOOKS_DIR / str(book_id)
    file_path = book_dir / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail='File not found')
    
    media_type, _ = mimetypes.guess_type(str(file_path))
    file_size = file_path.stat().st_size
    
    range_header = request.headers.get('range')
    if range_header:
        try:
            range_str = range_header.replace('bytes=', '')
            start, end = range_str.split('-')
            start = int(start) if start else 0
            end = int(end) if end else file_size - 1
            
            if start >= file_size or end >= file_size:
                raise HTTPException(status_code=416, detail='Range Not Satisfiable')
            
            with open(file_path, 'rb') as f:
                f.seek(start)
                data = f.read(end - start + 1)
            
            return StreamingResponse(
                iter([data]),
                status_code=206,
                headers={
                    'Content-Range': f'bytes {start}-{end}/{file_size}',
                    'Content-Length': str(end - start + 1),
                    'Content-Type': media_type or 'application/octet-stream',
                    'Accept-Ranges': 'bytes',
                }
            )
        except (ValueError, IndexError):
            pass
    
    return FileResponse(
        path=file_path,
        media_type=media_type or 'application/octet-stream',
        headers={'Accept-Ranges': 'bytes'}
    )
