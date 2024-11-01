from genetic.genetic_robot import GeneticRobot
from game_system.config import Colors, WINDOW_WIDTH, WINDOW_HEIGHT
import pygame
import numpy as np
from enum import Enum
from typing import List, Optional
from entities.projectile import Projectile

class Team(Enum):
    """Перечисление для команд"""
    BLUE = "blue"
    RED = "red"

class Robot(GeneticRobot):
    """Базовый класс для всех роботов"""
    def __init__(self, x: int, y: int, team: Team):
        super().__init__()  # Инициализация генетических свойств
        self.genes = None  # Убедитесь, что атрибут существует
        self.position = np.array([x, y], dtype=float)
        self.team = team
        self.alive = True
        self.last_attack_time = 0
        self.attack_cooldown = 1000
        self.radius = 15
        self.current_path = []
        self.pathfinder = None
        self.spawn_time = pygame.time.get_ticks()
        self.kills = 0  # Инициализация счетчика убийств
        self.base_damage_dealt = 0.0  # Инициализация урона по базе
        self.damage_taken = 0.0  # Инициализация полученного урона

    def set_pathfinder(self, pathfinder: 'PathFinder') -> None:
        """Установка pathfinder для робота"""
        self.pathfinder = pathfinder

    def is_alive(self) -> bool:
        """Проверка, жив ли робот"""
        return self.health > 0

    def update(self, allies: List['Robot'], enemies: List['Robot'],
               obstacles: List['Obstacle'], enemy_base: 'GameBase') -> None:
        """Обновление состояния робота"""
        if self.genes is None:
            print("Warning: Robot has no genes")
            return

        current_time = pygame.time.get_ticks()

        # Обновление метрик боя
        self.update_battle_metrics(
            time_alive=(current_time - self.spawn_time) / 1000.0,
            enemies_killed=self._count_kills(),
            base_damage=self._get_base_damage(),
            damage_taken=self._get_damage_taken()
        )

        # Групповое поведение
        if self._is_strong_enemy_present(enemies):
            self._coordinate_attack(allies, enemies)
        else:
            # Поведение в зависимости от агрессивности
            if self.genes.aggression > 0.7:
                # Высокая агрессивность - атака без учета здоровья
                target = self._find_nearest_enemy(enemies) or enemy_base
                self._attack(target)
            else:
                # Низкая агрессивность - осторожное поведение
                nearest_enemy = self._find_nearest_enemy(enemies)
                if nearest_enemy and self.health / self.max_health > 0.3:
                    self._attack(nearest_enemy)
                else:
                    self.move_along_path(np.array([enemy_base.x, enemy_base.y]), obstacles)

    def _is_strong_enemy_present(self, enemies: List['Robot']) -> bool:
        """Проверка наличия сильного врага"""
        for enemy in enemies:
            if enemy.is_alive() and enemy.health > 100:  # Пример порога
                return True
        return False

    def _coordinate_attack(self, allies: List['Robot'], enemies: List['Robot']) -> None:
        """Координация атаки с союзниками"""
        target = self._find_strongest_enemy(enemies)
        if target:
            for ally in allies:
                if ally.is_alive():
                    ally.move_along_path(target.position, [])
                    ally._attack(target)

    def _find_strongest_enemy(self, enemies: List['Robot']) -> Optional['Robot']:
        """Поиск самого сильного врага"""
        return max(enemies, key=lambda e: e.health if e.is_alive() else 0, default=None)

    def draw(self, screen: pygame.Surface) -> None:
        """Отрисовка робота"""
        screen.blit(self.image, self.rect)

        # Отрисовка полоски здоровья
        health_percentage = self.health / self.max_health
        health_bar_width = 30
        health_bar_height = 5

        # елый фон для полоски здоровья
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

    def distance_to(self, target_position: np.ndarray) -> float:
        """Вычисление расстояния до целевой позиции"""
        return np.linalg.norm(self.position - target_position)

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

    def _count_kills(self) -> int:
        """Возвращает количество убитых врагов"""
        return self.kills

    def _get_base_damage(self) -> float:
        """Возвращает нанесенный урон по базе"""
        return self.base_damage_dealt

    def _get_damage_taken(self) -> float:
        """Возвращает полученный урон"""
        return self.damage_taken

    def _can_attack_base(self, enemy_base: 'GameBase') -> bool:
        """Проверка возможности атаки базы"""
        distance = np.linalg.norm(self.position - np.array([enemy_base.x, enemy_base.y]))
        return distance <= self.attack_range

    def _find_nearest_enemy(self, enemies: List['Robot']) -> Optional['Robot']:
        """Поиск ближайшего врага"""
        living_enemies = [e for e in enemies if e.is_alive()]
        if not living_enemies:
            return None
        return min(living_enemies, key=lambda e: self.distance_to(e.position))

    def _find_weakest_ally(self, allies: List['Robot']) -> Optional['Robot']:
        """Поиск союзника с наименьшим здоровьем"""
        living_allies = [a for a in allies if a.is_alive() and a != self]
        if not living_allies:
            return None
        return min(living_allies, key=lambda a: a.health / a.max_health)

    def _attack(self, target: 'Robot' or 'GameBase') -> None:
        """Атака цели"""
        if isinstance(target, Robot):
            current_time = pygame.time.get_ticks()
            if current_time - self.last_attack_time >= self.attack_cooldown:
                target.take_damage(self.damage)
                if not target.is_alive():
                    self.kills += 1  # Увеличиваем счетчик убийств
                self.last_attack_time = current_time
        else:
            self._attack_base(target)

    def _attack_base(self, enemy_base: 'GameBase') -> None:
        """Атака базы"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            enemy_base.current_health -= self.damage
            self.base_damage_dealt += self.damage  # Увеличиваем урон по базе
            self.last_attack_time = current_time

    def take_damage(self, damage: float) -> None:
        """Получение урона"""
        self.health = max(0, self.health - damage)
        self.damage_taken += damage  # Увеличиваем полученный урон
        if self.health <= 0:
            self.alive = False

class MeleeRobot(Robot):
    """Робот ближнего боя"""
    def __init__(self, x: int, y: int, team: Team):
        super().__init__(x, y, team)
        # Базовые характеристики (будут изменены генами)
        self.health = 150
        self.max_health = 150
        self.speed = 5
        self.damage = 20
        self.radius = 20
        self.attack_range = 50
        self.detection_range = 200
        self.attack_threshold = 0.5  # Добавлен атрибут

        # Загрузка изображения
        if team == Team.BLUE:
            self.image = pygame.image.load("./pic/BlueMeleeAgent.png")
        else:
            self.image = pygame.image.load("./pic/RedMeleeAgent.png")
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect()

    def update(self, allies: List[Robot], enemies: List[Robot],
               obstacles: List['Obstacle'], enemy_base: 'GameBase') -> None:
        """Обновление с учетом генетических параметров"""
        if not self.is_alive():
            return

        super().update(allies, enemies, obstacles, enemy_base)

        # Проверка агрессивности для принятия решений
        if self._can_attack_base(enemy_base):
            relative_strength = self.health / self.max_health
            if relative_strength > self.attack_threshold:
                self._attack_base(enemy_base)
                return

        nearest_enemy = self._find_nearest_enemy(enemies)
        if nearest_enemy:
            dist_to_enemy = self.distance_to(nearest_enemy.position)
            relative_strength = (self.health / self.max_health) / (nearest_enemy.health / nearest_enemy.max_health)

            if dist_to_enemy <= self.attack_range and relative_strength > self.attack_threshold:
                self._attack(nearest_enemy)
            elif dist_to_enemy <= self.detection_range:
                if relative_strength > self.attack_threshold:
                    self.move_along_path(nearest_enemy.position, obstacles)
                else:
                    # Отступление при низкой агрессивности или здоровье
                    retreat_pos = self.position + (self.position - nearest_enemy.position) * 2
                    self.move_along_path(retreat_pos, obstacles)
        else:
            # Движение к базе при отсутствии врагов
            self.move_along_path(np.array([enemy_base.x, enemy_base.y]), obstacles)

    def _attack_base(self, enemy_base: 'GameBase') -> None:
        """Атака базы"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            enemy_base.current_health -= self.damage
            self.base_damage_dealt += self.damage  # Увеличиваем урон по базе
            self.last_attack_time = current_time

    def draw(self, screen: pygame.Surface) -> None:
        """Отрисовка робота"""
        # Обновление позиции прямоугольника изображения
        self.rect.center = self.position.astype(int)

        # Отрисовка изображения
        screen.blit(self.image, self.rect)

        # Отрисовка полоски здоровья
        super().draw(screen)

class RangedRobot(Robot):
    """Робот дальнего боя"""
    def __init__(self, x: int, y: int, team: Team):
        super().__init__(x, y, team)
        # Базовые характеристики (будут изменены генами)
        self.health = 80
        self.max_health = 80
        self.speed = 4
        self.damage = 15
        self.radius = 18
        self.attack_range = 200
        self.optimal_range = 150
        self.retreat_range = 100
        self.projectiles = []
        self.projectile_speed = 8
        self.attack_cooldown = 1500
        self.attack_threshold = 0.5  # Добавлен атрибут

        # Загрузка изображения
        if team == Team.BLUE:
            self.image = pygame.image.load("./pic/BlueRangedAgent.png")
        else:
            self.image = pygame.image.load("./pic/RedRangedAgent.png")
        self.image = pygame.transform.scale(self.image, (36, 36))
        self.rect = self.image.get_rect()

    def update(self, allies: List[Robot], enemies: List[Robot],
               obstacles: List['Obstacle'], enemy_base: 'GameBase') -> None:
        """Обновление с учетом генетических параметров"""
        if not self.is_alive():
            return

        super().update(allies, enemies, obstacles, enemy_base)

        # Обновление снарядов
        self._update_projectiles(enemies, enemy_base)

        # Проверка агрессивности для принятия решений
        base_distance = np.linalg.norm(self.position - np.array([enemy_base.x, enemy_base.y]))
        if self.optimal_range <= base_distance <= self.attack_range:
            self._attack_base_with_projectile(enemy_base)
            return

        nearest_enemy = self._find_nearest_enemy(enemies)
        if nearest_enemy:
            dist_to_enemy = self.distance_to(nearest_enemy.position)
            relative_strength = (self.health / self.max_health) / (nearest_enemy.health / nearest_enemy.max_health)

            if dist_to_enemy < self.retreat_range and relative_strength < self.attack_threshold:
                retreat_pos = self.position + (self.position - nearest_enemy.position) * 2
                self.move_along_path(retreat_pos, obstacles)
            elif dist_to_enemy > self.optimal_range:
                self.move_along_path(nearest_enemy.position, obstacles)
            elif dist_to_enemy <= self.attack_range:
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
        """Отрисовка робота и снарядов"""
        # Обновление позиции прямоугольника изображения
        self.rect.center = self.position.astype(int)

        # Отрисовка изображения
        screen.blit(self.image, self.rect)

        # Отрисовка полоски здоровья
        super().draw(screen)

        # Отрисовка снарядов
        for projectile in self.projectiles:
            projectile.draw(screen)

class TankRobot(Robot):
    """Робот-танк"""
    def __init__(self, x: int, y: int, team: Team):
        super().__init__(x, y, team)
        # Базовые характеристики (будут изменены генами)
        self.health = 200
        self.max_health = 200
        self.speed = 3
        self.damage = 25
        self.radius = 25
        self.attack_range = 80
        self.protection_range = 150
        self.damage_reduction = 0.5
        self.attack_threshold = 0.5  # Добавлен атибут

        # Загрузка изображения
        if team == Team.BLUE:
            self.image = pygame.image.load("./pic/BlueTankAgent.png")
        else:
            self.image = pygame.image.load("./pic/RedTankAgent.png")
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()

    def update(self, allies: List[Robot], enemies: List[Robot],
               obstacles: List['Obstacle'], enemy_base: 'GameBase') -> None:
        """Обновление с учетом генетических параметров"""
        if not self.is_alive():
            return

        super().update(allies, enemies, obstacles, enemy_base)

        # Проверка агрессивности для принятия решений
        if self._can_attack_base(enemy_base):
            relative_strength = self.health / self.max_health
            if relative_strength > self.attack_threshold:
                self._attack_base(enemy_base)
                return

        weak_ally = self._find_weakest_ally(allies)
        if weak_ally and weak_ally.health < weak_ally.max_health * 0.5:
            self.move_along_path(weak_ally.position, obstacles)
            for enemy in enemies:
                if (enemy.is_alive() and
                    enemy.distance_to(weak_ally.position) <= enemy.attack_range and
                    self.distance_to(enemy.position) <= self.attack_range):
                    self._attack(enemy)
        else:
            self.move_along_path(np.array([enemy_base.x, enemy_base.y]), obstacles)

    def draw(self, screen: pygame.Surface) -> None:
        """Отрисовка робота"""
        # Обновление позиции прямоугольника изображения
        self.rect.center = self.position.astype(int)

        # Отрисовка изображения
        screen.blit(self.image, self.rect)

        # Отрисовка полоски здоровья
        super().draw(screen)

    def take_damage(self, damage: float) -> None:
        """Переопределенное получение урона с учетом брони"""
        super().take_damage(damage * self.damage_reduction)

