![workflow](https://github.com/pmmakovk/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)
# foodgram

Проект Foodgram.\
«Продуктовый помощник»: сайт, на котором пользователи будут публиковать рецепты,
добавлять чужие рецепты в избранное и подписываться на публикации других авторов.
Сервис «Список покупок» позволит пользователям создавать список продуктов,
которые нужно купить для приготовления выбранных блюд.

Проект доступен по адресу http://158.160.8.13, доступ к админке admin@admin.ru;Admin1234!


## Технологии
- [Django] - Бэкэнд фреймворк
- [Django Rest Framework] - Фрэймворк для создания API на основе Django
- [Djoser] - Библиотека для авторизации
- [Django Filter] - Библиотека для фильтрации данных
- [Pillow] - Библиотека для обработки изображений
- [Reportlab] - Библиотека для создания PDF документов
- [Docker] - ПО для развертывания в контейнере
- [Reactjs] - Фронтэнд фреймворк
- [Gunicorn] - WSGI веб-сервер
- [Postgresql] - База данных
- [Nginx] - HTTP Веб-сервер

## Установка

### Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:pmmakovk/foodgram-project-react.git
```
```
cd foodgram-project-react
```
### Cоздать и активировать виртуальное окружение:
```
python -m venv venv
```
```
. venv/Scripts/activate
```
### Установить зависимости из файла requirements.txt:
```
python -m pip install --upgrade pip
```
```
pip install -r backend/foodgram_backend/requirements.txt
```
### Наполнить .env файл
```
cd infra

DB_ENGINE=<...> # указываем, что работаем с postgresql
DB_NAME=<...> # имя базы данных
POSTGRES_USER=<...> # логин для подключения к базе данных
POSTGRES_PASSWORD=<...> # пароль для подключения к БД (установите свой)
DB_HOST=<...> # название сервиса (контейнера)
DB_PORT=<...> # порт для подключения к БД
SECRET_KEY=<...>	# ключ для settings.py
```
### Перейти в папку с docker-compose.yml и собрать контейнеры:
```
cd infra
docker-compose up --build
```
### Создать миграции, провести их, собрать статику, создать суперюпользователя
```
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --no-input
docker-compose exec backend python manage.py createsuperuser
```
### Наполнить БД ингредиентами из CSV файла (при необходимости)
```
docker-compose exec backend python manage.py csv_manager
docker-compose exec backend python manage.py tags_manager
```
## Примеры запросов к API и ответов
### Доступно на http://localhost/api/docs/

## Разработчик - [Маковкин Павел](https://github.com/pmmakovk) ##