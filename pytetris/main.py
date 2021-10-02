import pygame, sys
from pygame import draw
from pygame import display
from pygame import event
from pygame.constants import QUIT

pygame.init()

size = width, height = 320, 480
speed = [2, 2]
black = 0, 0, 0
white = 255, 255, 255

screen = display.set_mode(size)
screen.fill(black)

def drawGrid(block_size: int):
    for x in range(0, width, block_size):
        for y in range(0, height, block_size):
            rect = pygame.Rect(x, y, block_size, block_size)
            draw.rect(screen, white, rect, 1)

while True:
    drawGrid(20)
    for e in event.get():
        if e.type == pygame.QUIT: sys.exit(0)
    
    display.update()