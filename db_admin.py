"""Файл для панели админа БД"""
from flask import Flask, request, Response
from flask_admin import Admin
from flask_admin.base import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import check_password_hash, generate_password_hash
from db_models import User, Conversion, ConversionStatus
from db_sessions import sessionlocal
import os

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD')

class Authentication(AdminIndexView):
    """Защищённая главная страница админки"""
    def is_accessible(self):
        auth = request.authorization
        if not auth:
            return False
        if auth.username != ADMIN_USERNAME:
            return False
        if not check_password_hash(ADMIN_PASSWORD_HASH, auth.password):
            return False
        return True

class SQLAlchemySession:
    """Обёртка над сессией SQLAlchemy для совместимости с Flask-Admin"""

    def __init__(self, sessionmaker):
        """сессия"""
        self.sessionmaker = sessionmaker

    @property
    def query(self):
        """чтобы фласк не ругался на query импортируем здесь"""
        return self.sessionmaker().query

    def commit(self):
        """коммит сессии"""
        session = self.sessionmaker()
        session.commit()
        session.close()

    def rollback(self):
        """откат сессии"""
        session = self.sessionmaker()
        session.rollback()
        session.close()

    def close(self):
        """закрытие сессии"""

db_session = SQLAlchemySession(sessionlocal)

app = Flask(__name__)
app.secret_key = 'supersecret'

admin = Admin(app, name='Админ')

class UserView(ModelView):
    """пользователь"""
    column_list = ('id', 'telegram_id', 'username')

class ConversionView(ModelView):
    """вся информация о конвертации"""
    column_list = ('id', 'user', 'file_id', 'pdf_file_id', 'status', 'created_at')

admin.add_view(UserView(User, db_session))
admin.add_view(ConversionView(Conversion, db_session))
admin.add_view(ModelView(ConversionStatus, db_session))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
