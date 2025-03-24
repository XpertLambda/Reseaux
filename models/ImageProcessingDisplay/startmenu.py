import pygame
from GLOBAL_VAR import *
from ImageProcessingDisplay.imagemethods import adjust_sprite

class StartMenu:
    def __init__(self, screen, game_state):
        self.screen = screen
        self.game_state = game_state
        self.font = pygame.font.Font(MEDIEVALSHARP, 28)

        self.buttons = {
            "create": pygame.Rect(screen.get_width()//2 - 150, screen.get_height()//2 - 80, 300, 50),
            "discover": pygame.Rect(screen.get_width()//2 - 150, screen.get_height()//2 + 20, 300, 50)
        }

        # Slider volume (contrôle via game_state.volume)
        self.slider_rect = pygame.Rect(screen.get_width() - 320, screen.get_height() - 50, 300, 10)
        self.slider_thumb_rect = pygame.Rect(
            self.slider_rect.x + int(self.game_state.volume * 300),
            self.slider_rect.y - 5,
            10,
            20
        )

    def draw(self):
        self.screen.blit(adjust_sprite(START_IMG, self.screen.get_width(), self.screen.get_height()), (0, 0))

        # Affichage boutons Create / Join
        pygame.draw.rect(self.screen, (180, 180, 180), self.buttons["create"])
        pygame.draw.rect(self.screen, (180, 180, 180), self.buttons["discover"])
        self._draw_text("Create Party", self.buttons["create"].center, centered=True)
        self._draw_text("Discover Game", self.buttons["discover"].center, centered=True)

        # Mise à jour dynamique du slider volume (position bas droite)
        self.slider_rect.topleft = (self.screen.get_width() - 320, self.screen.get_height() - 50)
        self.slider_thumb_rect.topleft = (
            self.slider_rect.x + int(self.game_state.volume * self.slider_rect.width),
            self.slider_rect.y - 5
        )
        self._draw_slider()

    def handle_click(self, pos, game_state):
        if self.buttons["create"].collidepoint(pos):
            print("Create Party clicked")
            game_state.go_to_create_menu()

        elif self.buttons["discover"].collidepoint(pos):
            print("Join Party clicked")
            game_state.go_to_discover_menu()
            return "join"

        # Volume slider interaction (clic simple uniquement)
        if self.slider_rect.collidepoint(pos):
            self.game_state.volume = max(0.0, min(1.0, (pos[0] - self.slider_rect.x) / self.slider_rect.width))
            self.slider_thumb_rect.x = self.slider_rect.x + int(self.game_state.volume * self.slider_rect.width)
            pygame.mixer.music.set_volume(self.game_state.volume)

        return None

    def _draw_slider(self):
        pygame.draw.rect(self.screen, (200, 200, 200), self.slider_rect)
        pygame.draw.rect(self.screen, (0, 0, 255), self.slider_thumb_rect)
        volume_text = f"Volume: {int(self.game_state.volume * 100)}%"
        self._draw_text(volume_text, (self.slider_rect.centerx, self.slider_rect.bottom + 10), centered=True)

    def _draw_text(self, text, pos, centered=False):
        rendered_text = self.font.render(text, True, WHITE_COLOR)
        text_rect = rendered_text.get_rect(center=pos if centered else None)
        self.screen.blit(rendered_text, text_rect if centered else pos)
