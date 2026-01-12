"""Модуль для настройки подключения к базе данных и управления сессиями."""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from alembic import command
from models import Base

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Создаёт и возвращает новую сессию SQLAlchemy."""
    dbsession = SessionLocal()
    try:
        yield dbsession
    finally:
        dbsession.close()
