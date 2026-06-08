from sqlalchemy.orm import declarative_base

Base = declarative_base()

from .book import Book
from .chapter import Chapter
from .progress import UserBookProgress
from .user import User
