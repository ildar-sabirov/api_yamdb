# О проекте:

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

## О команде разработчиков:

***Ильдар Сабиров*** [ildar-sabirov](https://github.com/ildar-sabirov)

***Анастасия Андреева*** [Comaash](https://github.com/Comaash)

***Арсений Кавтарев*** [Senya120](https://github.com/Senya120)


## Технологии:

+ Django
+ djangorestframework
+ JSON Web Token Authentication
+ SQLite

### Как запустить проект:

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
