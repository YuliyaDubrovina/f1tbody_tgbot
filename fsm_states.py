from aiogram.fsm.state import State, StatesGroup

# Состояние добавления тренировки для клиента
class AddWorkoutStates(StatesGroup):
    client_name = State()
    workouts_count = State()
    workout_description = State()
    exercises_count = State()
    exercise_name = State()
    exercise_description = State()
    repetitions = State()
    weight = State()