import pygame
import random
import math
from game_system.game_manager import GameManager
from genetic.visualizer import EvolutionVisualizer
from genetic.data_handler import DataHandler
import pandas as pd
import os

def visualize_results():
    """Функция для визуализации результатов после завершения игры"""
    try:
        # Создание экземпляра визуализатора
        visualizer = EvolutionVisualizer()

        # Загрузка данных
        data_handler = DataHandler()

        # Загрузка и проверка существования данных
        blue_gen1 = data_handler.load_generation('blue', 1)
        red_gen1 = data_handler.load_generation('red', 1)

        if blue_gen1 and red_gen1:
            print("Визуализация статистики поколений...")
            visualizer.plot_generation_stats('blue', blue_gen1)
            visualizer.plot_generation_stats('red', red_gen1)
            visualizer.plot_team_comparison(blue_gen1, red_gen1)

        # Проверяем существование файла статистики
        stats_file = 'logs/MeleeRobot_stats.csv'
        if os.path.exists(stats_file):
            print("Визуализация статистики боев...")
            battle_stats = pd.read_csv(stats_file)
            if not battle_stats.empty:
                visualizer.plot_battle_statistics(battle_stats)

        print("Визуализация завершена успешно")

    except Exception as e:
        print(f"Ошибка при визуализации: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Инициализация Pygame
    pygame.init()

    try:
        # Запуск игры
        game = GameManager()
        game.run()
    finally:
        # Завершение Pygame
        pygame.quit()

        # Визуализация результатов
        visualize_results()
