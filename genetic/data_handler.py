import csv
from typing import List, Dict
import os

class DataHandler:
    """Класс для работы с данными эволюции"""
    def __init__(self, output_dir: str = 'genetic_data'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def save_generation(self, robot_type: str, generation: int,
                       individuals: List[Dict]) -> None:
        """Сохранение поколения в CSV"""
        filename = f"{robot_type}_gen{generation}.csv"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=individuals[0].keys())
            writer.writeheader()
            writer.writerows(individuals)

    def load_generation(self, robot_type: str, generation: int) -> List[Dict]:
        """Загрузка поколения из CSV"""
        filename = f"{robot_type}_gen{generation}.csv"
        filepath = os.path.join(self.output_dir, filename)

        if not os.path.exists(filepath):
            return []

        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            return list(reader)
