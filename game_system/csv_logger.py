import csv
import os
from typing import List, Dict

class CSVLogger:
    """Класс для логирования статистики в CSV"""
    def __init__(self, output_dir: str = 'logs'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def log_team_statistics(self, team: str, robots: List['Robot']) -> None:
        """Логирование статистики команды"""
        filename = os.path.join(self.output_dir, f'{team}_team_stats.csv')
        fieldnames = ['robot_type', 'team', 'damage', 'speed', 'kills', 'damage_to_enemies', 'damage_to_base']

        with open(filename, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if f.tell() == 0:
                writer.writeheader()

            for robot in robots:
                writer.writerow({
                    'robot_type': type(robot).__name__,
                    'team': team,
                    'damage': robot.damage,
                    'speed': robot.speed,
                    'kills': robot.kills,
                    'damage_to_enemies': robot._get_base_damage(),
                    'damage_to_base': robot.base_damage_dealt
                })

    def log_robot_statistics(self, robot_type: str, robots: List['Robot']) -> None:
        """Логирование статистики по типу роботов"""
        filename = os.path.join(self.output_dir, f'{robot_type}_stats.csv')
        fieldnames = ['robot_type', 'team', 'damage', 'speed', 'kills', 'damage_to_enemies', 'damage_to_base']

        with open(filename, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if f.tell() == 0:
                writer.writeheader()

            for robot in robots:
                if type(robot).__name__ == robot_type:
                    writer.writerow({
                        'robot_type': type(robot).__name__,
                        'team': robot.team.value,
                        'damage': robot.damage,
                        'speed': robot.speed,
                        'kills': robot.kills,
                        'damage_to_enemies': robot._get_base_damage(),
                        'damage_to_base': robot.base_damage_dealt
                    })
