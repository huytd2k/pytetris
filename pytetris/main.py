import random
import sys
from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Iterator, List, Tuple

import numpy as np
import pygame
from pygame import Vector2, display, draw, event, time
from pygame import mixer


class Color(Enum):
    BLACK = 0, 0, 0
    WHITE = 185, 210, 218
    LIGHT_GREY = 200, 200, 200
    DARK_GREY = 29, 28, 26


class BlockColor(Enum):
    RED = 255, 105, 97	
    GREEN = 119, 221, 119
    YELLOW = 253, 253, 150	
    PURPLE = 179, 158, 181	


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
                draw.rect(SCREEN, Color.LIGHT_GREY.value, rect, 1)
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

def set_text(string, coordx, coordy, fontSize = 35): #Function to set text
    font = pygame.font.Font("pixel.ttf", fontSize) 
    text = font.render(string, True, (0, 0, 0)) 
    textRect = text.get_rect()
    textRect.center = (coordx, coordy) 
    return (text, textRect)

class Game:
    def __init__(self, grid: Grid) -> None:
        self.elements: List[Element] = [
            grid,
        ]
        self.grid = grid
        self.cur_control_ele: Brick = None
        self.block_id = 1
        self.speed = 4
        self.track = 0
        self.score = 0

    def add_elements(self, *ele: Element):
        self.elements.extend(ele)

    def draw(self):
        for e in self.elements:
            e.draw()
        totalText = set_text(f"Score: {self.score}", 250, 250, 20)
        SCREEN.blit(totalText[0], totalText[1])

    def update(self):
        self.track += 1
        if self.track == self.speed:
            self.cur_control_ele.move_down()
            self.track = 0
    
    def set_speed(self, speed: int):
        self.track = 0
        self.speed = speed

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
                return True
        self.add_elements(block)
        self.cur_control_ele = block
        self.block_id += 1
        return False

    def handle_grid_state(self) -> bool:
        scored = False
        for idx, row in enumerate(self.grid.states):
            if all((i != 0 for i in row)):
                self.grid.states.pop(idx)
                self.grid.states.insert(0, [0 for _ in range(self.grid._num_column)])
                self.score += 100
                scored = True
        return scored
    


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
    time.set_timer(STATE_UPDATE, 50)
    while True:
        for e in event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if e.type == GAMEOVER:
                mixer.music.load('game_over.ogg')
                pygame.mixer.music.play(0)
                game = init_game()
            if e.type == PLAYED_A_BLOCK:
                scored = game.handle_grid_state()
                is_game_over = game.spawn_block()
                if scored:
                    mixer.music.load('played_a_block2.ogg')
                    pygame.mixer.music.play(0)
                else:
                    if not is_game_over:
                        mixer.music.load('played_a_block.ogg')
                        pygame.mixer.music.play(0)
            if e.type == STATE_UPDATE:
                game.update()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_LEFT:
                    game.cur_control_ele.move_left()
                if e.key == pygame.K_RIGHT:
                    game.cur_control_ele.move_right()
                if e.key == pygame.K_UP:
                    game.cur_control_ele.rotate()
                if e.key == pygame.K_DOWN:
                    game.set_speed(1)
            if e.type == pygame.KEYUP:
                if e.key == pygame.K_DOWN:
                    game.set_speed(4)

        SCREEN.fill(Color.WHITE.value)
        game.draw()
        display.flip()
        clock.tick(30)


if __name__ == "__main__":
    main()
