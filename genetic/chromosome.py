from dataclasses import dataclass
from typing import Dict, Any
import numpy as np

@dataclass
class RobotGenes:
    """Класс для хранения генов робота"""
    health: float
    speed: float
    damage: float
    aggression: float

    @classmethod
    def from_robot(cls, robot: 'Robot') -> 'RobotGenes':
        """Создание генов из существующего робота"""
        return cls(
            health=robot.health,
            speed=robot.speed,
            damage=robot.damage,
            aggression=0.5  # Начальное значение агрессии
        )

    def mutate(self, mutation_rate: float = 0.1) -> None:
        """Мутация генов"""
        for field in self.__dataclass_fields__:
            if np.random.random() < mutation_rate:
                current_value = getattr(self, field)
                # Мутация в пределах ±20% от текущего значения
                mutation = np.random.uniform(-0.2, 0.2) * current_value
                new_value = current_value + mutation
                # Убедимся, что значение положительное
                setattr(self, field, max(0.1, new_value))

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для сохранения"""
        return {
            'health': self.health,
            'speed': self.speed,
            'damage': self.damage,
            'aggression': self.aggression
        }
