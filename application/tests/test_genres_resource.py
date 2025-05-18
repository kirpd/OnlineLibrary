from requests import get

print(get('http://127.0.0.1:5000/api/genres').json())  # Правильное получение всех жанров
print(get('http://127.0.0.1:5000/api/genres/-20').json())  # Получение одного жанра: Not found
print(get('http://127.0.0.1:5000/api/genres/a').json())  # Получение одного жанра: Not found
print(get('http://127.0.0.1:5000/api/genres/1').json())  # Правильное получение одного жанра
