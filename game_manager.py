from csv_logger import CSVLogger

class GameManager:
    def __init__(self):
        # ... существующий код ...
        self.csv_logger = CSVLogger()

    def update(self) -> None:
        """Обновление игровой логики"""
        current_time = pygame.time.get_ticks()

        # Спавн новых роботов
        self._handle_robot_spawning(current_time)

        # Обновление роботов
        for robot in self.blue_robots:
            if robot.is_alive():
                robot.update(self.blue_robots, self.red_robots, self.obstacles, self.red_base)

        for robot in self.red_robots:
            if robot.is_alive():
                robot.update(self.red_robots, self.blue_robots, self.obstacles, self.blue_base)

        # Удаление мертвых роботов
        self.blue_robots = [robot for robot in self.blue_robots if robot.is_alive()]
        self.red_robots = [robot for robot in self.red_robots if robot.is_alive()]

        # Логирование статистики после каждого матча
        blue_generation = self.evolution.populations['blue'].generation
        red_generation = self.evolution.populations['red'].generation

        self.csv_logger.log_statistics('blue_team_stats.csv', self.blue_robots, blue_generation)
        self.csv_logger.log_statistics('red_team_stats.csv', self.red_robots, red_generation)

        for robot_type in ['MeleeRobot', 'RangedRobot', 'TankRobot']:
            self.csv_logger.log_statistics(f'{robot_type}_stats.csv', self.blue_robots + self.red_robots, blue_generation)
