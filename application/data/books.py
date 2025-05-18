from datetime import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin

user_to_book = sqlalchemy.Table(  # Таблица, в которой хранятся любимые книги пользователя
    'user_to_book',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('user_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id')),
    sqlalchemy.Column('book_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('books.id'))
)


class Book(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'books'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.LargeBinary)
    pdf_file = sqlalchemy.Column(sqlalchemy.LargeBinary)
    genre = orm.relationship('Genre', secondary='book_to_genre', backref='book')
