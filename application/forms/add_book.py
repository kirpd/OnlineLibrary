from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FileField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileRequired, FileAllowed


class AddBookForm(FlaskForm):
    title = StringField('Введите название', validators=[DataRequired()])
    description = TextAreaField('Введите описание', validators=[DataRequired()])
    image = FileField('Выберите изображение (.png, .jpg)',
                      validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Только картинки в формате .jpg, .png!')])
    genre = SelectField('Выберите жанр', choices=[])  # Пока что choices пустой, но после будет заполнен
    pdf_file = FileField('Загрузите книгу в формате .pdf',
                         validators=[FileRequired(), FileAllowed(['pdf'], 'Только .pdf файлы!')])
    submit = SubmitField('Отправить')
