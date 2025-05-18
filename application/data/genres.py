import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin

book_to_genre = sqlalchemy.Table(  # вспомогательная таблица для книги и жанров
    'book_to_genre',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('book_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('books.id')),
    sqlalchemy.Column('genre_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('genres.id'))
)


class Genre(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'genres'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True)
