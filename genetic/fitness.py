from dataclasses import dataclass
from typing import Dict

@dataclass
class BattleMetrics:
    """Класс для хранения метрик боя"""
    time_alive: float
    enemies_killed: int
    base_damage: float
    damage_taken: float

class FitnessCalculator:
    """Класс для расчета приспособленности"""
    def __init__(self):
        self.weights = {
            'time_alive': 0.2,
            'enemies_killed': 0.3,
            'base_damage': 0.4,
            'damage_taken': 0.1
        }

    def calculate_fitness(self, metrics: BattleMetrics) -> float:
        """Расчет приспособленности на основе метрик"""
        fitness = (
            self.weights['time_alive'] * metrics.time_alive / 100.0 +
            self.weights['enemies_killed'] * metrics.enemies_killed * 10.0 +
            self.weights['base_damage'] * metrics.base_damage / 100.0 -
            self.weights['damage_taken'] * metrics.damage_taken / 100.0
        )
        return max(0, fitness)  # Фитнес не может быть отрицательным
