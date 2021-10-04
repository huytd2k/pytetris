from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import List, Tuple
import pygame, sys
from pygame import Vector2, draw, init
from pygame import display
from pygame import event
from pygame import time
from pygame.transform import scale

class Color(Enum):
    BLACK = 0, 0, 0
    WHITE = 255, 255, 255
    RED = 255, 0, 0

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
 
    def draw(self):
        for x in range(0, self._num_column):
            for y in range(0, self._num_row):
                pos_x = x * self.block_size
                pos_y = y * self.block_size
                rect = pygame.Rect(pos_x, pos_y, self.block_size, self.block_size)
                draw.rect(SCREEN, Color.WHITE.value, rect, 1)
    
def check_pos_in_grid(grid: Grid, pos: Vector2):
    return pos.x < grid._num_column and pos.y < grid._num_row and pos.x >= 0 and pos.y >= 0
    
class Block(Element):
    def __init__(self, init_pos: Vector2, block_size: float, color: Color, in_grid: Grid) -> None:
        self.pos = init_pos
        self.block_size = block_size
        self.color_val = color.value
        self.grid = in_grid

    def draw(self):
        rect = pygame.Rect(self.pos.x*self.block_size, self.pos.y*self.block_size, self.block_size, self.block_size)
        draw.rect(SCREEN, self.color_val, rect)
    
    def update_pos_if_valid(self, pos: Vector2):
        if check_pos_in_grid(self.grid, pos):
            self.pos = pos
    
    def move_down(self):
        self.update_pos_if_valid(self.pos + Vector2(0, 1))

    def move_up(self):
        self.update_pos_if_valid(self.pos - Vector2(0, 1))

    def move_right(self):
        self.update_pos_if_valid(self.pos + Vector2(1, 0))
        
    def move_left(self):
        self.update_pos_if_valid(self.pos - Vector2(1, 0))

class Game:
    def __init__(self, grid: Grid) -> None:
        self.elements: List[Element] = [grid,]
        self.grid = grid
        self.cur_control_ele: Block = None

    def add_elements(self, *ele: Element):
        self.elements.extend(ele)

    def draw(self):
        for e in self.elements:
            e.draw()

    def update(self):
        for e in self.elements:
            if isinstance(e, Block):
                e.move_down()

def init_game() -> Game:
    grid = Grid(10, 24, 20)
    game = Game(grid)
    block = Block(Vector2(1, 1), 20, Color.RED, grid)
    game.add_elements(block)
    game.cur_control_ele = block
    return game


def main():
    pygame.init()
    global SIZE, WIDTH, HEIGHT, SPEED, SCREEN
    SIZE = WIDTH, HEIGHT = 320, 480
    SPEED = [2, 2]
    SCREEN = display.set_mode(SIZE)
    SCREEN.fill(Color.BLACK.value)
    clock = time.Clock()
    game = init_game()
    STATE_UPDATE = pygame.USEREVENT
    time.set_timer(STATE_UPDATE, 150)

    while True:
        for e in event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if e.type == STATE_UPDATE:
                game.update()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_LEFT:
                    game.cur_control_ele.move_left()
                if e.key == pygame.K_RIGHT:
                    game.cur_control_ele.move_right()
        
        SCREEN.fill(Color.BLACK.value)
        game.draw()
        display.flip()
        clock.tick(30)


if __name__ == "__main__":
    main()
