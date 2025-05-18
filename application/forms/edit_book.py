from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FileField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed


class EditBookForm(FlaskForm):
    title = StringField('Введите название', validators=[DataRequired()])
    description = TextAreaField('Введите описание', validators=[DataRequired()])
    image = FileField('Выберите изображение (.png, .jpg) - Предварительно загружено',
                      validators=[FileAllowed(['jpg', 'png'], 'Только картинки в формате .jpg, .png!')])
    genre = SelectField('Выберите жанр', choices=[])
    pdf_file = FileField('Загрузите книгу в формате .pdf - Предварительно загружено',
                         validators=[FileAllowed(['pdf'], 'Только .pdf файлы!')])
    submit = SubmitField('Отправить')
