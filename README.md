## Описание
Социальная сеть, где пользователи могут отслеживать посты любимых авторов и оставлять свои комментарии, а также делиться своими постами и добавлять к ним картинки.
## Разверните проект на своём компьютере:
На своём компьютере в директории с проектами создайте папку для проекта YaNews.
Склонируйте проект Blogicum из репозитория: 
```
git clone https://github.com/alextriano/django_sprint4.git
```
Создайте виртуальное окружение:
```
python -m venv venv
```
Запустите виртуальное окружение и установите зависимости из файла requirements.txt: 
```
pip install -r requirements.txt
```
Миграции уже созданы, выполните их: 
```
python manage.py migrate
```
Cоздайте суперпользователя: 
```
python manage.py createsuperuser
```
Запустите проект:
```
python manage.py runserver
```
