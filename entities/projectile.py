import pygame
import numpy as np
from game_system.config import Colors

class Projectile:
    """Класс для управления снарядами"""
    def __init__(self, start_pos: np.ndarray, target_pos: np.ndarray, speed: float, damage: float):
        self.position = start_pos
        self.target_pos = target_pos
        self.speed = speed
        self.damage = damage
        self.active = True

        # Вычисление направления движения
        direction = target_pos - start_pos
        self.direction = direction / np.linalg.norm(direction)

    def update(self) -> None:
        """Обновление позиции снаряда"""
        if self.active:
            self.position += self.direction * self.speed
            # Проверка достижения цели
            if np.linalg.norm(self.position - self.target_pos) < self.speed:
                self.active = False

    def draw(self, screen: pygame.Surface) -> None:
        """Отрисовка снаряда"""
        if self.active:
            pygame.draw.circle(screen, (255, 255, 0), self.position.astype(int), 3)

    def check_collision(self, target: 'Robot') -> bool:
        """Проверка столкновения с роботом"""
        return np.linalg.norm(self.position - target.position) < target.radius

    def check_collision_with_base(self, base: 'GameBase') -> bool:
        """Проверка столкновения с базой"""
        return np.linalg.norm(self.position - np.array([base.x, base.y])) < base.radius
