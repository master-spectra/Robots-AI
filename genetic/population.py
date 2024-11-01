from typing import List, Optional
import numpy as np
from .chromosome import RobotGenes

class Population:
    """Класс для управления популяцией роботов"""
    def __init__(self, size: int = 10):
        self.size = size
        self.individuals: List[RobotGenes] = []
        self.generation = 0

    def initialize_from_robot(self, robot: 'Robot') -> None:
        """Инициализация популяции на основе базового робота"""
        self.individuals = []
        base_genes = RobotGenes.from_robot(robot)

        for _ in range(self.size):
            new_genes = RobotGenes(**base_genes.to_dict())
            new_genes.mutate(mutation_rate=1.0)  # 100% мутация для начальной популяции
            self.individuals.append(new_genes)

    def select_tournament(self, tournament_size: int = 3) -> RobotGenes:
        """Турнирная селекция"""
        tournament = np.random.choice(self.individuals, tournament_size, replace=False)
        return max(tournament, key=lambda x: x.fitness if hasattr(x, 'fitness') else 0)
