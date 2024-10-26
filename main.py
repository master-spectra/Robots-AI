import pygame
import random
import math
from game_manager import GameManager
# Инициализация Pygame
pygame.init()

# Константы
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (34, 139, 34)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)

class Base:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 40
        self.health = 100

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        # Отрисовка полоски здоровья
        pygame.draw.rect(screen, BLACK, (self.x - 25, self.y - 50, 50, 5))
        pygame.draw.rect(screen, GREEN, (self.x - 25, self.y - 50, self.health / 2, 5))

class Obstacle:
    def __init__(self, x, y, type_):
        self.x = x
        self.y = y
        self.type = type_  # "tree" или "rock"
        self.radius = 15 if type_ == "tree" else 20

    def draw(self, screen):
        color = BROWN if self.type == "tree" else GRAY
        pygame.draw.circle(screen, color, (self.x, self.y), self.radius)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Битва роботов")
        self.clock = pygame.time.Clock()
        self.running = True

        # Создание баз
        self.blue_base = Base(50, 50, BLUE)
        self.red_base = Base(WINDOW_WIDTH - 50, WINDOW_HEIGHT - 50, RED)

        # Создание препятствий
        self.obstacles = []
        self.generate_obstacles()

    def generate_obstacles(self):
        for _ in range(20):  # 20 препятствий
            while True:
                x = random.randint(100, WINDOW_WIDTH - 100)
                y = random.randint(100, WINDOW_HEIGHT - 100)

                # Проверка, чтобы препятствия не накладывались на базы
                if (math.dist((x, y), (self.blue_base.x, self.blue_base.y)) > 100 and
                    math.dist((x, y), (self.red_base.x, self.red_base.y)) > 100):
                    break

            obstacle_type = random.choice(["tree", "rock"])
            self.obstacles.append(Obstacle(x, y, obstacle_type))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        pass

    def draw(self):
        # Отрисовка фона
        self.screen.fill(GREEN)

        # Отрисовка препятствий
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)

        # Отрисовка баз
        self.blue_base.draw(self.screen)
        self.red_base.draw(self.screen)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = GameManager()
    game.run()
    pygame.quit()
