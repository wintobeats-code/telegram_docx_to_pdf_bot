"""Работа с базой данных"""
import datetime
from logging import info
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Optional
from sqlalchemy.orm import Session
from db_models import Base, User, Conversion, ConversionStatus
from db_sessions import sessionlocal, engine


class AbstractRepository(ABC):
    """Абстрактный репозиторий для работы с данными."""
    @abstractmethod
    def add(self, obj):
        """Добавить объект в сессию"""
    @abstractmethod
    def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Получить пользователя по telegram_id"""
    @abstractmethod
    def get_status_by_name(self, name: str) -> Optional[ConversionStatus]:
        """Получить статус по имени"""


class SqlAlchemyRepository(AbstractRepository):
    """Реализация репозитория"""
    def __init__(self, session: Session):
        self.session = session

    def add(self, obj):
        self.session.add(obj)

    def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        return self.session.query(User).filter(User.telegram_id == telegram_id).first()

    def get_status_by_name(self, name: str) -> Optional[ConversionStatus]:
        return self.session.query(ConversionStatus).filter_by(status_name=name).first()

# pylint: disable=too-few-public-methodsclass UnitOfWork:
    """Unit of Work для управления транзакциями"""
    def __init__(self, session_factory=sessionlocal):
        self.session_factory = session_factory
        self.session: Optional[Session] = None
        self.repo: Optional[SqlAlchemyRepository] = None

    @contextmanager
    def __call__(self):
        self.session = self.session_factory()
        self.repo = SqlAlchemyRepository(self.session)
        try:
            yield self
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        finally:
            self.session.close()


def intermediate_status(user_id: int, original_file_id: str, status_name: str) -> int:
    """Создаёт запись о конвертации с заданным статусом и создаёт пользователя при необходимости"""
    uow = UnitOfWork()
    with uow():
        user = uow.repo.get_by_telegram_id(user_id)
        if not user:
            user = User(telegram_id=user_id, username=None)
            uow.repo.add(user)
            uow.session.flush()

        status = uow.repo.get_status_by_name(status_name)
        if not status:
            raise RuntimeError(f"Статус '{status_name}' не найден в таблице conversion_status")

        conversion = Conversion(
            user_id=user.id,
            file_id=original_file_id,
            pdf_file_id=None,
            status_id=status.id,
            created_at=datetime.datetime.now()
        )
        uow.repo.add(conversion)
        return conversion.id
# pylint: disable=too-many-arguments,too-many-positional-arguments

def save_info_db(
    user_id: int,
    username: str | None,
    original_file_id: str,
    pdf_file_id: str | None,
    timestamp: datetime.datetime,
    status_name: str
):
    """Сохраняет информацию о конвертации в базу данных"""
    uow = UnitOfWork()
    with uow():
        user = uow.repo.get_by_telegram_id(user_id)
        if user:
            if user.username != username:
                user.username = username
            user_db_id = user.id
        else:
            user = User(telegram_id=user_id, username=username)
            uow.repo.add(user)
            uow.session.flush()
            user_db_id = user.id

        status = uow.repo.get_status_by_name(status_name)
        if not status:
            raise RuntimeError(f"Статус '{status_name}' не найден в таблице conversion_status")

        conversion = Conversion(
            user_id=user_db_id,
            file_id=original_file_id,
            pdf_file_id=pdf_file_id,
            status_id=status.id,
            created_at=timestamp
        )
        uow.repo.add(conversion)
        info("Запись сохранена в БД")

Base.metadata.create_all(bind=engine)
