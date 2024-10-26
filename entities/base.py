import pygame
import random
import math
from typing import Optional
from abc import ABC, abstractmethod
from game_system.config import Colors
from entities.robot import MeleeRobot, RangedRobot, TankRobot, Team, Robot

class BaseEntity(ABC):
    """Абстрактный базовый класс для всех игровых сущностей"""
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        pass

class GameBase(BaseEntity):
    """Базовый класс для игровых баз"""
    def __init__(self, x: int, y: int, color: tuple, team: Team, health: int = 5000):
        super().__init__(x, y)
        self.color = color
        self.radius = 40
        self.max_health = health
        self.current_health = health
        self.team = team
        self.spawn_cooldown = 5000  # 5 секунд между спавном
        self.last_spawn_time = 0
        self.robot_types = [MeleeRobot, RangedRobot, TankRobot]
        self.spawn_radius = 80  # Радиус зоны спавна
        self.spawn_min_radius = 50  # Минимальное расстояние от базы

    def spawn_robot(self, current_time: int) -> Optional[Robot]:
        """Спавн нового робота в безопасной зоне около базы"""
        if current_time - self.last_spawn_time >= self.spawn_cooldown:
            # Случайный выбор типа робота
            robot_class = random.choice(self.robot_types)

            # Генерация позиции в кольце вокруг базы
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(self.spawn_min_radius, self.spawn_radius)

            # Вычисление координат с учетом стороны базы
            if self.team == Team.BLUE:
                # Для синей базы - спавн в секторе 90 градусов в сторону поля
                angle = random.uniform(-math.pi/4, math.pi/4)
            else:
                # Для красной базы - спавн в секторе 90 градусов в сторону поля
                angle = random.uniform(3*math.pi/4, 5*math.pi/4)

            spawn_x = self.x + distance * math.cos(angle)
            spawn_y = self.y + distance * math.sin(angle)

            # Создание робота
            new_robot = robot_class(
                spawn_x,
                spawn_y,
                self.team
            )

            self.last_spawn_time = current_time
            return new_robot
        return None

    def draw(self, screen: pygame.Surface) -> None:
        # Отрисовка базы
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        self._draw_health_bar(screen)

        # Отрисовка зоны спавна (полупрозрачный круг)
        spawn_surface = pygame.Surface((self.spawn_radius * 2, self.spawn_radius * 2), pygame.SRCALPHA)
        if self.team == Team.BLUE:
            pygame.draw.circle(spawn_surface, (*Colors.BLUE, 30),
                             (self.spawn_radius, self.spawn_radius), self.spawn_radius)
        else:
            pygame.draw.circle(spawn_surface, (*Colors.RED, 30),
                             (self.spawn_radius, self.spawn_radius), self.spawn_radius)
        screen.blit(spawn_surface, (self.x - self.spawn_radius, self.y - self.spawn_radius))

    def _draw_health_bar(self, screen: pygame.Surface) -> None:
        """Отрисовка полоски здоровья"""
        health_bar_width = 80
        health_bar_height = 8
        health_percentage = self.current_health / self.max_health

        # Фон для текста HP (черный прямоугольник)
        text_background_height = 20
        pygame.draw.rect(screen, Colors.BLACK,
                        (self.x - health_bar_width/2,
                         self.y - 80,
                         health_bar_width,
                         text_background_height))

        # Фон полоски здоровья
        pygame.draw.rect(screen, Colors.BLACK,
                        (self.x - health_bar_width/2,
                         self.y - 60,
                         health_bar_width,
                         health_bar_height))

        # Определение цвета полоски здоровья
        if health_percentage > 0.7:
            health_color = Colors.GREEN
        elif health_percentage > 0.3:
            health_color = (255, 165, 0)  # Оранжевый
        else:
            health_color = Colors.RED

        # Текущее здоровье
        pygame.draw.rect(screen, health_color,
                        (self.x - health_bar_width/2,
                         self.y - 60,
                         health_bar_width * health_percentage,
                         health_bar_height))

        # Добавление текста с количеством HP на ченом фоне
        font = pygame.font.Font(None, 20)
        hp_text = font.render(f"{self.current_health}/{self.max_health}", True, Colors.WHITE)
        text_rect = hp_text.get_rect(center=(self.x, self.y - 70))
        screen.blit(hp_text, text_rect)

class RedBase(GameBase):
    """Класс красной базы"""
    def __init__(self, x: int, y: int):
        super().__init__(x, y, Colors.RED, Team.RED)

class BlueBase(GameBase):
    """Класс синей базы"""
    def __init__(self, x: int, y: int):
        super().__init__(x, y, Colors.BLUE, Team.BLUE)
