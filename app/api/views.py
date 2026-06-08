from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.api.dependencies import get_current_admin_user, get_current_user

router = APIRouter()
templates = Jinja2Templates(directory='app/templates')


@router.get('/', response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


@router.get('/login', response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse('login.html', {'request': request})


@router.get('/users', response_class=HTMLResponse)
def users(request: Request, current_user=Depends(get_current_admin_user)):
    return templates.TemplateResponse('users.html', {'request': request})


@router.get('/upload', response_class=HTMLResponse)
def upload(request: Request, current_user=Depends(get_current_user)):
    return templates.TemplateResponse('upload.html', {'request': request})


@router.get('/book/{book_id}', response_class=HTMLResponse)
def book_detail(request: Request, book_id: int):
    return templates.TemplateResponse('book_detail.html', {'request': request, 'book_id': book_id})


@router.get('/favorites', response_class=HTMLResponse)
def favorites(request: Request):
    return templates.TemplateResponse('favorites.html', {'request': request})
