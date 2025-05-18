from flask_restful import Resource, abort
from flask import jsonify
from . import db_session
from .genres import Genre


def abort_if_genre_not_found(genre_id):  # Функция, которая проверяет, существует ли жанр
    db_sess = db_session.create_session()
    genre = db_sess.query(Genre).filter(Genre.id == genre_id).first()
    if not genre:
        abort(404, message=f"Genre {genre} not found")


class GenreResource(Resource):
    def get(self, genre_id):  # get запрос на один жанр
        abort_if_genre_not_found(genre_id)
        db_sess = db_session.create_session()
        genre = db_sess.query(Genre).filter(Genre.id == genre_id).first()
        return jsonify({'genre': genre.to_dict(only=(
            'id', 'name'
        ))})


class GenreListResource(Resource):
    def get(self):  # get запрос на все жанры
        db_sess = db_session.create_session()
        genres = db_sess.query(Genre).all()
        return jsonify({'genres': [genre.to_dict(only=(
            'id', 'name'
        )) for genre in genres]})
