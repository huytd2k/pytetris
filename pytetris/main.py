from enum import Enum
from typing import List

import pygame, sys
from pygame import draw
from pygame import display
from pygame import event

class Color(Enum):
    BLACK = 0, 0, 0
    WHITE = 255, 255, 255

class Grid:
    def __init__(self, num_column: int, num_row: int, block_size: float) -> None:
        self._num_column = num_column
        self._num_row = num_row
        self.block_size = block_size
        self.colors: List[List[Color]] = [[Color.WHITE for _ in range(num_column)] for _ in range(num_row)]
 
    def draw(self):
        for x in range(0, self._num_column):
            for y in range(0, self._num_row):
                pos_x = x * self.block_size
                pos_y = y * self.block_size
                rect = pygame.Rect(pos_x, pos_y, self.block_size, self.block_size)
                draw.rect(SCREEN, self.colors[y][x].value, rect)

    def update_color(self, color: Color, row: int, col: int):
        self.colors[row][col] = color


def main():
    pygame.init()
    global SIZE, WIDTH, HEIGHT, SPEED, BLACK, WHITE, SCREEN
    SIZE = WIDTH, HEIGHT = 320, 480
    SPEED = [2, 2]
    BLACK = 0, 0, 0
    WHITE = 255, 255, 255
    SCREEN = display.set_mode(SIZE)
    SCREEN.fill(BLACK)

    while True:
        grid = Grid(3, 5, 20)
        grid.update_color(Color.BLACK, 0, 1)
        grid.draw()
        for e in event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
        
        display.update()


if __name__ == "__main__":
    main()
