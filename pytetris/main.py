import random
import sys
from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Iterator, List, Tuple

import numpy as np
import pygame
from pygame import Vector2, display, draw, event, time


class Color(Enum):
    BLACK = 0, 0, 0
    WHITE = 255, 255, 255


class BlockColor(Enum):
    RED = 255, 0, 0
    GREEN = 0, 255, 0
    BLUE = 0, 255, 255


class Element(metaclass=ABCMeta):
    @abstractmethod
    def draw(self):
        pass


class Grid(Element):
    def __init__(self, num_column: int, num_row: int, block_size: float) -> None:
        self._num_column = num_column
        self._num_row = num_row
        self.block_size = block_size
        self.states = [[0 for _ in range(num_column)] for _ in range(num_row)]
        self.color_storage = {}

    def draw(self):
        for x in range(0, self._num_column):
            for y in range(0, self._num_row):
                pos_x = x * self.block_size
                pos_y = y * self.block_size
                rect = pygame.Rect(pos_x, pos_y, self.block_size, self.block_size)
                draw.rect(SCREEN, Color.WHITE.value, rect, 1)
                if self.states[y][x] != 0:
                    rect = pygame.Rect(pos_x, pos_y, self.block_size, self.block_size)
                    draw.rect(SCREEN, self.color_storage[self.states[y][x]], rect)


class Shape(Enum):
    SQUARE = [[1, 1], [1, 1]]
    L_SHAPE = [[1, 0], [1, 0], [1, 1]]
    STICK = [[1], [1], [1]]
    Z = [[1, 1, 0], [0, 1, 1]]
    THERE_WAY = [[0, 1, 0], [1, 1, 1]]


def shape_val_iter(shape: List[List[int]]) -> Iterator[Tuple[int, int]]:
    for y, layer in enumerate(shape):
        for x, val in enumerate(layer):
            if val == 1:
                yield (x, y)


class Brick(Element):
    def __init__(
        self,
        init_pos: Vector2,
        block_size: float,
        color: Color,
        in_grid: Grid,
        shape: Shape,
        id: int,
    ) -> None:
        self.id = id
        self.pos = init_pos
        self.block_size = block_size
        self.color_val = color.value
        self.grid = in_grid
        self.shape = shape.value
        self.visiable = True
        self.played = False
        self.grid.color_storage[id] = self.color_val

    def bodies(self) -> Iterator[Vector2]:
        if not self.played:
            for x, y in shape_val_iter(self.shape):
                yield Vector2(self.pos.x + x, y + self.pos.y)

    def rotate(self):
        retoted_shape = np.rot90(np.array(self.shape)).tolist()
        if self.check_pos_in_grid(self.pos, next_shape=retoted_shape):
            for x, y in shape_val_iter(self.shape):
                self.grid.states[int(y + self.pos.y)][int(x + self.pos.x)] = 0
            self.shape = retoted_shape
            for x, y in shape_val_iter(self.shape):
                self.grid.states[int(y + self.pos.y)][int(x + self.pos.x)] = self.id

    def draw(self):
        pass

    def check_pos_in_grid(self, pos: Vector2, next_shape: List[List[int]] = None):
        shape = self.shape if next_shape is None else next_shape
        for x, y in shape_val_iter(shape):
            acc_x = int(x + pos.x)
            acc_y = int(y + pos.y)
            if acc_y < 0:
                continue
            if (
                acc_x >= self.grid._num_column
                or acc_y >= self.grid._num_row
                or acc_x < 0
                or acc_y < 0
                or self.grid.states[acc_y][acc_x] not in (0, self.id)
            ):
                return False
        return True

    def update_pos_if_valid(self, pos: Vector2):
        if self.check_pos_in_grid(pos):
            for x, y in shape_val_iter(self.shape):
                if y + pos.y >= 0:
                    self.grid.states[int(y + self.pos.y)][int(x + self.pos.x)] = 0
            self.pos = pos
            for x, y in shape_val_iter(self.shape):
                if y + pos.y >= 0:
                    self.grid.states[int(y + pos.y)][int(x + pos.x)] = self.id
            return True
        return False

    def move_down(self):
        if self.update_pos_if_valid(self.pos + Vector2(0, 1)) is False:
            event.post(event.Event(PLAYED_A_BLOCK))
            self.played = True

    def move_up(self):
        self.update_pos_if_valid(self.pos - Vector2(0, 1))

    def move_right(self):
        self.update_pos_if_valid(self.pos + Vector2(1, 0))

    def move_left(self):
        self.update_pos_if_valid(self.pos - Vector2(1, 0))


class Game:
    def __init__(self, grid: Grid) -> None:
        self.elements: List[Element] = [
            grid,
        ]
        self.grid = grid
        self.cur_control_ele: Brick = None
        self.block_id = 1

    def add_elements(self, *ele: Element):
        self.elements.extend(ele)

    def draw(self):
        for e in self.elements:
            e.draw()

    def update(self):
        self.cur_control_ele.move_down()

    def spawn_block(self):
        block = Brick(
            Vector2(4, 0),
            20,
            random.choice(list(BlockColor)),
            self.grid,
            random.choice(list(Shape)),
            self.block_id,
        )
        for pos in block.bodies():
            if self.grid.states[int(pos.y)][int(pos.x)] != 0:
                event.post(event.Event(GAMEOVER))
        self.add_elements(block)
        self.cur_control_ele = block
        self.block_id += 1

    def handle_grid_state(self):
        for idx, row in enumerate(self.grid.states):
            if all((i != 0 for i in row)):
                self.grid.states.pop(idx)
                self.grid.states.insert(0, [0 for _ in range(self.grid._num_column)])


def init_game() -> Game:
    grid = Grid(10, 24, 20)
    game = Game(grid)
    game.spawn_block()
    return game


PLAYED_A_BLOCK = pygame.USEREVENT
GAMEOVER = pygame.USEREVENT + 1
STATE_UPDATE = pygame.USEREVENT + 2


def main():
    pygame.init()
    global SIZE, WIDTH, HEIGHT, SPEED, SCREEN
    SIZE = WIDTH, HEIGHT = 320, 480
    SPEED = [2, 2]
    SCREEN = display.set_mode(SIZE)
    SCREEN.fill(Color.BLACK.value)
    clock = time.Clock()
    game = init_game()
    time.set_timer(STATE_UPDATE, 150)

    while True:
        for e in event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if e.type == GAMEOVER:
                game = init_game()
            if e.type == PLAYED_A_BLOCK:
                game.handle_grid_state()
                game.spawn_block()
            if e.type == STATE_UPDATE:
                game.update()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_LEFT:
                    game.cur_control_ele.move_left()
                if e.key == pygame.K_RIGHT:
                    game.cur_control_ele.move_right()
                if e.key == pygame.K_UP:
                    game.cur_control_ele.rotate()

        SCREEN.fill(Color.BLACK.value)
        game.draw()
        display.flip()
        clock.tick(30)


if __name__ == "__main__":
    main()
