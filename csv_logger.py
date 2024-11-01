import csv
import os
from typing import List

class CSVLogger:
    """Класс для логирования статистики в CSV"""
    def __init__(self, output_dir: str = 'logs'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def log_statistics(self, filename: str, robots: List['Robot'], generation: int) -> None:
        """Логирование статистики роботов"""
        filepath = os.path.join(self.output_dir, filename)
        fieldnames = ['robot_type', 'team', 'generation', 'damage', 'speed', 'kills', 'damage_to_enemies', 'damage_to_base', 'aggression']

        with open(filepath, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if f.tell() == 0:
                writer.writeheader()

            for robot in robots:
                writer.writerow({
                    'robot_type': type(robot).__name__,
                    'team': robot.team.value,
                    'generation': generation,
                    'damage': robot.damage,
                    'speed': robot.speed,
                    'kills': robot.kills,
                    'damage_to_enemies': robot._get_base_damage(),
                    'damage_to_base': robot.base_damage_dealt,
                    'aggression': robot.genes.aggression if robot.genes else None
                })
