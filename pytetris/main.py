import pygame, sys
from pygame import draw
from pygame import display
from pygame import event

def drawGrid(block_size: int):
    for x in range(0, WIDTH, block_size):
        for y in range(0, HEIGHT, block_size):
            rect = pygame.Rect(x, y, block_size, block_size)
            draw.rect(SCREEN, WHITE, rect, 1)

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
        drawGrid(20)
        for e in event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
        
        display.update()