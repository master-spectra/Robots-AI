import pygame
import random
import math
from typing import List
from game_system.config import *
from entities.base import RedBase, BlueBase
from entities.obstacle import Obstacle

class GameManager:
    """Класс управления игровым процессом"""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Битва роботов")
        self.clock = pygame.time.Clock()
        self.running = True

        self._initialize_game_objects()

    def _initialize_game_objects(self) -> None:
        """Инициализация игровых объектов"""
        # Создание баз в новых позициях с учетом отступов для полосок здоровья
        self.blue_base = BlueBase(100, 100)  # Увеличил отступ от края
        self.red_base = RedBase(WINDOW_WIDTH - 100, WINDOW_HEIGHT - 100)

        # Создание препятствий
        self.obstacles = self._generate_obstacles()

    def _generate_obstacles(self) -> List[Obstacle]:
        """Генерация препятствий на карте"""
        obstacles = []
        for _ in range(20):
            while True:
                x = random.randint(150, WINDOW_WIDTH - 150)  # Увеличил отступ
                y = random.randint(150, WINDOW_HEIGHT - 150)  # Увеличил отступ

                # Проверка расстояния до баз
                if (math.dist((x, y), (self.blue_base.x, self.blue_base.y)) > 100 and
                    math.dist((x, y), (self.red_base.x, self.red_base.y)) > 100):
                    break

            obstacle_type = random.choice(["tree", "rock"])
            obstacles.append(Obstacle(x, y, obstacle_type))
        return obstacles

    def handle_events(self) -> None:
        """Обработка игровых событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self) -> None:
        """Обновление игровой логики"""
        pass

    def draw(self) -> None:
        """Отрисовка игровых объектов"""
        self.screen.fill(Colors.GREEN)

        for obstacle in self.obstacles:
            obstacle.draw(self.screen)

        self.blue_base.draw(self.screen)
        self.red_base.draw(self.screen)

        pygame.display.flip()

    def run(self) -> None:
        """Главный игровой цикл"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
