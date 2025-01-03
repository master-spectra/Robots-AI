import pygame
import random
import math
from typing import List
from game_system.config import Colors, WINDOW_WIDTH, WINDOW_HEIGHT, FPS
from entities.base import RedBase, BlueBase
from entities.obstacle import Obstacle
from entities.robot import Robot, MeleeRobot, Team, RangedRobot, TankRobot
from entities.pathfinder import PathFinder
from genetic.evolution import Evolution
from genetic.config import GeneticConfig
from genetic.data_handler import DataHandler
from game_system.csv_logger import CSVLogger

class GameManager:
    """Класс управления игровым процессом"""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Битва роботов")
        self.clock = pygame.time.Clock()
        self.running = True
        self.max_robots_per_team = 6  # Максимальное количество роботов в команде

        self._initialize_game_objects()
        self.blue_robots = []
        self.red_robots = []
        self.pathfinder = PathFinder(self.obstacles)

        # Инициализация эволюции должна быт до инициализации роботов
        self.evolution = Evolution(GeneticConfig.POPULATION_SIZE, GeneticConfig.MUTATION_RATE)
        self.spawned_robots_count = {'blue': 0, 'red': 0}
        self.data_handler = DataHandler(GeneticConfig.DATA_DIR)

        # Инициализация популяций
        self._initialize_populations()

        # Инициализация роботов
        self._initialize_robots()

        self.csv_logger = CSVLogger()

    def _generate_obstacles(self) -> List[Obstacle]:
        """Генерация препятствий на карте"""
        obstacles = []
        min_distance = 150  # Минимальное расстояние между препятствиями
        base_safe_distance = 180  # Безопасное расстояние от баз

        for _ in range(10):  # Уменьшили количество препятствий
            attempts = 0
            while attempts < 100:  # Максимальное количество попыток
                x = random.randint(180, WINDOW_WIDTH - 180)
                y = random.randint(180, WINDOW_HEIGHT - 180)

                # Проверка расстояния до баз
                if (math.dist((x, y), (100, 100)) > base_safe_distance and
                    math.dist((x, y), (WINDOW_WIDTH - 100, WINDOW_HEIGHT - 100)) > base_safe_distance):

                    # Проверка расстояния до других препятствий
                    valid_position = True
                    for obstacle in obstacles:
                        if math.dist((x, y), (obstacle.x, obstacle.y)) < min_distance:
                            valid_position = False
                            break

                    if valid_position:
                        obstacle_type = random.choice(["tree", "tree", "tree", "rock", "rock"])
                        obstacles.append(Obstacle(x, y, obstacle_type))
                        break

                attempts += 1

        return obstacles

    def _initialize_game_objects(self) -> None:
        """Инициализация игровых объектов"""
        # Создание баз
        self.blue_base = BlueBase(100, 100)
        self.red_base = RedBase(WINDOW_WIDTH - 100, WINDOW_HEIGHT - 100)

        # Создание препятствий
        self.obstacles = self._generate_obstacles()

    def update(self) -> None:
        """Обновление игровой логики"""
        current_time = pygame.time.get_ticks()

        # Спавн новых роботов
        self._handle_robot_spawning(current_time)

        # Обновление роботов
        for robot in self.blue_robots:
            if robot.is_alive():
                # Синие роботы атакуют красную базу
                robot.update(self.blue_robots, self.red_robots, self.obstacles, self.red_base)

        for robot in self.red_robots:
            if robot.is_alive():
                # Красные роботы атакуют синюю базу
                robot.update(self.red_robots, self.blue_robots, self.obstacles, self.blue_base)

        # Удаление мертвых роботов
        self.blue_robots = [robot for robot in self.blue_robots if robot.is_alive()]
        self.red_robots = [robot for robot in self.red_robots if robot.is_alive()]

        # Логирование статистики после каждого матча
        self.csv_logger.log_team_statistics('blue', self.blue_robots)
        self.csv_logger.log_team_statistics('red', self.red_robots)

        for robot_type in ['MeleeRobot', 'RangedRobot', 'TankRobot']:
            self.csv_logger.log_robot_statistics(robot_type, self.blue_robots + self.red_robots)

    def _handle_robot_spawning(self, current_time: int) -> None:
        """Обработка спавна новых роботов"""
        # Спавн для синей базы
        if len(self.blue_robots) < self.max_robots_per_team:
            new_robot = self.blue_base.spawn_robot(current_time)
            if new_robot:
                new_robot.set_pathfinder(self.pathfinder)
                self.blue_robots.append(new_robot)
                self.spawned_robots_count['blue'] += 1
                if self.spawned_robots_count['blue'] >= 3:
                    self.evolution.evolve_population('blue')
                    individuals = [robot.genes.to_dict() for robot in self.blue_robots if robot.genes is not None]
                    if individuals:  # Проверка, что список не пуст
                        self.data_handler.save_generation(
                            'blue',
                            self.evolution.populations['blue'].generation,
                            individuals
                        )
                    self.spawned_robots_count['blue'] = 0

        # Спавн для красной базы
        if len(self.red_robots) < self.max_robots_per_team:
            new_robot = self.red_base.spawn_robot(current_time)
            if new_robot:
                new_robot.set_pathfinder(self.pathfinder)
                self.red_robots.append(new_robot)
                self.spawned_robots_count['red'] += 1
                if self.spawned_robots_count['red'] >= 3:
                    self.evolution.evolve_population('red')
                    individuals = [robot.genes.to_dict() for robot in self.red_robots if robot.genes is not None]
                    if individuals:  # Проверка, что список не пуст
                        self.data_handler.save_generation(
                            'red',
                            self.evolution.populations['red'].generation,
                            individuals
                        )
                    self.spawned_robots_count['red'] = 0

    def _initialize_robots(self) -> None:
        """Инициализация начальных роботов"""
        robot_types = [MeleeRobot, RangedRobot, TankRobot]

        for robot_class in robot_types:
            # Синие роботы
            blue_robot = robot_class(
                self.blue_base.x + random.randint(-30, 30),
                self.blue_base.y + random.randint(-30, 30),
                Team.BLUE
            )
            blue_robot.set_pathfinder(self.pathfinder)
            if self.evolution.populations['blue'].individuals:
                blue_robot.genes = self.evolution.populations['blue'].individuals[0]  # Присваиваем гены
            else:
                print("Warning: No genes available for blue robot")
            self.blue_robots.append(blue_robot)

            # Красные роботы
            red_robot = robot_class(
                self.red_base.x + random.randint(-30, 30),
                self.red_base.y + random.randint(-30, 30),
                Team.RED
            )
            red_robot.set_pathfinder(self.pathfinder)
            if self.evolution.populations['red'].individuals:
                red_robot.genes = self.evolution.populations['red'].individuals[0]  # Присваиваем гены
            else:
                print("Warning: No genes available for red robot")
            self.red_robots.append(red_robot)

    def handle_events(self) -> None:
        """Обработка игровых событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def draw(self) -> None:
        """Отрисовка игровых объектов"""
        self.screen.fill(Colors.GREEN)

        # Отрисовка препятствий
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)

        # Отрисовка баз
        self.blue_base.draw(self.screen)
        self.red_base.draw(self.screen)

        # Отрисовка роботов
        for robot in self.blue_robots + self.red_robots:
            if robot.is_alive():
                robot.draw(self.screen)

        pygame.display.flip()

    def run(self) -> None:
        """Главный игровой цикл"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def _initialize_populations(self) -> None:
        """Инициализация популяций для каждой команды"""
        # Создаем временных роботов для инициализации популяций
        temp_blue_robot = MeleeRobot(self.blue_base.x, self.blue_base.y, Team.BLUE)
        temp_red_robot = MeleeRobot(self.red_base.x, self.red_base.y, Team.RED)

        self.evolution.initialize_population('blue', temp_blue_robot)
        self.evolution.initialize_population('red', temp_red_robot)
