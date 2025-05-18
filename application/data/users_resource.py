from flask_restful import Resource, abort
from flask import jsonify
from . import db_session
from .users import User


def abort_if_user_not_found(user_id):  # Функция, которая проверяет, существует ли пользователь
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    if not user:
        abort(404, message=f"User {user_id} not found")


class UserResource(Resource):
    def get(self, user_id):  # get запрос на одного пользователя
        abort_if_user_not_found(user_id)
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == user_id).first()
        return jsonify({'user': user.to_dict(only=(
            'id', 'login', 'is_admin', 'created_date'
        ))})


class UserListResource(Resource):
    def get(self):  # get запрос на всех пользователей
        db_sess = db_session.create_session()
        users = db_sess.query(User).all()
        return jsonify({'users': [user.to_dict(only=(
            'id', 'login', 'is_admin'
        )) for user in users]})
