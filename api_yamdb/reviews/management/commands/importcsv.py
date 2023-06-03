import csv

from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404
from reviews.models import (Category, Comment, Genre, Review, Title,
                            TitleGenres, User)

TABLE_PATH = {
    'Category': 'static/data/category.csv',
    'Comment': 'static/data/comments.csv',
    'Genre': 'static/data/genre.csv',
    'Review': 'static/data/review.csv',
    'Title': 'static/data/titles.csv',
    'TitleGenres': 'static/data/genre_title.csv',
    'User': 'static/data/users.csv',
}


class Command(BaseCommand):
    help = "Заполняет базу данных из файлов csv"

    def sucsess_import_message(self, table_name):
        self.stdout.write(
            self.style.SUCCESS(
                f'Данные таблицы {table_name} успешно импортированы'
            )
        )

    def handle(self, *args, **options):
        with open(TABLE_PATH['Genre'], encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            Genre.objects.all().delete()
            for row in reader:
                genre = Genre(
                    id=row[0],
                    name=row[1],
                    slug=row[2])
                genre.save()
        self.sucsess_import_message('Жанры')

        with open(TABLE_PATH['Category'], encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            Category.objects.all().delete()
            for row in reader:
                category = Category(
                    id=row[0],
                    name=row[1],
                    slug=row[2])
                category.save()
        self.sucsess_import_message('Категории')

        with open(TABLE_PATH['Title'], encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            Title.objects.all().delete()
            for row in reader:
                category = get_object_or_404(Category, id=int(row[3]))
                title = Title(
                    id=row[0],
                    name=row[1],
                    year=row[2],
                    category=category)
                title.save()
        self.sucsess_import_message('Произведения')

        with open(TABLE_PATH['TitleGenres'], encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            TitleGenres.objects.all().delete()
            for row in reader:
                title = get_object_or_404(Title, id=row[1])
                genre = get_object_or_404(Genre, id=row[-1])
                title_genre = TitleGenres(
                    id=row[0],
                    title=title,
                    genre=genre)
                title_genre.save()
        self.sucsess_import_message('Произведения-Жанры')

        with open(TABLE_PATH['User'], encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            User.objects.all().delete()
            for row in reader:
                user = User(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    role=row[3],
                    bio=row[4],
                    first_name=row[5],
                    last_name=row[6])
                user.save()
        self.sucsess_import_message('Пользователи')

        with open(TABLE_PATH['Review'], encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            Review.objects.all().delete()
            for row in reader:
                title = get_object_or_404(Title, id=row[1])
                author = get_object_or_404(User, id=row[3])
                review = Review(
                    id=row[0],
                    title=title,
                    text=row[2],
                    author=author,
                    score=row[4],
                    pub_date=row[5])
                review.save()
        self.sucsess_import_message('Отзывы')

        with open(TABLE_PATH['Comment'], encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            Comment.objects.all().delete()
            for row in reader:
                review = get_object_or_404(Review, id=row[1])
                author = get_object_or_404(User, id=row[3])
                comment = Comment(
                    id=row[0],
                    review=review,
                    text=row[2],
                    author=author,
                    pub_date=row[4])
                comment.save()
        self.sucsess_import_message('Комментарии')
