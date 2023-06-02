import re

from django.core.exceptions import ValidationError

INVALID_USERNAME = 'Недопустимый username'
INCORRECT_USERNAME = 'username содержит недопустимые символы'


def validate_username(username):
    if username.lower() == 'me':
        raise ValidationError(INVALID_USERNAME)
    if not username or not bool(re.match(r'^[\w.@+-]+$', username)):
        raise ValidationError(INCORRECT_USERNAME)
    return username
