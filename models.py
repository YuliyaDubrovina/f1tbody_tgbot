import re
from typing import List
from pydantic import BaseModel, validator, ValidationError

class Exercise(BaseModel):
    name: str
    description: str
    repetitions: int
    weight: int

    @validator('name', 'description')
    def validate_strings(cls, value):
        if not value.strip():
            raise ValueError('Поле не может быть пустым')
        return value

    @validator('repetitions')
    def validate_repetitions(cls, value):
        if value < 1:
            raise ValueError('Количество повторений должно быть больше 0')
        return value

    @validator('weight')
    def validate_weight(cls, value):
        if value < 1:
            raise ValueError('Вес должен быть больше 0')
        return value

class Workout(BaseModel):
    description: str
    exercises: List[Exercise] = []

    @validator('description')
    def validate_description(cls, value):
        if not value.strip():
            raise ValueError('Описание тренировки не может быть пустым')
        return value

class Client(BaseModel):
    client_name: str
    workouts_count: int
    workouts: List[Workout] = []

    @validator('client_name')
    def validate_client_name(cls, value):
        if not value.strip():
            raise ValueError('Имя клиента не может быть пустым')
        if not re.match(r'^[A-Za-zА-Яа-яЁё\s\-]+$', value):
            raise ValueError('Имя клиента может состоять только из букв, пробелов и дефисов')
        return value

    @validator('workouts_count')
    def validate_workouts_count(cls, value):
        if value < 1:
            raise ValueError('Количество тренировок должно быть больше 0')
        return value
