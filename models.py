from typing import List
from pydantic import BaseModel, Field

class Exercise(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Название упражнения")
    description: str = Field(..., min_length=1, max_length=500, description="Описание упражнения и техники выполнения")
    repetitions: int = Field(..., ge=1, le=999, description="Количество повторений в упражнении")
    weight: int = Field(..., ge=0, le=1000, description="Вес в упражнении (в кг)")

    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True
    }

class Workout(BaseModel):
    description: str = Field(..., min_length=1, max_length=300, description="Описание тренировки")
    exercises: List[Exercise] = Field(default_factory=list, description="Список упражнений")

    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True
    }

class Client(BaseModel):
    client_name: str = Field(..., min_length=1, max_length=100, description="Имя клиента")
    workouts_count: int = Field(..., ge=1, le=100, description="Количество тренировок")
    workouts: List[Workout] = Field(default_factory=list, description="Список тренировок")

    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True
    }
    
    def generate_summary(self) -> str:
        """Генерирует краткий отчет о тренировках клиента"""
        lines = [
            "✅ Добавлены тренировки:",
            "",
            f"👤 Клиент: {self.client_name}",
            f"📊 Тренировок: {self.workouts_count}",
            ""
        ]
        
        for i, workout in enumerate(self.workouts, 1):
            lines.extend([
                f"🏆 Тренировка {i}",
                f"📝 {workout.description}",
                f"💪 Упражнений: {len(workout.exercises)}",
                ""
            ])
            
            for j, exercise in enumerate(workout.exercises, 1):
                lines.extend([
                    f"  🎯 {j}. {exercise.name}",
                    f"  📖 {exercise.description}",
                    f"  🔄 {exercise.repetitions} повторений",
                    f"  ⚖️ {exercise.weight} кг",
                    ""
                ])
        
        return "\n".join(lines)
