import pygame, sys, os
from pygame.locals import *
pygame.init()

screen = pygame.display.set_mode((1088,800))
floor = pygame.image.load(os.path.join("floor4.png"))
floor = pygame.transform.scale(floor, (1088,800))

while True:
    screen.blit(floor,(0,0))
    pygame.display.flip()

pygame.quit()
