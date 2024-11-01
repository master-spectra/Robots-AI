from abc import ABC
from typing import Dict, Any
from .chromosome import RobotGenes

class GeneticRobot(ABC):
    """Базовый класс для роботов с генетическими свойствами"""
    def __init__(self):
        self.genes: RobotGenes = None
        self.fitness: float = 0.0
        self.battle_metrics = {
            'time_alive': 0.0,
            'enemies_killed': 0,
            'base_damage': 0.0,
            'damage_taken': 0.0
        }

    def apply_genes(self, genes: RobotGenes) -> None:
        """Применение генов к роботу"""
        self.genes = genes
        self.health = genes.health
        self.speed = genes.speed
        self.damage = genes.damage
        self._apply_aggression(genes.aggression)

    def _apply_aggression(self, aggression: float) -> None:
        """Применение уровня агрессии к поведению робота"""
        self.attack_threshold = 1.0 - aggression  # Чем выше агрессия, тем ниже порог атаки

    def update_battle_metrics(self, time_alive: float, enemies_killed: int,
                            base_damage: float, damage_taken: float) -> None:
        """Обновление метрик боя"""
        self.battle_metrics['time_alive'] = time_alive
        self.battle_metrics['enemies_killed'] = enemies_killed
        self.battle_metrics['base_damage'] = base_damage
        self.battle_metrics['damage_taken'] = damage_taken
