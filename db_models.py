"""Таблицы для БД"""
# pylint: disable=too-few-public-methods
from datetime import datetime
from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    """Маппинг"""

class User(Base):
    """Модель пользователя Telegram"""
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    conversions: Mapped[list["Conversion"]] = relationship("Conversion", back_populates="user")

    def __str__(self):
        """Юзернейм в строку для выводу в Flask Admin"""
        return self.username

class Conversion(Base):
    """Модель конвертаций"""
    __tablename__ = 'conversions'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    file_id: Mapped[str] = mapped_column(String(255))
    pdf_file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status_id: Mapped[int] = mapped_column(Integer,ForeignKey('conversion_status.id'))
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    user: Mapped["User"] = relationship(back_populates="conversions")
    status: Mapped["ConversionStatus"] = relationship(back_populates="conversions")

    def __str__(self):
        """Имя статуса в строку для Flask Admin"""
        return self.status_name


class ConversionStatus(Base):
    "Модель статусов конвертаций"
    __tablename__ = 'conversion_status'
    id: Mapped[int] = mapped_column(Integer, primary_key = True)
    status_name: Mapped[str] = mapped_column(String(50), unique=True)
    conversions: Mapped[list["Conversion"]] = relationship(back_populates="status")
