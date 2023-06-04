import re

from django.core.exceptions import ValidationError

INVALID_USERNAME = 'Недопустимо использовать имя пользователя: {username}'
INCORRECT_USERNAME = 'Имя пользователя содержит недопустимые символы'


def validate_username(username):
    if username == 'me':
        raise ValidationError(INVALID_USERNAME.format(username=username))
    invalid_matches = list(set(re.findall(r'[^\w.@+-]', username)))
    if invalid_matches:
        raise ValidationError(
            f'{INCORRECT_USERNAME}: {"".join(invalid_matches)}'
        )
    return username
