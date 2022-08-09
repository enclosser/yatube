from django import forms


def validate_not_empty(value):
    if value == '':
        raise forms.ValidationError(
            'Обязательное для заполнения поле.',
            params={'value': value},
        )
