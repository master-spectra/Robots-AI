from game_system.config import Colors
from entities.base import BaseEntity
import pygame
import math

class Obstacle(BaseEntity):
    """Класс препятствий на карте"""
    def __init__(self, x: int, y: int, obstacle_type: str):
        super().__init__(x, y)
        self.type = obstacle_type
        self.radius = 15 if obstacle_type == "tree" else 20
        self.color = Colors.BROWN if obstacle_type == "tree" else Colors.GRAY

    def draw(self, screen) -> None:
        if self.type == "tree":
            self._draw_tree(screen)
        else:
            # Камни остаются круглыми
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

    def _draw_tree(self, screen) -> None:
        """Отрисовка дерева"""
        # Ствол дерева
        trunk_width = 16
        trunk_height = 45
        trunk_rect = pygame.Rect(
            self.x - trunk_width // 2,
            self.y - trunk_height // 2,
            trunk_width,
            trunk_height
        )
        pygame.draw.rect(screen, Colors.BROWN, trunk_rect)

        # Крона дерева
        crown_radius = 25
        dark_green = (34, 139, 34)    # Темно-зеленый
        forest_green = (40, 180, 40)  # Лесной зеленый
        lime_green = (50, 205, 50)    # Светло-зеленый

        # Нижний круг кроны (самый большой)
        pygame.draw.circle(screen, dark_green,
                         (self.x, self.y - trunk_height//4),  # Почти у основания ствола
                         crown_radius)

        # Средний круг кроны
        pygame.draw.circle(screen, forest_green,
                         (self.x, self.y - trunk_height//4 - crown_radius//2),  # Вплотную к нижнему
                         crown_radius - 5)

        # Верхний круг кроны (самый маленький)
        pygame.draw.circle(screen, lime_green,
                         (self.x, self.y - trunk_height//4 - crown_radius),  # Вплотную к среднему
                         crown_radius - 10)
