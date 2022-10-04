# foodgram

Проект Foodgram.\
«Продуктовый помощник»: сайт, на котором пользователи будут публиковать рецепты,
добавлять чужие рецепты в избранное и подписываться на публикации других авторов.
Сервис «Список покупок» позволит пользователям создавать список продуктов,
которые нужно купить для приготовления выбранных блюд.


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
cd foodgram-project
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
pip install -r backend/foodgram/requirements.txt
```
### Перейти в папку с docker-compose.yml и собрать контейнеры:
```
cd infra
docker-compose up --build
```

### Наполнить БД ингредиентами из CSV файла (при необходимости)
```
python manage csv_manager
python manage tags_manager
```
## Примеры запросов к API и ответов
### Доступно на http://localhost/api/docs/

## Разработчик - [Маковкин Павел](https://github.com/pmmakovk) ##