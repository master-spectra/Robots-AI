import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os
from typing import List, Dict, Optional

class EvolutionVisualizer:
    """Класс для визуализации процесса эволюции"""
    def __init__(self, output_dir: str = 'genetic_plots'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Настройка стиля графиков
        plt.style.use('default')  # Используем стандартный стиль
        sns.set_theme()  # Применяем тему seaborn
        sns.set_palette("husl")  # Устанавливаем палитру цветов

    def plot_generation_stats(self, team: str, generation_data: List[Dict]) -> None:
        """Визуализация статистики поколения"""
        if not generation_data:
            print(f"Предупреждение: Нет данных для команды {team}")
            return

        df = pd.DataFrame(generation_data)

        # Проверяем наличие необходимых колонок
        required_columns = ['health', 'speed', 'damage', 'aggression']
        if not all(col in df.columns for col in required_columns):
            print("Предупреждение: Отсутствуют необходимые колонки в данных поколения")
            return

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'Generation Statistics for {team.capitalize()} Team', size=16)

        # График распределения характеристик
        sns.boxplot(data=df[required_columns], ax=axes[0, 0])
        axes[0, 0].set_title('Distribution of Robot Characteristics')
        axes[0, 0].set_ylabel('Value')

        # График корреляции между характеристиками
        correlation_matrix = df[required_columns].corr().fillna(0)  # Заполняем NaN нулями
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', ax=axes[0, 1])
        axes[0, 1].set_title('Correlation Between Characteristics')

        # График распределения агрессии
        sns.histplot(data=df, x='aggression', bins=20, ax=axes[1, 0])
        axes[1, 0].set_title('Distribution of Aggression')

        # График соотношения здоровья к урону
        sns.scatterplot(data=df, x='health', y='damage',
                       size='speed', sizes=(50, 400), ax=axes[1, 1])
        axes[1, 1].set_title('Health vs Damage (size=Speed)')

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f'{team}_gen_stats.png'))
        plt.close()

    def plot_evolution_progress(self, team: str, generations: List[Dict]) -> None:
        """Визуализация прогресса эволюции через поколения"""
        fig, axes = plt.subplots(2, 1, figsize=(12, 16))
        fig.suptitle(f'Evolution Progress for {team.capitalize()} Team', size=16)

        # Подготовка данных
        gen_numbers = range(len(generations))
        avg_stats = {
            'health': [np.mean([r['health'] for r in gen]) for gen in generations],
            'damage': [np.mean([r['damage'] for r in gen]) for gen in generations],
            'speed': [np.mean([r['speed'] for r in gen]) for gen in generations],
            'aggression': [np.mean([r['aggression'] for r in gen]) for gen in generations]
        }

        # График изменения средних характеристик
        for stat, values in avg_stats.items():
            axes[0].plot(gen_numbers, values, label=stat.capitalize(), marker='o')

        axes[0].set_title('Average Characteristics Over Generations')
        axes[0].set_xlabel('Generation')
        axes[0].set_ylabel('Value')
        axes[0].legend()
        axes[0].grid(True)

        # График разброса характеристик
        data_for_box = []
        labels = []
        for i, gen in enumerate(generations):
            for stat in ['health', 'damage', 'speed', 'aggression']:
                data_for_box.extend([r[stat] for r in gen])
                labels.extend([f'{stat.capitalize()} (Gen {i})'] * len(gen))

        sns.boxplot(x=labels, y=data_for_box, ax=axes[1])
        axes[1].set_title('Characteristic Distribution Over Generations')
        axes[1].set_xticklabels(axes[1].get_xticklabels(), rotation=45)

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f'{team}_evolution_progress.png'))
        plt.close()

    def plot_team_comparison(self, blue_data: List[Dict], red_data: List[Dict]) -> None:
        """Сравнение статистики команд"""
        blue_df = pd.DataFrame(blue_data)
        red_df = pd.DataFrame(red_data)

        blue_df['team'] = 'Blue'
        red_df['team'] = 'Red'
        combined_df = pd.concat([blue_df, red_df])

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Team Comparison', size=16)

        # Сравнение характеристик между командами
        for i, stat in enumerate(['health', 'damage', 'speed', 'aggression']):
            ax = axes[i // 2, i % 2]
            sns.violinplot(data=combined_df, x='team', y=stat, ax=ax)
            ax.set_title(f'{stat.capitalize()} Distribution')

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'team_comparison.png'))
        plt.close()

    def plot_battle_statistics(self, battle_stats: pd.DataFrame) -> None:
        """Визуализация статистики боев"""
        # Проверяем наличие необходимых колонок
        required_columns = ['robot_type', 'team', 'kills', 'damage_to_base',
                          'damage_to_enemies']

        if not all(col in battle_stats.columns for col in required_columns):
            print("Предупреждение: Отсутствуют необходимые колонки в данных")
            return

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Battle Statistics', size=16)

        # Количество убийств по типам роботов
        ax1 = sns.barplot(data=battle_stats, x='robot_type', y='kills',
                         hue='team', ax=axes[0, 0])
        axes[0, 0].set_title('Kills by Robot Type')
        ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45)

        # Урон по базе
        ax2 = sns.barplot(data=battle_stats, x='robot_type', y='damage_to_base',
                         hue='team', ax=axes[0, 1])
        axes[0, 1].set_title('Base Damage by Robot Type')
        ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45)

        # Общий нанесенный урон
        ax3 = sns.barplot(data=battle_stats, x='robot_type', y='damage_to_enemies',
                         hue='team', ax=axes[1, 0])
        axes[1, 0].set_title('Damage to Enemies by Robot Type')
        ax3.set_xticklabels(ax3.get_xticklabels(), rotation=45)

        # Среднее количество убийств
        ax4 = sns.boxplot(data=battle_stats, x='robot_type', y='kills',
                         hue='team', ax=axes[1, 1])
        axes[1, 1].set_title('Kills Distribution by Robot Type')
        ax4.set_xticklabels(ax4.get_xticklabels(), rotation=45)

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'battle_statistics.png'))
        plt.close()
