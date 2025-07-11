"""
Диалог для добавления тренировок для конкретного клиента

TODO:
- Внести проверку на существование клиента в базе данных/получение id клиента
- Внести сохранение новых тренировок в базу данных
- Использование pydentic для сущности тренировки
"""

from typing import Optional
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

def generate_workouts_result_msg(data: dict) -> str:
    """Генерирует сообщение с результатами добавления тренировок"""
    try:
        client = Client(**data)
        return client.generate_summary()
    except ValueError as e:
        return f"❌ Ошибка создания отчета: {e}"


@router.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    """
    Обработчик команды /start - очищает состояние и показывает главное меню
    """
    await state.clear()
    await message.answer("Привет! Это бот для управления тренировками.\nИспользуй /add_workouts для добавления тренировок клиенту.")


@router.message(Command("add_workouts"))
async def add_workouts(message: types.Message, state: FSMContext):
    """
    Стартовое состояние
    """
    await state.clear()
    await message.answer("Привет! Сейчас я помогу добавить тренировки для клиента.\nЕсли передумаешь в процессе, то нажми /cancel")
    await state.set_state(AddWorkoutStates.client_name)
    await message.answer("Введи имя клиента")


@router.message(AddWorkoutStates.client_name)
async def set_client_name(message: types.Message, state: FSMContext):
    """
    Получение имени клиента
    """
    try:
        client_data = Client(client_name=message.text, workouts_count=1, workouts=[])
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
    try:
        workouts_count = int(message.text)
        if workouts_count < 1 or workouts_count > 100:
            raise ValueError("Количество тренировок должно быть от 1 до 100")
    except ValueError:
        await message.answer("Количество тренировок может быть только числом")
        return

    await state.update_data(workouts_count=workouts_count, workouts=[])
    await message.answer("Введи описание тренировки")
    await state.set_state(AddWorkoutStates.workout_description)


@router.message(AddWorkoutStates.workout_description)
async def set_workout_description(message: types.Message, state: FSMContext):
    """
    Ввод описания тренировки
    """
    try:
        workout = Workout(description=message.text, exercises=[])
    except ValueError as e:
        await message.answer(str(e))
        return

    data = await state.get_data()
    workouts = data.get("workouts", [])
    workouts.append(workout.model_dump())
    await state.update_data(workouts=workouts)
    await message.answer("Введи количество упражнений в тренировке")
    await state.set_state(AddWorkoutStates.exercises_count)


@router.message(AddWorkoutStates.exercises_count)
async def set_exercise_count(message: types.Message, state: FSMContext):
    try:
        exercise_count = int(message.text)
        if exercise_count < 1 or exercise_count > 20:
            raise ValueError("Количество упражнений должно быть от 1 до 20")
    except ValueError:
        await message.answer("Количество упражнений может быть только числом")
        return

    data = await state.get_data()
    workouts = data["workouts"]
    workouts[-1]["exercises_count"] = exercise_count
    await state.update_data(workouts=workouts)
    await message.answer("Введи название упражнения")
    await state.set_state(AddWorkoutStates.exercise_name)


@router.message(AddWorkoutStates.exercise_name)
async def set_exercise_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    workouts = data["workouts"]
    
    # Сохраняем временные данные для создания Exercise
    await state.update_data(temp_exercise_name=message.text.strip())
    await message.answer("Введи описание упражнения")
    await state.set_state(AddWorkoutStates.exercise_description)


@router.message(AddWorkoutStates.exercise_description)
async def set_exercise_description(message: types.Message, state: FSMContext):
    await state.update_data(temp_exercise_description=message.text.strip())
    await message.answer("Введи количество повторений")
    await state.set_state(AddWorkoutStates.repetitions)


@router.message(AddWorkoutStates.repetitions)
async def set_repetitions(message: types.Message, state: FSMContext):
    try:
        repetitions = int(message.text)
        if repetitions < 1 or repetitions > 999:
            raise ValueError("Количество повторений должно быть от 1 до 999")
    except ValueError:
        await message.answer("Количество повторений может быть только числом")
        return

    await state.update_data(temp_exercise_repetitions=repetitions)
    await message.answer("Введи вес упражнения")
    await state.set_state(AddWorkoutStates.weight)


# Вспомогательные функции для set_weight
async def _validate_weight(text: str) -> Optional[int]:
    """Валидирует вес"""
    try:
        weight = int(text)
        return weight if 0 <= weight <= 1000 else None
    except ValueError:
        return None

async def _create_exercise_from_state(state: FSMContext, weight: int) -> Optional[Exercise]:
    """Создает упражнение из данных состояния"""
    try:
        data = await state.get_data()
        return Exercise(
            name=data["temp_exercise_name"],
            description=data["temp_exercise_description"],
            repetitions=data["temp_exercise_repetitions"],
            weight=weight
        )
    except (ValueError, KeyError):
        return None

async def _add_exercise_and_update_counters(state: FSMContext, exercise: Exercise) -> None:
    """Добавляет упражнение и обновляет счетчики"""
    data = await state.get_data()
    workouts = data["workouts"]
    
    # Добавляем упражнение
    exercises = workouts[-1].get("exercises", [])
    exercises.append(exercise.model_dump())
    workouts[-1]["exercises"] = exercises
    
    # Обновляем счетчик
    workouts[-1]["exercises_count"] -= 1
    
    await state.update_data(workouts=workouts)

async def _clear_temp_data(state: FSMContext) -> None:
    """Очищает временные данные упражнения"""
    await state.update_data(
        temp_exercise_name=None,
        temp_exercise_description=None,
        temp_exercise_repetitions=None
    )

async def _finalize_workout(state: FSMContext) -> None:
    """Завершает текущую тренировку"""
    data = await state.get_data()
    workouts = data["workouts"]
    workouts[-1].pop("exercises_count", None)
    
    current_workouts_count = data["workouts_count"] - 1
    await state.update_data(
        workouts=workouts,
        workouts_count=current_workouts_count
    )

async def _complete_all_workouts(state: FSMContext, message: types.Message) -> None:
    """Завершает все тренировки и показывает результат"""
    data = await state.get_data()
    await state.update_data(workouts_count=len(data["workouts"]))
    await message.answer("Все тренировки добавлены")
    
    result_msg = generate_workouts_result_msg(await state.get_data())
    await message.answer(result_msg)
    await state.clear()

async def _proceed_to_next_step(state: FSMContext, message: types.Message) -> None:
    """Определяет и выполняет следующий шаг"""
    data = await state.get_data()
    workouts = data["workouts"]
    
    # Проверяем упражнения
    exercises_count = workouts[-1]["exercises_count"]
    if exercises_count > 0:
        await message.answer(f"Осталось упражнений: {exercises_count}. Введи название следующего")
        await state.set_state(AddWorkoutStates.exercise_name)
        return
    
    # Завершаем тренировку
    await _finalize_workout(state)
    
    # Проверяем тренировки
    updated_data = await state.get_data()
    if updated_data["workouts_count"] > 0:
        await message.answer(f"Осталось тренировок: {updated_data['workouts_count']}. Введи описание следующей")
        await state.set_state(AddWorkoutStates.workout_description)
    else:
        await _complete_all_workouts(state, message)

@router.message(AddWorkoutStates.weight)
async def set_weight(message: types.Message, state: FSMContext):
    """Обрабатывает ввод веса упражнения"""
    # Валидация веса
    weight = await _validate_weight(message.text)
    if weight is None:
        await message.answer("Вес может быть только числом от 0 до 1000")
        return
    
    # Создание упражнения
    exercise = await _create_exercise_from_state(state, weight)
    if exercise is None:
        await message.answer("Ошибка создания упражнения")
        return
    
    # Обновление данных и переход к следующему шагу
    await _add_exercise_and_update_counters(state, exercise)
    await _clear_temp_data(state)
    await _proceed_to_next_step(state, message)


@router.message(Command("cancel"))
async def cancel_adding(message: types.Message, state: FSMContext):
    await message.answer("Отмена добавления тренировок")
    await state.clear()