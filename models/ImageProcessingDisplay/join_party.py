import pygame
from ImageProcessingDisplay.imagemethods import adjust_sprite
from GLOBAL_VAR import *

class JoinPartyMenu:
    def __init__(self, screen):
        self.screen = screen

    def draw(self):
        self.screen.blit(adjust_sprite(START_IMG, self.screen.get_width(), self.screen.get_height()), (0,0))

        # Carré noir central
        rect_width, rect_height = 500, 300
        rect_x = (self.screen.get_width() - rect_width) // 2
        rect_y = (self.screen.get_height() - rect_height) // 2
        pygame.draw.rect(self.screen, (0, 0, 0), (rect_x, rect_y, rect_width, rect_height))

    def handle_event(self, event):
        pass
