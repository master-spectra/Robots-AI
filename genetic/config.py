from dataclasses import dataclass, field
from typing import Dict

@dataclass
class GeneticConfig:
    """Конфигурация генетического алгоритма"""
    # Базовые параметры
    POPULATION_SIZE: int = 10
    MUTATION_RATE: float = 0.1
    TOURNAMENT_SIZE: int = 3
    ELITE_SIZE: int = 1

    # Размеры популяций для разных типов роботов
    POPULATION_SIZES: Dict[str, int] = field(default_factory=lambda: {
        'melee': 10,
        'ranged': 10,
        'tank': 10
    })

    # Пределы характеристик
    MAX_HEALTH: float = 300.0
    MAX_SPEED: float = 10.0
    MAX_DAMAGE: float = 50.0
    MAX_AGGRESSION: float = 1.0

    # Веса для фитнес-функции
    FITNESS_WEIGHTS = {
        'time_alive': 0.2,
        'enemies_killed': 0.3,
        'base_damage': 0.4,
        'damage_taken': 0.1
    }

    # Параметры сохранения данных
    SAVE_FREQUENCY: int = 1  # Каждое n-ое поколение
    DATA_DIR: str = 'genetic_data'
    PLOT_DIR: str = 'genetic_plots'

    # Параметры визуализации
    PLOT_FIGSIZE: tuple = (10, 6)
    PLOT_STYLE: str = 'seaborn'
    PLOT_DPI: int = 100
