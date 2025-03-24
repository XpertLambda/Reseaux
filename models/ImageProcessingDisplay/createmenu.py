import pygame
from GLOBAL_VAR import *
from ImageProcessingDisplay.imagemethods import adjust_sprite

class CreateMenu:
    def __init__(self, screen, game_state):
        self.screen = screen
        self.game_state = game_state

        self.map_cell_count_x = 250
        self.map_cell_count_y = 250
        self.editing_map_cell_count_x = False
        self.editing_map_cell_count_y = False

        self.map_options = ["Carte Normal", "Carte Centrée"]
        self.selected_map_index = MAP_NORMAL

        self.game_mode_options = ["Lean", "Mean", "Marines"]
        self.selected_mode_index = LEAN

        self.selected_player_count = 2
        self.editing_player_count = False

        self.display_mode = ISO2D

        # Boutons
        self.back_button = pygame.Rect(20, 20, 50, 50)

        self.buttons = {
            "left_map_x": pygame.Rect(0, 0, 50, 50),
            "right_map_x": pygame.Rect(0, 0, 50, 50),
            "left_map_y": pygame.Rect(0, 0, 50, 50),
            "right_map_y": pygame.Rect(0, 0, 50, 50),
            "left_map": pygame.Rect(0, 0, 50, 50),
            "right_map": pygame.Rect(0, 0, 50, 50),
            "left_mode": pygame.Rect(0, 0, 50, 50),
            "right_mode": pygame.Rect(0, 0, 50, 50),
            "left_player_count": pygame.Rect(0, 0, 50, 50),
            "right_player_count": pygame.Rect(0, 0, 50, 50),
            "Terminal": pygame.Rect(0, 0, 115, 50),
            "2.5D": pygame.Rect(0, 0, 115, 50),
            "Lancer la Partie": pygame.Rect(0, 0, 300, 50)
        }

        # Volume slider (lié au game_state.volume)
        self.slider_rect = pygame.Rect(screen.get_width() - 320, screen.get_height() - 50, 300, 10)
        self.slider_thumb_rect = pygame.Rect(
            self.slider_rect.x + int(self.game_state.volume * 300),
            self.slider_rect.y - 5,
            10,
            20
        )

    def draw(self):
        self.screen.fill((255, 255, 255))
        screen_width, screen_height = self.screen.get_size()
        self.screen.blit(adjust_sprite(START_IMG, screen_width, screen_height), (0, 0))

        self.slider_rect.topleft = (screen_width - 320, screen_height - 50)
        self.slider_thumb_rect.topleft = (
            self.slider_rect.x + int(self.game_state.volume * self.slider_rect.width),
            self.slider_rect.y - 5
        )

        center_x = screen_width // 2
        center_y = screen_height // 2

        self.buttons["left_map_x"].topleft = (center_x - 215, center_y - 260)
        self.buttons["right_map_x"].topleft = (center_x + 165, center_y - 260)
        self.buttons["left_map_y"].topleft = (center_x - 215, center_y - 200)
        self.buttons["right_map_y"].topleft = (center_x + 165, center_y - 200)
        self.buttons["left_map"].topleft = (center_x - 215, center_y - 140)
        self.buttons["right_map"].topleft = (center_x + 165, center_y - 140)
        self.buttons["left_mode"].topleft = (center_x - 215, center_y - 80)
        self.buttons["right_mode"].topleft = (center_x + 165, center_y - 80)
        self.buttons["left_player_count"].topleft = (center_x - 215, center_y - 20)
        self.buttons["right_player_count"].topleft = (center_x + 165, center_y - 20)
        self.buttons["Terminal"].topleft = (center_x - 120, center_y + 40)
        self.buttons["2.5D"].topleft = (center_x + 5, center_y + 40)
        self.buttons["Lancer la Partie"].topleft = (center_x - 150, center_y + 100)

        # Map Cell Count X
        self._draw_button("left_map_x", "<")
        label_x = f"Cellules X: {self.map_cell_count_x}" if not self.editing_map_cell_count_x else "Cellules X: _"
        self._draw_text(label_x, (center_x, center_y - 245), centered=True)
        self._draw_button("right_map_x", ">")

        # Map Cell Count Y
        self._draw_button("left_map_y", "<")
        label_y = f"Cellules Y: {self.map_cell_count_y}" if not self.editing_map_cell_count_y else "Cellules Y: _"
        self._draw_text(label_y, (center_x, center_y - 185), centered=True)
        self._draw_button("right_map_y", ">")

        # Map Type
        self._draw_button("left_map", "<")
        map_label = f"Carte: {self.map_options[self.selected_map_index]}"
        self._draw_text(map_label, (center_x, center_y - 125), centered=True)
        self._draw_button("right_map", ">")

        # Mode
        self._draw_button("left_mode", "<")
        mode_label = f"Mode: {self.game_mode_options[self.selected_mode_index]}"
        self._draw_text(mode_label, (center_x, center_y - 65), centered=True)
        self._draw_button("right_mode", ">")

        # Joueurs
        self._draw_button("left_player_count", "<")
        player_label = f"Joueurs: {self.selected_player_count}" if not self.editing_player_count else "Joueurs: _"
        self._draw_text(player_label, (center_x, center_y - 5), centered=True)
        self._draw_button("right_player_count", ">")

        # Affichage
        self._draw_button("Terminal", "Terminal", self.display_mode == TERMINAL)
        self._draw_button("2.5D", "2.5D", self.display_mode == ISO2D)

        self._draw_button("Lancer la Partie", "Lancer la Partie")

        self._draw_slider()

        pygame.draw.polygon(self.screen, (128, 128, 128), [
            (self.back_button.x + 35, self.back_button.y + 10),
            (self.back_button.x + 15, self.back_button.y + 25),
            (self.back_button.x + 35, self.back_button.y + 40)
        ])

    def handle_click(self, pos, game_state):
        if self.back_button.collidepoint(pos):
            game_state.go_to_main_menu()
            return None

        if self.buttons["left_map_x"].collidepoint(pos):
            self.map_cell_count_x = max(120, self.map_cell_count_x - 5)
        elif self.buttons["right_map_x"].collidepoint(pos):
            self.map_cell_count_x = min(1020, self.map_cell_count_x + 5)
        elif self.buttons["left_map_y"].collidepoint(pos):
            self.map_cell_count_y = max(120, self.map_cell_count_y - 5)
        elif self.buttons["right_map_y"].collidepoint(pos):
            self.map_cell_count_y = min(1020, self.map_cell_count_y + 5)
        elif self.buttons["left_map"].collidepoint(pos):
            self.selected_map_index = (self.selected_map_index - 1) % len(self.map_options)
        elif self.buttons["right_map"].collidepoint(pos):
            self.selected_map_index = (self.selected_map_index + 1) % len(self.map_options)
        elif self.buttons["left_mode"].collidepoint(pos):
            self.selected_mode_index = (self.selected_mode_index - 1) % len(self.game_mode_options)
        elif self.buttons["right_mode"].collidepoint(pos):
            self.selected_mode_index = (self.selected_mode_index + 1) % len(self.game_mode_options)
        elif self.buttons["left_player_count"].collidepoint(pos):
            self.selected_player_count = max(2, self.selected_player_count - 1)
        elif self.buttons["right_player_count"].collidepoint(pos):
            self.selected_player_count += 1
        elif self.buttons["Terminal"].collidepoint(pos):
            self.display_mode = TERMINAL
        elif self.buttons["2.5D"].collidepoint(pos):
            self.display_mode = ISO2D
        elif self.buttons["Lancer la Partie"].collidepoint(pos):
            return True

        if self.slider_rect.collidepoint(pos):
            self.game_state.volume = max(0.0, min(1.0, (pos[0] - self.slider_rect.x) / self.slider_rect.width))
            self.slider_thumb_rect.x = self.slider_rect.x + int(self.game_state.volume * self.slider_rect.width)
            pygame.mixer.music.set_volume(self.game_state.volume)

        return False

    def _draw_slider(self):
        pygame.draw.rect(self.screen, (200, 200, 200), self.slider_rect)
        pygame.draw.rect(self.screen, (0, 0, 255), self.slider_thumb_rect)
        volume_text = f"Volume: {int(self.game_state.volume * 100)}%"
        font = pygame.font.Font(MEDIEVALSHARP, 28)
        text = font.render(volume_text, True, WHITE_COLOR)
        self.screen.blit(text, text.get_rect(center=(self.slider_rect.centerx, self.slider_rect.bottom + 10)))

    def _draw_button(self, key, text, selected=False):
        rect = self.buttons[key]
        color = (0, 128, 0) if selected else (128, 128, 128)
        pygame.draw.rect(self.screen, color, rect)
        font = pygame.font.Font(MEDIEVALSHARP, 28)
        button_text = font.render(text, True, (255, 255, 255))
        self.screen.blit(button_text, button_text.get_rect(center=rect.center))

    def _draw_text(self, text, pos, centered=False):
        font = pygame.font.Font(MEDIEVALSHARP, 28)
        rendered_text = font.render(text, True, WHITE_COLOR)
        text_rect = rendered_text.get_rect(center=pos if centered else None)
        self.screen.blit(rendered_text, text_rect if centered else pos)

    def handle_keydown(self, event):
        if self.editing_map_cell_count_x:
            if event.key == pygame.K_RETURN:
                self.editing_map_cell_count_x = False
                self.map_cell_count_x = min(1020, max(120, self.map_cell_count_x))
                self.map_cell_count_x = (self.map_cell_count_x // 5) * 5
            elif event.key == pygame.K_BACKSPACE:
                self.map_cell_count_x = int(str(self.map_cell_count_x)[:-1] or "120")
            elif event.unicode.isdigit():
                self.map_cell_count_x = self.map_cell_count_x * 10 + int(event.unicode)

        elif self.editing_map_cell_count_y:
            if event.key == pygame.K_RETURN:
                self.editing_map_cell_count_y = False
                self.map_cell_count_y = min(1020, max(120, self.map_cell_count_y))
                self.map_cell_count_y = (self.map_cell_count_y // 5) * 5
            elif event.key == pygame.K_BACKSPACE:
                self.map_cell_count_y = int(str(self.map_cell_count_y)[:-1] or "120")
            elif event.unicode.isdigit():
                self.map_cell_count_y = self.map_cell_count_y * 10 + int(event.unicode)

        elif self.editing_player_count:
            if event.key == pygame.K_RETURN:
                self.editing_player_count = False
                self.selected_player_count = min(20, max(2, self.selected_player_count))
            elif event.key == pygame.K_BACKSPACE:
                self.selected_player_count = int(str(self.selected_player_count)[:-1] or "2")
            elif event.unicode.isdigit():
                self.selected_player_count = self.selected_player_count * 10 + int(event.unicode)

    def start_editing_map_cell_count_x(self):
        self.editing_map_cell_count_x = True
        self.map_cell_count_x = 0

    def start_editing_map_cell_count_y(self):
        self.editing_map_cell_count_y = True
        self.map_cell_count_y = 0

    def start_editing_player_count(self):
        self.editing_player_count = True
        self.selected_player_count = 0
