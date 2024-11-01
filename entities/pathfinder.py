from typing import List, Tuple
import numpy as np
import heapq
from game_system.config import WINDOW_WIDTH, WINDOW_HEIGHT

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
