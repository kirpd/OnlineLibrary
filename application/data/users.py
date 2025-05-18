from datetime import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    login = sqlalchemy.Column(sqlalchemy.String, unique=True, index=True)  # У каждого user не повторяется login
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    is_admin = sqlalchemy.Column(sqlalchemy.Boolean)  # Является ли этот user администратором
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now)
    book = orm.relationship('Book', secondary='user_to_book', backref='user', lazy='subquery')

    def set_password(self, password):  # Метод, который хеширует пароль
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):  # Метод, которой проверяет строку password с self.hashed_password
        return check_password_hash(self.hashed_password, password)
