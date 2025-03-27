from aiogram import Router, F, types
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

router = Router()

class AddTraining(StatesGroup):
    enter_count = State()
    enter_training_name = State()
    enter_training_description = State()
    enter_exercise_count = State()
    enter_exercise_name = State()
    enter_exercise_description = State()
    enter_exercise_sets = State()
    enter_exercise_weight = State()

@router.message(commands=["add_trainings"])
async def start_add_trainings(message: Message, state: FSMContext):
    await message.answer("Сколько тренировок нужно добавить?")
    await state.set_state(AddTraining.enter_count)

@router.message(AddTraining.enter_count, F.text.isdigit())
async def set_training_count(message: Message, state: FSMContext):
    count = int(message.text)
    if count <= 0:
        await message.answer("Количество должно быть больше нуля. Попробуйте еще раз.")
        return

    await state.update_data(remaining_trainings=count, trainings=[])
    await message.answer("Введите название первой тренировки:")
    await state.set_state(AddTraining.enter_training_name)

@router.message(AddTraining.enter_training_name)
async def enter_training_name(message: Message, state: FSMContext):
    await state.update_data(current_training={"name": message.text})
    await message.answer("Введите описание тренировки:")
    await state.set_state(AddTraining.enter_training_description)

@router.message(AddTraining.enter_training_description)
async def enter_training_description(message: Message, state: FSMContext):
    data = await state.get_data()
    current_training = data["current_training"]
    current_training["description"] = message.text
    current_training["exercises"] = []

    await state.update_data(current_training=current_training)
    await message.answer("Сколько упражнений в этой тренировке?")
    await state.set_state(AddTraining.enter_exercise_count)

@router.message(AddTraining.enter_exercise_count, F.text.isdigit())
async def set_exercise_count(message: Message, state: FSMContext):
    count = int(message.text)
    if count <= 0:
        await message.answer("Количество упражнений должно быть больше нуля. Попробуйте еще раз.")
        return

    await state.update_data(remaining_exercises=count)
    await message.answer("Введите название первого упражнения:")
    await state.set_state(AddTraining.enter_exercise_name)

@router.message(AddTraining.enter_exercise_name)
async def enter_exercise_name(message: Message, state: FSMContext):
    await state.update_data(current_exercise={"name": message.text})
    await message.answer("Введите описание упражнения:")
    await state.set_state(AddTraining.enter_exercise_description)

@router.message(AddTraining.enter_exercise_description)
async def enter_exercise_description(message: Message, state: FSMContext):
    data = await state.get_data()
    current_exercise = data["current_exercise"]
    current_exercise["description"] = message.text

    await state.update_data(current_exercise=current_exercise)
    await message.answer("Введите количество подходов:")
    await state.set_state(AddTraining.enter_exercise_sets)

@router.message(AddTraining.enter_exercise_sets, F.text.isdigit())
async def enter_exercise_sets(message: Message, state: FSMContext):
    sets = int(message.text)
    if sets <= 0:
        await message.answer("Количество подходов должно быть больше нуля. Попробуйте еще раз.")
        return

    data = await state.get_data()
    current_exercise = data["current_exercise"]
    current_exercise["sets"] = sets

    await state.update_data(current_exercise=current_exercise)
    await message.answer("Введите вес для упражнения:")
    await state.set_state(AddTraining.enter_exercise_weight)

@router.message(AddTraining.enter_exercise_weight, F.text.isdigit())
async def enter_exercise_weight(message: Message, state: FSMContext):
    weight = int(message.text)
    if weight < 0:
        await message.answer("Вес не может быть отрицательным. Попробуйте еще раз.")
        return

    data = await state.get_data()
    current_exercise = data["current_exercise"]
    current_exercise["weight"] = weight

    # Добавление упражнения в список
    data["current_training"]["exercises"].append(current_exercise)
    remaining_exercises = data["remaining_exercises"] - 1

    if remaining_exercises > 0:
        await state.update_data(remaining_exercises=remaining_exercises, current_exercise={})
        await message.answer(f"Осталось добавить {remaining_exercises} упражнений. Введите название следующего упражнения:")
        await state.set_state(AddTraining.enter_exercise_name)
    else:
        data["trainings"].append(data["current_training"])
        remaining_trainings = data["remaining_trainings"] - 1

        if remaining_trainings > 0:
            await state.update_data(remaining_trainings=remaining_trainings, current_training={})
            await message.answer(f"Осталось добавить {remaining_trainings} тренировок. Введите название следующей тренировки:")
            await state.set_state(AddTraining.enter_training_name)
        else:
            await message.answer("Все тренировки успешно добавлены!")
            await state.clear()