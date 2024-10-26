from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
import pygame
import numpy as np
from enum import Enum
from game_system.config import Colors, WINDOW_WIDTH, WINDOW_HEIGHT
import heapq
import random

class Team(Enum):
    """Перечисление для команд"""
    BLUE = "blue"
    RED = "red"

class PathFinder:
    """Класс для поиска пути (A* алгоритм)"""
    def __init__(self, obstacles: List['Obstacle'], grid_size: int = 20):
        self.grid_size = grid_size
        self.obstacles = obstacles
        self.rows = WINDOW_HEIGHT // grid_size
        self.cols = WINDOW_WIDTH // grid_size

    def _get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Получение соседних клеток"""
        x, y = pos
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < self.cols and 0 <= new_y < self.rows:
                neighbors.append((new_x, new_y))
        return neighbors

    def _is_valid_position(self, pos: Tuple[int, int], robot_radius: int) -> bool:
        """Проверка валидности позиции"""
        x, y = pos[0] * self.grid_size, pos[1] * self.grid_size
        for obstacle in self.obstacles:
            if np.linalg.norm(np.array([x, y]) - np.array([obstacle.x, obstacle.y])) < (obstacle.radius + robot_radius):
                return False
        return True

    def find_path(self, start: np.ndarray, goal: np.ndarray, robot_radius: int) -> List[np.ndarray]:
        """Поиск пути с помощью A*"""
        start_pos = (int(start[0] // self.grid_size), int(start[1] // self.grid_size))
        goal_pos = (int(goal[0] // self.grid_size), int(goal[1] // self.grid_size))

        if not self._is_valid_position(goal_pos, robot_radius):
            return []

        frontier = [(0, start_pos)]
        came_from = {start_pos: None}
        cost_so_far = {start_pos: 0}

        while frontier:
            _, current = heapq.heappop(frontier)

            if current == goal_pos:
                break

            for next_pos in self._get_neighbors(current):
                if not self._is_valid_position(next_pos, robot_radius):
                    continue

                new_cost = cost_so_far[current] + 1
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + np.linalg.norm(np.array(goal_pos) - np.array(next_pos))
                    heapq.heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = current

        # Восстановление пути
        path = []
        current = goal_pos
        while current is not None:
            path.append(np.array([current[0] * self.grid_size, current[1] * self.grid_size]))
            current = came_from.get(current)

        return list(reversed(path))

class Robot(ABC):
    """Базовый кл��сс для всех роботов"""
    def __init__(self, x: int, y: int, team: Team):
        self.position = np.array([x, y], dtype=float)
        self.team = team
        self.health = 100
        self.max_health = 100
        self.speed = 5
        self.alive = True
        self.last_attack_time = 0
        self.attack_cooldown = 1000
        self.radius = 15
        self.current_path = []
        self.pathfinder = None

    def set_pathfinder(self, pathfinder: PathFinder) -> None:
        """Установка pathfinder для робота"""
        self.pathfinder = pathfinder

    def move_along_path(self, target_position: np.ndarray, obstacles: List['Obstacle']) -> None:
        """Движение по пути с обходом препятствий"""
        if not self.current_path:
            if self.pathfinder:
                self.current_path = self.pathfinder.find_path(self.position, target_position, self.radius)

        if self.current_path:
            next_point = self.current_path[0]
            if np.linalg.norm(self.position - next_point) < self.speed:
                self.current_path.pop(0)
            else:
                self.move_towards(next_point)

    def draw(self, screen: pygame.Surface) -> None:
        """Отрисовка робота"""
        color = Colors.BLUE if self.team == Team.BLUE else Colors.RED
        pygame.draw.circle(screen, color, self.position.astype(int), self.radius)

        # Отрисовка полоски здоровья
        health_percentage = self.health / self.max_health
        health_bar_width = 30
        health_bar_height = 5

        # Белый фон для полоски здоровья
        pygame.draw.rect(screen, Colors.WHITE,
                        (self.position[0] - health_bar_width/2 - 1,  # Немного шире для рамки
                         self.position[1] - self.radius - 11,        # Немного выше для раки
                         health_bar_width + 2,                       # Добавляем отступ для рамки
                         health_bar_height + 2))                     # Добавляем отступ для рамки

        # Черная рамка
        pygame.draw.rect(screen, Colors.BLACK,
                        (self.position[0] - health_bar_width/2,
                         self.position[1] - self.radius - 10,
                         health_bar_width,
                         health_bar_height))

        # Текущее здоровье
        if health_percentage > 0.7:
            health_color = Colors.GREEN
        elif health_percentage > 0.3:
            health_color = (255, 165, 0)  # Оранжевый
        else:
            health_color = Colors.RED

        pygame.draw.rect(screen, health_color,
                        (self.position[0] - health_bar_width/2,
                         self.position[1] - self.radius - 10,
                         health_bar_width * health_percentage,
                         health_bar_height))

    def move_towards(self, target_position: np.ndarray) -> None:
        """Движение к целевой позиции с учетом границ карты"""
        direction = target_position - self.position
        distance = np.linalg.norm(direction)
        if distance > 0:
            normalized_direction = direction / distance
            new_position = self.position + normalized_direction * min(self.speed, distance)

            # Проверка границ карты
            new_position[0] = np.clip(new_position[0], self.radius, WINDOW_WIDTH - self.radius)
            new_position[1] = np.clip(new_position[1], self.radius, WINDOW_HEIGHT - self.radius)

            self.position = new_position

    def distance_to(self, target_position: np.ndarray) -> float:
        return np.linalg.norm(self.position - target_position)

    def is_alive(self) -> bool:
        return self.health > 0

    def take_damage(self, damage: float) -> None:
        self.health = max(0, self.health - damage)
        if self.health <= 0:
            self.alive = False

    @abstractmethod
    def update(self, allies: List['Robot'], enemies: List['Robot'], obstacles: List['Obstacle']) -> None:
        pass

    def _find_nearest_enemy(self, enemies: List['Robot']) -> Optional['Robot']:
        """Поиск ближайшего врага"""
        living_enemies = [e for e in enemies if e.is_alive()]
        if not living_enemies:
            return None
        return min(living_enemies, key=lambda e: self.distance_to(e.position))

    def _attack(self, target: 'Robot') -> None:
        """Базовый метод атаки"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            target.take_damage(self.damage)
            self.last_attack_time = current_time

    def _can_attack_base(self, enemy_base: 'GameBase') -> bool:
        """Проверка возможности атаки базы"""
        distance = np.linalg.norm(self.position - np.array([enemy_base.x, enemy_base.y]))
        return distance <= self.attack_range

    def _attack_base(self, enemy_base: 'GameBase') -> None:
        """Базовый метод атаки базы"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            enemy_base.current_health -= self.damage
            self.last_attack_time = current_time

class MeleeRobot(Robot):
    """Робот ближнего боя"""
    def __init__(self, x: int, y: int, team: Team):
        super().__init__(x, y, team)
        self.attack_range = 50
        self.detection_range = 200
        self.damage = 20
        self.health = 150
        self.max_health = 150
        self.radius = 20

        # Загрузка изображения в зависимости от команды
        if team == Team.BLUE:
            self.image = pygame.image.load("./pic/BlueMeleeAgent.png")
        else:
            self.image = pygame.image.load("./pic/RedMeleeAgent.png")

        # Масштабирование изображения
        self.image = pygame.transform.scale(self.image, (40, 40))  # Размер в пикселях
        self.rect = self.image.get_rect()

    def draw(self, screen: pygame.Surface) -> None:
        """Отрисовка робота с изображением"""
        # Обновление позиции прямоугольника изображения
        self.rect.center = self.position.astype(int)

        # Отрисовка изображения
        screen.blit(self.image, self.rect)

        # Отрисовка полоски здоровья
        health_percentage = self.health / self.max_health
        health_bar_width = 30
        health_bar_height = 5

        # Белый фон для полоски здоровья
        pygame.draw.rect(screen, Colors.WHITE,
                        (self.position[0] - health_bar_width/2 - 1,
                         self.position[1] - self.radius - 11,
                         health_bar_width + 2,
                         health_bar_height + 2))

        # Черная рамка
        pygame.draw.rect(screen, Colors.BLACK,
                        (self.position[0] - health_bar_width/2,
                         self.position[1] - self.radius - 10,
                         health_bar_width,
                         health_bar_height))

        # Текущее здоровье
        if health_percentage > 0.7:
            health_color = Colors.GREEN
        elif health_percentage > 0.3:
            health_color = (255, 165, 0)  # Оранжевый
        else:
            health_color = Colors.RED

        pygame.draw.rect(screen, health_color,
                        (self.position[0] - health_bar_width/2,
                         self.position[1] - self.radius - 10,
                         health_bar_width * health_percentage,
                         health_bar_height))

    def update(self, allies: List[Robot], enemies: List[Robot], obstacles: List['Obstacle'], enemy_base: 'GameBase') -> None:
        if not self.is_alive():
            return

        # Сначала проверяем возможность атаки базы
        if self._can_attack_base(enemy_base):
            self._attack_base(enemy_base)
            return

        # Существующая логика атаки враг��в
        nearest_enemy = self._find_nearest_enemy(enemies)
        if nearest_enemy:
            dist_to_enemy = self.distance_to(nearest_enemy.position)
            if dist_to_enemy <= self.attack_range:
                self._attack(nearest_enemy)
            elif dist_to_enemy <= self.detection_range:
                self._avoid_obstacles_and_move(nearest_enemy.position, obstacles)
        else:
            # Если нет врагов, двигаемся к вражеской базе
            self.move_along_path(np.array([enemy_base.x, enemy_base.y]), obstacles)

    def _avoid_obstacles_and_move(self, target_position: np.ndarray, obstacles: List['Obstacle']) -> None:
        """Движение к цели с обходом препятствий"""
        for obstacle in obstacles:
            if self.distance_to(np.array([obstacle.x, obstacle.y])) < obstacle.radius + self.radius + 10:
                # Простой алгоритм обхода - отходим от препятствия
                direction = self.position - np.array([obstacle.x, obstacle.y])
                if np.linalg.norm(direction) > 0:
                    self.move_towards(self.position + direction)
                return

        self.move_towards(target_position)

    def _attack(self, target: Robot) -> None:
        """Атака ближнего боя"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            # Гарантированное попадание в ближнем бою
            target.take_damage(self.damage)
            self.last_attack_time = current_time

class Projectile:
    """Класс снаряда"""
    def __init__(self, start_pos: np.ndarray, target_pos: np.ndarray, speed: float = 10, damage: float = 15):
        self.position = start_pos.copy()
        self.direction = target_pos - start_pos
        length = np.linalg.norm(self.direction)
        if length > 0:
            self.direction = self.direction / length
        self.speed = speed
        self.damage = damage
        self.active = True
        self.radius = 3

    def update(self) -> None:
        """Обновление позиции снаряда"""
        self.position += self.direction * self.speed

    def draw(self, screen: pygame.Surface) -> None:
        """Отрисовка снаряда"""
        pygame.draw.circle(screen, Colors.WHITE, self.position.astype(int), self.radius)
        # Добавим след снаряда
        trail_pos = self.position - self.direction * 5
        pygame.draw.circle(screen, Colors.WHITE, trail_pos.astype(int), self.radius - 1)

    def check_collision(self, target: 'Robot') -> bool:
        """Проверка попадания в цель"""
        distance = np.linalg.norm(self.position - target.position)
        return distance < (target.radius + self.radius)

    def check_collision_with_base(self, base: 'GameBase') -> bool:
        """Проверка попадания в базу"""
        distance = np.linalg.norm(self.position - np.array([base.x, base.y]))
        return distance < (base.radius + self.radius)

class RangedRobot(Robot):
    """Робот дальнего боя"""
    def __init__(self, x: int, y: int, team: Team):
        super().__init__(x, y, team)
        self.attack_range = 200
        self.optimal_range = 150
        self.retreat_range = 100
        self.damage = 15
        self.health = 80
        self.max_health = 80
        self.speed = 4
        self.radius = 18
        self.projectiles = []  # Список активных снарядов
        self.projectile_speed = 8
        self.attack_cooldown = 1500  # Увеличенная перезарядка для баланса

        # Загрузка изображения
        if team == Team.BLUE:
            self.image = pygame.image.load("./pic/BlueRangedAgent.png")
        else:
            self.image = pygame.image.load("./pic/RedRangedAgent.png")

        self.image = pygame.transform.scale(self.image, (36, 36))
        self.rect = self.image.get_rect()

    def update(self, allies: List[Robot], enemies: List[Robot], obstacles: List['Obstacle'], enemy_base: 'GameBase') -> None:
        if not self.is_alive():
            return

        # Обновление снарядов
        self._update_projectiles(enemies, enemy_base)

        # Проверка возможности атаки базы
        base_distance = np.linalg.norm(self.position - np.array([enemy_base.x, enemy_base.y]))
        if self.optimal_range <= base_distance <= self.attack_range:
            self._attack_base_with_projectile(enemy_base)
            return

        # Существующая логика
        nearest_enemy = self._find_nearest_enemy(enemies)
        if nearest_enemy:
            dist_to_enemy = self.distance_to(nearest_enemy.position)

            if dist_to_enemy < self.retreat_range:
                # Отступление
                retreat_pos = self.position + (self.position - nearest_enemy.position) * 2
                self.move_along_path(retreat_pos, obstacles)
            elif dist_to_enemy > self.optimal_range:
                # Сближение
                self.move_along_path(nearest_enemy.position, obstacles)
            elif dist_to_enemy <= self.attack_range:
                # Атака
                self._attack(nearest_enemy)

    def _update_projectiles(self, enemies: List[Robot], enemy_base: 'GameBase') -> None:
        """Обновление всех активных снарядов"""
        for projectile in self.projectiles:
            projectile.update()

            # Проверка попаданий по роботам
            for enemy in enemies:
                if enemy.is_alive() and projectile.active and projectile.check_collision(enemy):
                    enemy.take_damage(projectile.damage)
                    projectile.active = False

            # Проверка попаданий по базе
            if projectile.active and projectile.check_collision_with_base(enemy_base):
                enemy_base.current_health -= projectile.damage
                projectile.active = False

            # Проверка выхода за пределы экрана
            if (projectile.position[0] < 0 or projectile.position[0] > WINDOW_WIDTH or
                projectile.position[1] < 0 or projectile.position[1] > WINDOW_HEIGHT):
                projectile.active = False

        self.projectiles = [p for p in self.projectiles if p.active]

    def _attack_base_with_projectile(self, enemy_base: 'GameBase') -> None:
        """Атака базы снарядом"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            projectile = Projectile(
                self.position.copy(),
                np.array([enemy_base.x, enemy_base.y]),
                self.projectile_speed,
                self.damage * 0.5  # Уменьшенный урон по базе для баланса
            )
            self.projectiles.append(projectile)
            self.last_attack_time = current_time

    def draw(self, screen: pygame.Surface) -> None:
        # Отрисовка снарядов
        for projectile in self.projectiles:
            projectile.draw(screen)

        # Отрисовка робота (оставшийся код без изменений)
        super().draw(screen)

    def _attack(self, target: Robot) -> None:
        """Атака дальнего боя со снарядами"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            # Создание нового снаряда
            projectile = Projectile(
                self.position.copy(),
                target.position.copy(),
                self.projectile_speed,
                self.damage
            )
            self.projectiles.append(projectile)
            self.last_attack_time = current_time

class TankRobot(Robot):
    """Робот-танк"""
    def __init__(self, x: int, y: int, team: Team):
        super().__init__(x, y, team)
        self.attack_range = 80
        self.protection_range = 150
        self.damage = 25
        self.health = 200
        self.max_health = 200
        self.speed = 3
        self.radius = 25
        self.damage_reduction = 0.5

        # Загрузка изображения в зависимости от команды
        if team == Team.BLUE:
            self.image = pygame.image.load("./pic/BlueTankAgent.png")
        else:
            self.image = pygame.image.load("./pic/RedTankAgent.png")

        # Масштабирование изображения
        self.image = pygame.transform.scale(self.image, (50, 50))  # Больше, чем другие роботы
        self.rect = self.image.get_rect()

    def draw(self, screen: pygame.Surface) -> None:
        """Отрисовка робота с изображением"""
        # Обновление позиции прямоугольника изображения
        self.rect.center = self.position.astype(int)

        # Отрисовка изображения
        screen.blit(self.image, self.rect)

        # Отрисовка полоски здоровья
        health_percentage = self.health / self.max_health
        health_bar_width = 40  # Увеличенная ширина полоски здоровья для танка
        health_bar_height = 6  # Увеличенная высота полоски здоровья для танка

        # Белый фон для полоски здоровья
        pygame.draw.rect(screen, Colors.WHITE,
                        (self.position[0] - health_bar_width/2 - 1,
                         self.position[1] - self.radius - 11,
                         health_bar_width + 2,
                         health_bar_height + 2))

        # Черная рамка
        pygame.draw.rect(screen, Colors.BLACK,
                        (self.position[0] - health_bar_width/2,
                         self.position[1] - self.radius - 10,
                         health_bar_width,
                         health_bar_height))

        # Текущее здоровье
        if health_percentage > 0.7:
            health_color = Colors.GREEN
        elif health_percentage > 0.3:
            health_color = (255, 165, 0)  # Оранжевый
        else:
            health_color = Colors.RED

        pygame.draw.rect(screen, health_color,
                        (self.position[0] - health_bar_width/2,
                         self.position[1] - self.radius - 10,
                         health_bar_width * health_percentage,
                         health_bar_height))

    def update(self, allies: List[Robot], enemies: List[Robot], obstacles: List['Obstacle'], enemy_base: 'GameBase') -> None:
        if not self.is_alive():
            return

        # Проверка возможности атаки базы
        if self._can_attack_base(enemy_base):
            self._attack_base(enemy_base)
            return

        # Защита союзников
        weak_ally = self._find_weakest_ally(allies)
        if weak_ally and weak_ally.health < weak_ally.max_health * 0.5:
            self.move_along_path(weak_ally.position, obstacles)

            # Атака врагов вблизи слабого союзника
            for enemy in enemies:
                if (enemy.is_alive() and
                    enemy.distance_to(weak_ally.position) <= enemy.attack_range and
                    self.distance_to(enemy.position) <= self.attack_range):
                    self._attack(enemy)
        else:
            # Если нет слабых союзников, двигаемся к вражеской базе
            self.move_along_path(np.array([enemy_base.x, enemy_base.y]), obstacles)

    def take_damage(self, damage: float) -> None:
        """Переопределенное получение урона с учетом брони"""
        super().take_damage(damage * self.damage_reduction)

    def _find_weakest_ally(self, allies: List[Robot]) -> Optional[Robot]:
        """Поиск союзника с наименьшим здоровьем"""
        living_allies = [a for a in allies if a.is_alive() and a != self]
        if not living_allies:
            return None
        return min(living_allies, key=lambda a: a.health / a.max_health)

    def _attack(self, target: Robot) -> None:
        """Атака танка с оглушающим эффектом"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            # Танк наносит гарантированный урон
            target.take_damage(self.damage)
            self.last_attack_time = current_time

    def _attack_base(self, enemy_base: 'GameBase') -> None:
        """Атака базы танком"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            enemy_base.current_health -= self.damage * 1.5  # Увеличенный урон по базе
            self.last_attack_time = current_time

