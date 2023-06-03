# О проекте:

Проект YaMDb собирает отзывы пользователей на произведения.

Произведения делятся на категории, такие как «Книги», «Фильмы», «Музыка». Список категорий может быть расширен.
Произведению может быть присвоен жанр из списка предустановленных.
Добавлять произведения, категории и жанры может только администратор.

Пользователи оставляют к произведениям текстовые отзывы и ставят произведению оценку в диапазоне от одного до десяти; из пользовательских оценок формируется рейтинг.
На одно произведение пользователь может оставить только один отзыв. Пользователи так же могут оставлять комментарии к отзывам.

Добавлять отзывы, комментарии и ставить оценки могут только аутентифицированные пользователи.

## Технологии:

+ Django
+ djangorestframework
+ JSON Web Token Authentication
+ SQLite

## Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/ildar-sabirov/api_yamdb.git
```

```
cd api_final_yatube
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

* Если у вас Linux/macOS

    ```
    source env/bin/activate
    ```

* Если у вас windows

    ```
    source env/scripts/activate
    ```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

Для заполнения базы данных тестовыми данными:

```
python3 manage.py importcsv
```

## Справка:

Проект API_YAMDB предоставляет доступ к следующим ендпойнтам:

1. `api/v1/auth/signup/`
2. `api/v1/auth/token/`
3. `api/v1/categories/`
4. `api/v1/genres/`
5. `api/v1/titles/`
6. `api/v1/titles/{title_id}/reviews/`
7. `api/v1/titles/{title_id}/reviews/{review_id}/comments/`
8. `api/v1/users/`
9. `api/v1/users/me/`

Эндпойнты `signup` `token` доступны всем пользователям, предоставляют возможность зарегистрироваться и получить/обновить токен.

Эндпойнт `users` доступен только Администраторам, `users/me` Только зарегистрированным пользователям.

Остальные эндпойнты доступны для чтения всем пользователям.
Изменения в `categories`, `genres`, `titles` могут вносить только администраторы.

Добавлять записи в эндпойнты `reviews` и `comments` могут только авторизированные пользователи, а изменить записи их авторы или персонал (Администраторы, Модераторы).

Документация доступна по адресу `redoc/`

## Примеры запросов к API

### `Post` auth/signup/

*email, username обязательные поля*

```json
{
    "email": "user@example.com",
    "username": "string"
}
```

Ответ:

```json
{
    "email": "user@example.com",
    "username": "string"
}
```

### `Post` auth/token/

*username, confirmation_code обязательные поля*

```json
{
    "username": "string",
    "confirmation_code": "string"
}
```

Ответ:

```json
{
    "token": "string"
}
```

---

### `Get` api/v1/categories/

Вернет список из 5 категорий на страницу.

Ответ:

```json
{
    "count": 0,
    "next": "string",
    "previous": "string",
    "results": [
        {}
    ]
}
```

### `Post` api/v1/categories/

*Только для администраторов*

```json
{
    "name": "string",
    "slug": "string"
}
```

Ответ:

```json
{
    "name": "string",
    "slug": "string"
}
```

---

### `Get` api/v1/genres/

Вернет список из 5 жанров на страницу.

Ответ:

```json
{
    "count": 0,
    "next": "string",
    "previous": "string",
    "results": [
        {}
    ]
}
```

### `Post` api/v1/genres/

*Только для администраторов*

```json
{
    "name": "string",
    "slug": "string"
}
```

Ответ:

```json
{
    "name": "string",
    "slug": "string"
}
```

---
### `Get` api/v1/titles/

Вернет список из 5 произведений на страницу.

Ответ:

```json
{
    "count": 0,
    "next": "string",
    "previous": "string",
    "results": [
        {}
    ]
}
```

### `Post` api/v1/titles/

*Только для администраторов*

```json
{
    "name": "string",
    "year": 0,
    "description": "string",
    "genre": [
        "string"
    ],
    "category": "string"
}
```

Ответ:

```json
{
    "id": 0,
    "name": "string",
    "year": 0,
    "rating": 0,
    "description": "string",
    "genre": [
        {}
    ],
    "category": {
        "name": "string",
        "slug": "string"
    }
 }
```

---
### `Get` api/v1/titles/{title_id}/reviews/

Вернет список из 5 отзывов к произведению на страницу.

Ответ:

```json
{
    "count": 0,
    "next": "string",
    "previous": "string",
    "results": [
        {}
    ]
}
```

### `Post` api/v1/titles/{title_id}/reviews/

*Для зарегистрированных пользователей*

```json
{
    "text": "string",
    "score": 1
}
```

Ответ:

```json
{
    "id": 0,
    "text": "string",
    "author": "string",
    "score": 1,
    "pub_date": "2019-08-24T14:15:22Z"
 }
```

---
### `Get` api/v1/titles/{title_id}/reviews/{review_id}/comments/

Вернет список из 5 комментариев к отзыву на страницу.

Ответ:

```json
{
    "count": 0,
    "next": "string",
    "previous": "string",
    "results": [
        {}
    ]
}
```

### `Post` api/v1/titles/{title_id}/reviews/{review_id}/comments/

*Для зарегистрированных пользователей*

```json
{
    "text": "string",
}
```

Ответ:

```json
{
    "id": 0,
    "text": "string",
    "author": "string",
    "pub_date": "2019-08-24T14:15:22Z"
 }
```

---
### `Get` api/v1/users/

*Только для администраторов*

Вернет список из 5 пользователей на страницу.

Ответ:

```json
{
    "count": 0,
    "next": "string",
    "previous": "string",
    "results": [
        {}
    ]
}
```

### `Post` api/v1/users/

*Только для администраторов*

```json
{
    "username": "string",
    "email": "user@example.com",
    "first_name": "string",
    "last_name": "string",
    "bio": "string",
    "role": "user"
}
```

Ответ:

```json
{
    "username": "string",
    "email": "user@example.com",
    "first_name": "string",
    "last_name": "string",
    "bio": "string",
    "role": "user"
 }
```

---
### `Get` api/v1/users/me/

*Только для зарегистрированных пользователей*

Вернет данные пользователя.

Ответ:

```json
{
    "username": "string",
    "email": "user@example.com",
    "first_name": "string",
    "last_name": "string",
    "bio": "string",
    "role": "user"
}
```

### `Patch` api/v1/users/me/

*Только для зарегистрированных пользователей*

```json
{
    "username": "string",
    "email": "user@example.com",
    "first_name": "string",
    "last_name": "string",
    "bio": "string"
}
```

Ответ:

```json
{
    "username": "string",
    "email": "user@example.com",
    "first_name": "string",
    "last_name": "string",
    "bio": "string",
    "role": "user"
 }
```

---

## О команде разработчиков:

***Ильдар Сабиров*** [ildar-sabirov](https://github.com/ildar-sabirov)

***Анастасия Андреева*** [Comaash](https://github.com/Comaash)

***Арсений Кавтарев*** [Senya120](https://github.com/Senya120)
