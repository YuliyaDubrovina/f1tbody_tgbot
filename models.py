import re

from pydantic import BaseModel, validatior, ValidationError

class Exercise(BaseModel):
    name: str
    description: str
    repetitions: int
    weight: int

    @validatior('name', 'description')
    def validate_strings(self, value):
        if not value.strip():
            raise ValidationError('Описание не может быть пустым')
        return value

    @validatior('repetitions', 'weight')
    def validate_numbers(self, value):
        if not value.isdigit() and value < 1:
            raise ValidationError('Поле должно быть числом и больше 0')
        return value

class Workout(BaseModel):
    description: str
    exercises: list[Exercise] = []

    @validatior('name', 'description')
    def validate_strings(self, value):
        if not value.strip():
            raise ValidationError('Описание не может быть пустым')
        return value

class Client(BaseModel):
    client_name: str
    workouts_count: int
    workouts: list[Workout] = []

    @validatior('client_name')
    def validate_client_name(self, value):
        if not value.strip():
            raise ValidationError('Имя клиента не может быть пустым')
        if not re.match(r'^[A-Za-zА-Яа-яЁё\s]+$', value):
            raise ValidationError('Имя клиента может состоять только из букв, пробелов и дефисов')
        return value

    @validatior('workouts_count')
    def validate_workouts_count(self, value):
        if not value.isdigit() and value < 1:
            raise ValidationError('Поле должно быть числом и больше 0')
        return value
