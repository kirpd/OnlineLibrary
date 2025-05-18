from flask_restful import Resource, abort
from flask import jsonify
from . import db_session
from .books import Book
import base64


def abort_if_book_not_found(book_id):
    db_sess = db_session.create_session()
    book = db_sess.query(Book).filter(Book.id == book_id).first()
    if not book:
        abort(404, message=f"Book {book_id} not found")


class BookResource(Resource):
    def get(self, book_id):
        abort_if_book_not_found(book_id)
        db_sess = db_session.create_session()
        book = db_sess.query(Book).filter(Book.id == book_id).first()
        book.image = str(base64.b64encode(book.image))[2:][:-1]  # Кодируем картинку в файл base64
        book.pdf_file = str(base64.b64encode(book.pdf_file))[2:][:-1]  # Кодируем pdf файл в файл base64
        return jsonify({'book': book.to_dict(only=(
            'id', 'title', 'description', 'created_date', 'modified_date', 'image', 'pdf_file'
        ))})


class BookListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        books = db_sess.query(Book).all()
        return jsonify({'books': [book.to_dict(only=(
            'id', 'title', 'description'
        )) for book in books]})
