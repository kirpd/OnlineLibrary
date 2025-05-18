from requests import get

print(get('http://127.0.0.1:5000/api/books').json())  # Правильное получение всех книг
print(get('http://127.0.0.1:5000/api/books/-20').json())  # Получение одной книги: Not found
print(get('http://127.0.0.1:5000/api/books/a').json())  # Получение одной книги: Not found
print(get('http://127.0.0.1:5000/api/books/1').json())  # Правильное получение всех книг
