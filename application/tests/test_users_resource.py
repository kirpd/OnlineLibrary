from requests import get

print(get('http://127.0.0.1:5000/api/users').json())  # Правильное получение всех пользователей
print(get('http://127.0.0.1:5000/api/users/-20').json())  # Получение одного пользователя: Not found
print(get('http://127.0.0.1:5000/api/users/a').json())  # Получение одного пользователя: Not found
print(get('http://127.0.0.1:5000/api/users/1').json())  # Правильное получение одного пользователя
