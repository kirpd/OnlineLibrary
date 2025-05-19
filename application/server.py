from io import BytesIO
import base64
from os import environ
from datetime import datetime
from flask import Flask, render_template, redirect, request, abort, send_file, make_response, jsonify
from data import db_session, users_resource, books_resource, genres_resource
from data.users import User
from data.books import Book
from data.genres import Genre
from forms.register import RegisterForm
from forms.login import LoginForm
from forms.add_book import AddBookForm
from forms.edit_book import EditBookForm
from forms.filter_genre import FilterGenre
from flask_login import LoginManager, login_required, logout_user, login_user, current_user
from flask_restful import Api
from waitress import serve

app = Flask(__name__)  # Создаем приложение Flask
api = Api(app)  # API для приложения Flask
login_manager = LoginManager()  # Нужно для того, чтобы можно было авторизовывать пользователей
login_manager.init_app(app)  # Инициализация
app.config.from_pyfile('config.py')  # В файле config.py хранятся все настройки для приложения


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/', methods=['GET', 'POST'])  # Главная страница
def index():
    form = FilterGenre()
    form.genres.choices = ['-'] + list_genres()
    if request.method == 'GET':
        db_sess = db_session.create_session()  # Создаем сессию
        books = db_sess.query(Book).all()  # Получаем все книги
        for book in books:
            book.count_favorites = len(book.user)  # Подсчет у каждой книги кол-ва пользователей, которые добавили в
            # избранное эту книгу и присвоение этого значения атрибуту count_favorites
            book.str_genre = book.genre[0].name  # В шаблоне можно будет удобно получить значение по атрибуту
            # str_genre
        images_books = [str(base64.b64encode(book.image))[2:][:-1] for book in books]
        # images_books - это списочное выражение, в котором происходит превращение потока байт в base64.
        # После срезом удаляются первые 2 символа (b'), и еще срезается самый последний символ (') для того чтобы
        # в html в теге <img> можно было в атрибуте src поместить "data:png;base64, {{ изображение в формате base64 }}"
        # без лишних знаков, иначе изображение не отобразится.
        for book, image in zip(books, images_books):
            book.image = image  # Присваиваем изображения в формате base24, при этом db_sess.commit() не делается.
            # Это нужно для того, чтобы внутри шаблона в цикле можно было удобно обращаться к атрибутам объектов списка
        books_id = []
        if current_user.is_authenticated:  # Если пользователь авторизован
            books_id = [book.id for book in current_user.book]  # Это нужно для проверки внутри шаблона
        return render_template('home.html', title='Главная страница', books=books, books_id=books_id, form=form,
                               url_add='add_to_favorites_book_on_home', url_delete='delete_from_favorites_book_on_home')
    if form.validate_on_submit():
        if form.genres.data == '-':
            return redirect('/')
        url = f"/{form.genres.data}"
        return redirect(url)


@app.route('/<genre_name>', methods=['GET', 'POST'])  # Фильтрация книг по жанру, другая страница
def filter_genre(genre_name):
    form = FilterGenre()
    form.genres.choices = ['-'] + list_genres()
    if request.method == 'GET':
        db_sess = db_session.create_session()  # Создаем сессию
        books = db_sess.query(Book).all()  # Получаем все книги
        for book in books:
            book.count_favorites = len(book.user)  # Подсчет у каждой книги кол-ва пользователей, которые добавили в
            # избранное эту книгу и присвоение этого значения атрибуту count_favorites
            book.str_genre = book.genre[0].name  # В шаблоне можно будет удобно получить значение по атрибуту
            # str_genre
        images_books = [str(base64.b64encode(book.image))[2:][:-1] for book in books]
        # images_books - это списочное выражение, в котором происходит превращение потока байт в base24.
        # После срезом удаляются первые 2 символа (b'), и еще срезается самый последний символ (') для того чтобы
        # в html в теге <img> можно было в атрибуте src поместить "data:png;base64, {{ изображение в формате base24 }}"
        # без лишних знаков, иначе изображение не отобразится.
        for book, image in zip(books, images_books):
            book.image = image  # Присваиваем изображения в формате base24, при этом db_sess.commit() не делается.
            # Это нужно для того, чтобы внутри шаблона в цикле можно было удобно обращаться к атрибутам объектов списка
        books_id = []
        if current_user.is_authenticated:  # Если пользователь авторизован
            books_id = [book.id for book in current_user.book]  # Это нужно для проверки внутри шаблона
        filter_books = []  # Список книг, имеющих такой же жанр как и genre_name
        for book in books:
            if book.str_genre == genre_name:  # Если жанр книги равен значению genre_name
                filter_books.append(book)
        return render_template('home.html', title='Главная страница', books=filter_books, books_id=books_id, form=form,
                               url_add=f"add_to_favorites_book_filter_books/{genre_name}",
                               url_delete=f"delete_from_favorites_book_filter_books/{genre_name}")
    if form.validate_on_submit():
        if form.genres.data == '-':
            return redirect('/')
        url = f"/{form.genres.data}"
        return redirect(url)


@app.route('/register', methods=['GET', 'POST'])  # Страница регистрации
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        check_user = db_sess.query(User).filter(User.login == form.login.data).first()
        if check_user:
            return render_template('register.html', title='Регистрация', form=form,
                                   message='Такой пользователь уже существует')
        new_user = User()
        new_user.login = form.login.data
        new_user.set_password(form.password.data)  # Установка захэшированного пароля
        new_user.is_admin = False  # Зарегистрировался обычный пользователь
        db_sess.add(new_user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])  # Страница авторизации
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        check_user = db_sess.query(User).filter(User.login == form.login.data).first()
        if check_user and check_user.check_password(form.password.data) and check_user.is_admin is form.is_admin.data:
            login_user(check_user)  # Логиним пользователя
            return redirect('/')
        return render_template('login.html', title='Авторизация', form=form,
                               message='Неправильный логин или пароль')
    return render_template('login.html', title='Авторизация', form=form)


def list_genres():  # Вспомогательная функция, которая загружает жанры (нужная для подзаполнения форм)
    db_sess = db_session.create_session()
    genres = db_sess.query(Genre).all()
    genres = [genre.name for genre in genres]
    return genres


@app.route('/add_book', methods=['GET', 'POST'])  # Страница добавления книги (только для админа)
@login_required  # Для авторизованных
def add_book():
    form = AddBookForm()
    form.genre.choices = list_genres()  # Подзаполняем форму
    if request.method == 'GET':
        db_sess = db_session.create_session()
        check_user = db_sess.query(User).filter(User.id == current_user.id).first()
        if not check_user.is_admin:
            abort(403)  # Отказано в доступе, так как пользователь не администратор
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        check_user = db_sess.query(User).filter(User.id == current_user.id).first()
        if not check_user.is_admin:
            abort(403)  # На всякий случай делаем еще одну проверку
        else:
            new_book = Book()
            new_book.title = form.title.data
            new_book.description = form.description.data
            new_book.genre.append(db_sess.query(Genre).filter(Genre.name == form.genre.data).first())
            new_book.image = form.image.data.read()  # Получаем из формы файл и сразу его считываем
            new_book.pdf_file = form.pdf_file.data.read()
            db_sess.add(new_book)
            db_sess.commit()
            return redirect('/')
    return render_template('add_book.html', title='Добавление книги', form=form)


@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])  # Страница редактирования книги (только для админа)
@login_required
def edit_book(book_id):
    form = EditBookForm()
    form.genre.choices = list_genres()  # Подзаполняем форму
    if request.method == 'GET':
        db_sess = db_session.create_session()
        check_user = db_sess.query(User).filter(User.id == current_user.id).first()
        if not check_user.is_admin:
            abort(403)  # Отказано в доступе, так как пользователь не администратор
        check_book = db_sess.query(Book).filter(Book.id == book_id).first()
        if not check_book:
            abort(404)  # Книга не найдена
        else:  # Подзаполняем форму
            form.title.data = check_book.title
            form.description.data = check_book.description
            form.genre.data = check_book.genre[0].name
            # Файлы можно не загружать, так как это будет бессмысленно из-за того, что они пропадут внутри условия
            # if form.validate_on_submit() и еще из-за того, что FileField будет помечен как "Файл не выбран"
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        check_user = db_sess.query(User).filter(User.id == current_user.id).first()
        if not check_user.is_admin:
            abort(403)  # Отказано в доступе, так как пользователь не администратор
        check_book = db_sess.query(Book).filter(Book.id == book_id).first()
        if not check_book:
            abort(404)  # Книга не найдена
        # Еще раз сделали проверку на всякий случай
        else:
            check_book.title = form.title.data
            check_book.description = form.description.data
            check_book.genre.clear()  # Очищаем список жанров одной книги, чтобы не было повторов
            check_book.genre.append(db_sess.query(Genre).filter(Genre.name == form.genre.data).first())
            file_image = form.image.data.read()  # Предварительно надо присвоить переменной, иначе позже исчезнет
            file_pdf = form.pdf_file.data.read()
            if len(file_image) != 0:  # Если поток байт не пустой, то тогда загрузим новую картинку
                check_book.image = file_image
            if len(file_pdf) != 0:
                check_book.pdf_file = file_pdf
            check_book.modified_date = datetime.now()
            db_sess.commit()
            return redirect('/')
    return render_template('edit_book.html', title='Редактирование книги', form=form)


@app.route('/delete_book/<int:book_id>')  # Удаление книги (только для админа), без страницы
@login_required
def delete_book(book_id):
    db_sess = db_session.create_session()
    check_user = db_sess.query(User).filter(User.id == current_user.id).first()
    if not check_user.is_admin:
        abort(403)  # Отказано в доступе, так как пользователь не администратор
    check_book = db_sess.query(Book).filter(Book.id == book_id).first()
    if not check_book:
        abort(404)  # Такой книги нет
    else:
        db_sess.delete(check_book)
        db_sess.commit()
    return redirect('/')


@app.route('/info_about_book/<int:book_id>')  # Страница с информацией о книге (всем)
def info_about_book(book_id):
    db_sess = db_session.create_session()
    check_book = db_sess.query(Book).filter(Book.id == book_id).first()
    check_book.count_favorites = len(check_book.user)
    check_book.str_genre = check_book.genre[0].name  # В шаблоне можно будет удобно получить значение по атрибуту
    # str_genre
    if not check_book:
        abort(404)
    check_book.image = str(base64.b64encode(check_book.image))[2:][:-1]
    return render_template('info_about_book.html', title='Информация о книге', book=check_book)


@app.route('/download_book/<int:book_id>')  # Загрузка книги (всем)
def download_book(book_id):
    db_sess = db_session.create_session()
    check_book = db_sess.query(Book).filter(Book.id == book_id).first()
    if not check_book:
        abort(404)
    else:
        pdf_file = BytesIO(check_book.pdf_file)  # Преобразуем поток байт в двоичный файл
        filename = check_book.title + '.pdf'  # Создаем имя книги, на основе его title
        return send_file(pdf_file, download_name=filename, as_attachment=True)


@app.route('/read_book/<int:book_id>')  # Чтение онлайн книги (всем)
def read_book(book_id):
    db_sess = db_session.create_session()
    check_book = db_sess.query(Book).filter(Book.id == book_id).first()
    if not check_book:
        abort(404)
    else:
        pdf_file = BytesIO(check_book.pdf_file)  # Преобразуем поток байт в двоичный файл
        filename = check_book.title + '.pdf'  # Создаем имя книги, на основе его title
        return send_file(pdf_file, download_name=filename)


@app.route('/add_to_favorites_book_on_home/<int:book_id>')  # На главной странице добавляем
@login_required
def add_to_favorites_book_on_home(book_id):
    add_to_favorites_book(book_id)
    return redirect('/')


@app.route('/delete_from_favorites_book_on_home/<int:book_id>')  # На главной странице удаляем
@login_required
def delete_from_favorites_book_on_home(book_id):
    delete_from_favorites_book(book_id)
    return redirect('/')


@app.route('/delete_from_favorites_book_on_favorites/<int:book_id>')  # На странице избранных книг удаляем
@login_required
def delete_from_favorites_book_on_favorites(book_id):
    delete_from_favorites_book(book_id)
    return redirect('/selected_books')


@app.route('/delete_from_favorites_book_filter_books/<genre_name>/<int:book_id>')  # На странице отфильтрованных
@login_required
def delete_from_favorites_book_on_filter_books(genre_name, book_id):
    delete_from_favorites_book(book_id)
    return redirect(f"/{genre_name}")


@app.route('/add_to_favorites_book_filter_books/<genre_name>/<int:book_id>')  # На странице отфильтрованных
@login_required
def add_to_favorites_book_on_filter_books(genre_name, book_id):
    add_to_favorites_book(book_id)
    return redirect(f"/{genre_name}")


def add_to_favorites_book(book_id):  # Вспомогательная функция для добавления в избранное книг
    db_sess = db_session.create_session()
    check_book = db_sess.query(Book).filter(Book.id == book_id).first()
    if not check_book:
        abort(404)  # Не найдена книга, которую хотят добавить в избранное
    books_id = [book.id for book in current_user.book]  # Список с id всех книг авторизованного пользователя
    if check_book.id in books_id:
        abort(400)  # Эта книга уже в избранном у пользователя
    book = Book(id=check_book.id, title=check_book.title, description=check_book.description,
                created_date=check_book.created_date, modified_date=check_book.modified_date,
                image=check_book.image, pdf_file=check_book.pdf_file)
    current_user.book.append(book)  # Добавили в избранное авторизованному пользователю книгу
    db_sess.merge(current_user)  # Сообщаем сессии, что пользователь изменен
    db_sess.commit()  # Сохраняем в базу данных


def delete_from_favorites_book(book_id):  # Вспомогательная функция для удаления из избранного книг
    db_sess = db_session.create_session()
    check_book = db_sess.query(Book).filter(Book.id == book_id).first()
    if not check_book:
        abort(404)  # Не найдена книга, которую хотят удалить из избранного
    books_id = [book.id for book in current_user.book]  # Список с id всех книг авторизованного пользователя
    if check_book.id not in books_id:
        abort(400)  # Пользователь не может удалить книгу, которой у него нет в избранном
    index_book = books_id.index(check_book.id)
    del current_user.book[index_book]  # Удаляем книгу по индексу из избранного
    db_sess.merge(current_user)
    db_sess.commit()


@app.route('/selected_books')  # Страница, индивидуальная для каждого зарегистрированного пользователя
@login_required  # Это страница избранных книг зарегистрированного пользователя
def selected_books():
    books = current_user.book  # Книги авторизованного пользователя
    books_id = [book.id for book in current_user.book]  # Нужно для проверки в шаблоне
    images_books = [str(base64.b64encode(book.image))[2:][:-1] for book in books]
    for book in books:
        book.count_favorites = len(book.user)
        book.str_genre = book.genre[0].name
    for book, image in zip(books, images_books):
        book.image = image
    return render_template('selected_books.html', title='Избранные книги', books=books, books_id=books_id)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


def main():
    db_session.global_init('db/library.sqlite')
    api.add_resource(users_resource.UserResource, '/api/users/<int:user_id>')  # Добавляем api ресурсы
    api.add_resource(users_resource.UserListResource, '/api/users')
    api.add_resource(books_resource.BookResource, '/api/books/<int:book_id>')
    api.add_resource(books_resource.BookListResource, '/api/books')
    api.add_resource(genres_resource.GenreResource, '/api/genres/<int:genre_id>')
    api.add_resource(genres_resource.GenreListResource, '/api/genres')
    port = int(environ.get("PORT", 5000))
    serve(app, host='0.0.0.0', port=port)  # Для того, чтобы каждому пользователю создавался свой экземпляр Flask
    # приложения и сервер работал бы асинхронно


if __name__ == '__main__':
    main()
