from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField


class FilterGenre(FlaskForm):  # Фильтрация по жанрам
    genres = SelectField('Жанры', choices=[])
    apply = SubmitField('Применить')
