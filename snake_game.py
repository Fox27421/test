import random
import sys
from dataclasses import dataclass
from typing import List, Tuple

import pygame


CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 22
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE
FPS = 12

BACKGROUND_COLOR = (18, 18, 18)
GRID_COLOR = (30, 30, 30)
SNAKE_COLOR = (60, 200, 80)
SNAKE_HEAD_COLOR = (90, 240, 110)
FOOD_COLOR = (220, 70, 70)
TEXT_COLOR = (240, 240, 240)


@dataclass(frozen=True)
class Point:
    x: int
    y: int

    def to_pixels(self) -> Tuple[int, int]:
        return self.x * CELL_SIZE, self.y * CELL_SIZE


DIRECTION_VECTORS = {
    pygame.K_UP: Point(0, -1),
    pygame.K_w: Point(0, -1),
    pygame.K_DOWN: Point(0, 1),
    pygame.K_s: Point(0, 1),
    pygame.K_LEFT: Point(-1, 0),
    pygame.K_a: Point(-1, 0),
    pygame.K_RIGHT: Point(1, 0),
    pygame.K_d: Point(1, 0),
}


class Snake:
    def __init__(self) -> None:
        self.body: List[Point] = [
            Point(GRID_WIDTH // 2 + i, GRID_HEIGHT // 2) for i in range(3)
        ]
        self.direction = Point(-1, 0)
        self.pending_direction = self.direction
        self.grow_pending = 0

    @property
    def head(self) -> Point:
        return self.body[0]

    def set_direction(self, direction: Point) -> None:
        if (direction.x == -self.direction.x and direction.y == -self.direction.y):
            return
        self.pending_direction = direction

    def move(self) -> None:
        self.direction = self.pending_direction
        new_head = Point(self.head.x + self.direction.x, self.head.y + self.direction.y)
        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self, amount: int = 1) -> None:
        self.grow_pending += amount

    def hits_self(self) -> bool:
        return self.head in self.body[1:]


class Food:
    def __init__(self, occupied: List[Point]) -> None:
        self.position = self._random_position(occupied)

    def relocate(self, occupied: List[Point]) -> None:
        self.position = self._random_position(occupied)

    @staticmethod
    def _random_position(occupied: List[Point]) -> Point:
        available = [
            Point(x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if Point(x, y) not in occupied
        ]
        return random.choice(available)


class SnakeGame:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Snake")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Segoe UI", 24)
        self.large_font = pygame.font.SysFont("Segoe UI", 36)
        self.reset()

    def reset(self) -> None:
        self.snake = Snake()
        self.food = Food(self.snake.body)
        self.score = 0
        self.game_over = False
        self.paused = False

    def run(self) -> None:
        while True:
            self.clock.tick(FPS)
            self.handle_events()
            if not self.game_over and not self.paused:
                self.update()
            self.draw()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in DIRECTION_VECTORS:
                    self.snake.set_direction(DIRECTION_VECTORS[event.key])
                elif event.key == pygame.K_SPACE:
                    if not self.game_over:
                        self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self.reset()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

    def update(self) -> None:
        self.snake.move()
        if not (0 <= self.snake.head.x < GRID_WIDTH and 0 <= self.snake.head.y < GRID_HEIGHT):
            self.game_over = True
            return
        if self.snake.hits_self():
            self.game_over = True
            return
        if self.snake.head == self.food.position:
            self.snake.grow(2)
            self.score += 10
            self.food.relocate(self.snake.body)

    def draw(self) -> None:
        self.screen.fill(BACKGROUND_COLOR)
        self.draw_grid()
        self.draw_food()
        self.draw_snake()
        self.draw_hud()
        if self.paused:
            self.draw_center_text("Paused", self.large_font)
        if self.game_over:
            self.draw_center_text("Game Over - Press R", self.large_font)
        pygame.display.flip()

    def draw_grid(self) -> None:
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (WINDOW_WIDTH, y))

    def draw_snake(self) -> None:
        for index, segment in enumerate(self.snake.body):
            color = SNAKE_HEAD_COLOR if index == 0 else SNAKE_COLOR
            rect = pygame.Rect(*segment.to_pixels(), CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, color, rect)

    def draw_food(self) -> None:
        rect = pygame.Rect(*self.food.position.to_pixels(), CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, FOOD_COLOR, rect)

    def draw_hud(self) -> None:
        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        controls_text = self.font.render("Arrows/WASD to move, Space pause, R restart", True, TEXT_COLOR)
        self.screen.blit(score_text, (10, 6))
        self.screen.blit(controls_text, (10, WINDOW_HEIGHT - 30))

    def draw_center_text(self, text: str, font: pygame.font.Font) -> None:
        surface = font.render(text, True, TEXT_COLOR)
        rect = surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(surface, rect)


if __name__ == "__main__":
    SnakeGame().run()
