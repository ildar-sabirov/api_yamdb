import re

from django.core.exceptions import ValidationError

INVALID_USERNAME = 'Недопустимо использовать имя пользователя: {username}'
INCORRECT_USERNAME = ('Имя пользователя содержит недопустимые символы: '
                      '{invalid_chars}')


def validate_username(username):
    if username.lower() == 'me':
        raise ValidationError(INVALID_USERNAME.format(username=username))
    invalid_chars = re.findall(r'[^\w.@+-]', username)
    if invalid_chars:
        raise ValidationError(
            INCORRECT_USERNAME.format(invalid_chars=', '.join(invalid_chars))
        )
    return username
