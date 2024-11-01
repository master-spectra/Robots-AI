from typing import List, Tuple, Optional
import numpy as np
from .chromosome import RobotGenes
from .population import Population
from .fitness import FitnessCalculator

class Evolution:
    """Класс управления эволюционным процессом"""
    def __init__(self, population_size: int = 10, mutation_rate: float = 0.1):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.populations = {
            'blue': Population(self.population_size),
            'red': Population(self.population_size)
        }
        self.fitness_calculator = FitnessCalculator()

    def initialize_population(self, robot_type: str, base_robot: 'Robot') -> None:
        """Инициализация популяции для определенного типа робота"""
        population = self.populations[robot_type]
        base_genes = RobotGenes.from_robot(base_robot)

        for _ in range(self.population_size):
            new_genes = RobotGenes(**base_genes.to_dict())
            new_genes.mutate(mutation_rate=1.0)  # 100% мутация для начальной популяции
            population.individuals.append(new_genes)

    def evolve_population(self, robot_type: str) -> None:
        """Эволюция популяции одного типа роботов"""
        population = self.populations[robot_type]
        new_individuals = []

        # Элитизм - сохраняем лучшую особь
        elite = max(population.individuals,
                   key=lambda x: x.fitness if hasattr(x, 'fitness') else 0)
        new_individuals.append(RobotGenes(**elite.to_dict()))

        # Создаем новое поколение
        while len(new_individuals) < self.population_size:
            parent1 = population.select_tournament()
            parent2 = population.select_tournament()
            child = self._crossover(parent1, parent2)
            child.mutate(self.mutation_rate)
            new_individuals.append(child)

        population.individuals = new_individuals
        population.generation += 1

    def _crossover(self, parent1: RobotGenes, parent2: RobotGenes) -> RobotGenes:
        """Равномерное скрещивание"""
        child_genes = {}
        for field in parent1.__dataclass_fields__:
            if np.random.random() < 0.5:
                child_genes[field] = getattr(parent1, field)
            else:
                child_genes[field] = getattr(parent2, field)
        return RobotGenes(**child_genes)
