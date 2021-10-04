from enum import Enum
from dataclasses import dataclass
from typing import Tuple
import pygame, sys
from pygame import draw
from pygame import display
from pygame import event

class Color(Enum):
    BLACK = 0, 0, 0
    WHITE = 255, 255, 255
    RED = 255, 0, 0

GridPos = Tuple[int, int]
class Grid:
    def __init__(self, num_column: int, num_row: int, block_size: float) -> None:
        self._num_column = num_column
        self._num_row = num_row
        self.block_size = block_size
 
    def reset(self):
        for x in range(0, self._num_column):
            for y in range(0, self._num_row):
                pos_x = x * self.block_size
                pos_y = y * self.block_size
                rect = pygame.Rect(pos_x, pos_y, self.block_size, self.block_size)
                draw.rect(SCREEN, Color.WHITE.value, rect, 1)
    
    def _validate_cell_pos(self, pos: GridPos):
        return pos[0] < self._num_column and pos[1] < self._num_row

    def draw_cell(self, color: Color, pos: GridPos):
        cell_game_pos_x = pos[0]*self.block_size
        cell_game_pos_y = pos[1]*self.block_size
        rect = pygame.Rect(cell_game_pos_x, cell_game_pos_y, self.block_size, self.block_size)
        SCREEN.fill(Color.BLACK.value)
        self.reset()
        draw.rect(SCREEN, color.value, rect)
        

class Shape(Enum):
    SQUARE = [[1, 1],
              [1, 1]]

class Brick:
    def __init__(self, shape: Shape) -> None:
        self.shape = shape
    # def draw()

def main():
    pygame.init()
    global SIZE, WIDTH, HEIGHT, SPEED, BLACK, WHITE, SCREEN
    SIZE = WIDTH, HEIGHT = 320, 480
    SPEED = [2, 2]
    SCREEN = display.set_mode(SIZE)
    SCREEN.fill(Color.BLACK.value)
    grid = Grid(10, 24, 20)
    grid.reset()
    pos = (1, 1)

    while True:
        grid.draw_cell(Color.RED, pos)
        for e in event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_DOWN:
                    pos = (pos[0], pos[1] + 1)
                if e.key == pygame.K_UP:
                    pos = (pos[0], pos[1] - 1)
        
        display.flip()


if __name__ == "__main__":
    main()
