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
from models import Client, Workout, Exercise

# Создаем маршрутизатор
router = Router()

# TODO: добавить проверку существования клиента в базе данных
# def check_if_client_exists(session, client_name: str) -> bool:
#     """ Проверяет существование клиента в базе данных  """
#     сlient = session.query(Client).filter(Client.name == client_name).first()
#     return bool(client)

def generate_workouts_result_msg(data: dict):
    client = Client(**data)
    result = f"Вы добавили следующие тренировки:\n👨🏼 Имя клиента: {client.client_name}\nКоличество тренировок: {client.workouts_count}\n"
    for i, workout in enumerate(client.workouts):
        result += f"🏆 Тренировка {i + 1}\nОписание: {workout.description}\nКоличество упражнений: {len(workout.exercises)}\n"
        for j, exercise in enumerate(workout.exercises):
            result += f"🎗 Упражнение {j + 1}:\nНазвание: {exercise.name}\nОписание: {exercise.description}\nКоличество подходов: {exercise.repetitions}\nВес: {exercise.weight} кг\n"
    return result


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
    try:
        client_data = Client(client_name=client_name, workouts_count=0, workouts=[])
    except ValueError as e:
        await message.answer(str(e))
        return

    # TODO Добавить проверку существования клиента в базе данных

    await state.update_data(**client_data.model_dump())
    await message.answer("Сколько тренировок добавить?")
    await state.set_state(AddWorkoutStates.workouts_count)


@router.message(AddWorkoutStates.workouts_count)
async def set_workouts_count(message: types.Message, state: FSMContext):
    """
    Ввод количества тренировок
    """
    # Проверка нужна здесь, чтобы пользователь получил понятное сообщение,
    # если введёт не число. В pydantic-моделях такая проверка не требуется,
    # так как pydantic сам выбросит ошибку при попытке создать объект с неверным типом.
    if not message.text.isdigit():
        await message.answer("Количество тренировок должно быть числом")
        return

    workouts_count = int(message.text)
    if workouts_count < 1:
        await message.answer("Количество тренировок должно быть больше 0")
        return

    await state.update_data(workouts_count=workouts_count, workouts=[])
    await message.answer("Введи описание тренировки")
    await state.set_state(AddWorkoutStates.workout_description)


@router.message(AddWorkoutStates.workout_description)
async def set_workout_description(message: types.Message, state: FSMContext):
    """
    Ввод описания тренировки
    """
    workout_description = message.text.strip()

    data = await state.get_data()
    workouts = data.get("workouts", [])
    try:
        workout = Workout(description=workout_description, exercises=[])
    except ValueError as e:
        await message.answer(str(e))
        return
    workouts.append(workout.dict())
    await state.update_data(workouts=workouts)
    await message.answer("Введи количество упражнений в тренировке")
    await state.set_state(AddWorkoutStates.exercises_count)


@router.message(AddWorkoutStates.exercises_count)
async def set_exercise_count(message: types.Message, state: FSMContext):
    # Аналогично, эта проверка нужна для пользовательского ввода,
    # чтобы не показывать "сырые" ошибки pydantic.
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
    exercises = workouts[-1].get("exercises", [])
    # временно добавляем пустые поля, заполним далее
    exercises.append({'name': exercise_name, 'description': '', 'repetitions': 1, 'weight': 0.0})
    workouts[-1]["exercises"] = exercises
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
    # Проверка пользовательского ввода для повторений
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
    # Здесь используем try/except для float, чтобы обработать ошибку преобразования
    try:
        weight = float(message.text)
    except ValueError:
        await message.answer("Вес упражнения должен быть числом")
        return
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
        # Удаляем временное поле exercises_count
        workouts[-1].pop("exercises_count", None)
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