import pygame
from ImageProcessingDisplay.imagemethods import adjust_sprite
from GLOBAL_VAR import START_IMG, MEDIEVALSHARP

class MultiplayerMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(MEDIEVALSHARP, 28)

        self.buttons = {
            "create": pygame.Rect(screen.get_width()//2 - 150, screen.get_height()//2 - 80, 300, 50),
            "join": pygame.Rect(screen.get_width()//2 - 150, screen.get_height()//2 + 20, 300, 50)
        }

    def draw(self):
        self.screen.blit(adjust_sprite(START_IMG, self.screen.get_width(), self.screen.get_height()), (0,0))

        # Draw buttons
        pygame.draw.rect(self.screen, (180, 180, 180), self.buttons["create"])
        pygame.draw.rect(self.screen, (180, 180, 180), self.buttons["join"])

        create_text = self.font.render("Create Party", True, (0, 0, 0))
        join_text = self.font.render("Join Party", True, (0, 0, 0))

        self.screen.blit(create_text, create_text.get_rect(center=self.buttons["create"].center))
        self.screen.blit(join_text, join_text.get_rect(center=self.buttons["join"].center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if self.buttons["create"].collidepoint(mouse_pos):
                return "create"
            elif self.buttons["join"].collidepoint(mouse_pos):
                return "join"
        return None
