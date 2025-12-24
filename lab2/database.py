"""
Модуль для настройки подключения к базе данных SQLite.
Использует SQLAlchemy для работы с БД.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Путь к файлу базы данных SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./sppr.db"

# Создание движка SQLAlchemy
# connect_args={"check_same_thread": False} необходим для работы SQLite в многопоточном режиме
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Создание фабрики сессий для работы с БД
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для всех моделей
Base = declarative_base()


def get_db():
    """
    Генератор для получения сессии базы данных.
    Используется как зависимость в FastAPI endpoints.
    
    Yields:
        Session: Сессия базы данных
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Инициализация базы данных - создание всех таблиц.
    Вызывается при первом запуске приложения.
    """
    Base.metadata.create_all(bind=engine)





