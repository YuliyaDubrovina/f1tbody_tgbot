"""
Диалог для добавления тренировок для конкретного клиента

TODO:
- Внести проверку на существование клиента в базе данных/получение id клиента
- Внести сохранение новых тренировок в базу данных
- Использование pydentic для сущности тренировки
"""
import re

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from fsm_states import AddWorkoutStates

# Создаем маршрутизатор
router = Router()

# TODO: добавить проверку существования клиента в базе данных
# def check_if_client_exists(session, client_name: str) -> bool:
#     """ Проверяет существование клиента в базе данных  """
#     сlient = session.query(Client).filter(Client.name == client_name).first()
#     return bool(client)

def generate_workouts_result_msg(data):
    workouts = data["workouts"]
    result = "Вы добавили следующие тренировки:\n"
    result += f"👨🏼 Имя клиента: {data["client_name"]}\n"
    result += f"Количество тренировок: {data["workouts_count"]}\n"
    for i, workout in enumerate(workouts):
        result += f"🏆 Тренировка {i + 1}\n"
        result += f"Описание: {workout["description"]}\n"
        result += f"Количество упражнений: {workout["exercises_count"]}\n"
        for j, exercise in enumerate(workout["exercises"]):
            result += f"🎗 Упражнение {j + 1}:\n"
            result += f"Название: {exercise["name"]}\n"
            result += f"Описание: {exercise["description"]}\n"
            result += f"Количество подходов: {exercise["repetitions"]}\n"
            result += f"Вес: {int(exercise["weight"])} кг\n"

    return result


def is_valid_name(name: str) -> bool:
    """
    Проверяет валидность имени клиента
    - Состоит из букв, пробелов, дефисов (латиница и кириллица)
    - Не пустое
    - Нет лишних символов

    :param name: Имя клиента
    :return: bool
    """
    return bool(re.match(r"^[A-Za-zА-Яа-яЁё\s-]+$", name.strip()))


@router.message(Command("add_workouts"))
async def add_workouts(message: types.Message, state: FSMContext):
    """
    Стартовое состояние
    """
    await message.answer("Привет! Сейчас я помогу добавить тренировки для клиента.\nЕсли передумаешь в процессе, то нажми /cancel")
    await state.set_state(AddWorkoutStates.client_name)
    await message.answer("Введи имя клиента")
    await state.set_state(AddWorkoutStates.client_name)


@router.message(AddWorkoutStates.client_name)
async def set_client_name(message: types.Message, state: FSMContext):
    """
    Получение имени клиента
    """
    client_name = message.text.strip()

    # Проверяем корректность имени
    if not is_valid_name(client_name):
        await message.answer("Имя клиента может состоять только из букв, пробелов, дефисов")
        return

    # TODO Добавить проверку существования клиента в базе данных

    await state.update_data(client_name=client_name)
    await message.answer("Сколько тренировок добавить?")
    await state.set_state(AddWorkoutStates.workouts_count)


@router.message(AddWorkoutStates.workouts_count)
async def set_workouts_count(message: types.Message, state: FSMContext):
    """
    Ввод количества тренировок
    """
    if not message.text.isdigit():
        await message.answer("Количество тренировок должно быть числом")
        return

    workouts_count = int(message.text)
    if workouts_count < 1:
        await message.answer("Количество тренировок должно быть больше 0")
        return

    await state.update_data(workouts_count=workouts_count, workouts= [])
    await message.answer("Введи описание тренировки")
    await state.set_state(AddWorkoutStates.workout_description)


@router.message(AddWorkoutStates.workout_description)
async def set_workout_description(message: types.Message, state: FSMContext):
    """
    Ввод описания тренировки
    """
    workout_description = message.text.strip()

    data = await state.get_data()
    workouts = data["workouts"]
    workouts.append({
        "description": workout_description,
        "exercise_count": 0,
        "exercises": []
    })
    await state.update_data(workouts=workouts)
    await message.answer("Введи количество упражнений в тренировке")
    await state.set_state(AddWorkoutStates.exercises_count)


@router.message(AddWorkoutStates.exercises_count)
async def set_exercise_count(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Количество упражнений должно быть числом")
        return

    exercise_count = int(message.text)
    if exercise_count < 1:
        await message.answer("Количество упражнений должно быть больше 0")
        return

    data = await state.get_data()
    workouts = data["workouts"]
    workouts[-1]["exercises_count"] = exercise_count
    await state.update_data(workouts=workouts)
    await message.answer("Введи название упражнения")
    await state.set_state(AddWorkoutStates.exercise_name)


@router.message(AddWorkoutStates.exercise_name)
async def set_exercise_name(message: types.Message, state: FSMContext):
    exercise_name = message.text.strip()
    data = await state.get_data()
    workouts = data["workouts"]
    workouts[-1]["exercises"].append({'name': exercise_name, 'description': '', 'weight': ''})

    await state.update_data(workouts=workouts)
    await message.answer("Введи описание упражнения")
    await state.set_state(AddWorkoutStates.exercise_description)


@router.message(AddWorkoutStates.exercise_description)
async def set_exercise_description(message: types.Message, state: FSMContext):
    exercise_description = message.text.strip()
    if not exercise_description:
        await message.answer("Описание упражнения не может быть пустым")
        return

    data = await state.get_data()
    workouts = data["workouts"]
    workouts[-1]["exercises"][-1]["description"] = exercise_description
    await state.update_data(workouts=workouts)
    await message.answer("Введи количество повторений")
    await state.set_state(AddWorkoutStates.repetitions)


@router.message(AddWorkoutStates.repetitions)
async def set_repetitions(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Количество повторений должно быть числом")
        return

    repetitions = int(message.text)
    if repetitions < 1:
        await message.answer("Количество повторений должно быть больше 0")
        return

    data = await state.get_data()
    workouts = data["workouts"]
    workouts[-1]["exercises"][-1]["repetitions"] = repetitions
    await state.update_data(workouts=workouts)
    await message.answer("Введи вес упражнения")
    await state.set_state(AddWorkoutStates.weight)

@router.message(AddWorkoutStates.weight)
async def set_weight(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Вес упражнения должно быть числом")
        return

    weight = float(message.text)
    if weight < 0:
        await message.answer("Вес упражнения не может быть отрицательным")
        return

    data = await state.get_data()
    workouts = data["workouts"]
    workouts[-1]["exercises"][-1]["weight"] = weight
    workouts[-1]["exercises_count"] -= 1
    exercises_count = workouts[-1]["exercises_count"]
    await state.update_data(workouts=workouts)

    if exercises_count > 0:
        await message.answer(f"Осталось добавить упражнений: {exercises_count}. Введи название следующего упражнения")
        await state.set_state(AddWorkoutStates.exercise_name)
    else:
        workouts[-1]["exercises_count"] = len(workouts[-1]["exercises"])
        await state.update_data(workouts=workouts)

        current_workouts_count = await state.get_value("workouts_count") - 1
        await state.update_data(workouts_count=current_workouts_count)

        if current_workouts_count > 0:
            await message.answer(f"Осталось добавить тренировок: {current_workouts_count}. Введи описание следующей тренировки")
            await state.set_state(AddWorkoutStates.workout_description)
        else:

            await state.update_data(workouts_count=len(workouts))
            await message.answer("Все тренировки добавлены")
            result_msg = generate_workouts_result_msg(await state.get_data())
            await message.answer(result_msg)
            await state.clear()


@router.message(Command("cancel"))
async def cancel_adding(message: types.Message, state: FSMContext):
    await message.answer("Отмена добавления тренировок")
    await state.clear()