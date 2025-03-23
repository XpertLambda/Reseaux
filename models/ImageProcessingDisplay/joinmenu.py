import pygame
from GLOBAL_VAR import *
from ImageProcessingDisplay.imagemethods import adjust_sprite

class JoinMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(MEDIEVALSHARP, 22)

        rect_width, rect_height = 600, 350
        self.players_rect = pygame.Rect(
            (screen.get_width() - rect_width) // 2,
            (screen.get_height() - rect_height) // 2,
            rect_width,
            rect_height
        )

        self.join_button = pygame.Rect(
            screen.get_width() // 2 - 75,
            self.players_rect.bottom + 20,
            150,
            50
        )

        self.back_button = pygame.Rect(20, 20, 50, 50)

        self.scroll_y = 0
        self.max_visible_lines = 6
        self.line_height = 40
        self.slider_rect = pygame.Rect(
            self.players_rect.right - 20,
            self.players_rect.y,
            20,
            self.players_rect.height
        )

        self.selected_ip = None

    def generate_color(self, port, taille, mode, joueurs):
        seed = hash(f"{port}-{taille}-{mode}-{joueurs}")
        r = (seed & 0xFF0000) >> 16
        g = (seed & 0x00FF00) >> 8
        b = seed & 0x0000FF
        return (r % 256, g % 256, b % 256)

    def draw(self):
        screen_width, screen_height = self.screen.get_size()
        self.screen.blit(adjust_sprite(START_IMG, screen_width, screen_height), (0, 0))
        pygame.draw.rect(self.screen, (0, 0, 0), self.players_rect)

        # Positions des colonnes
        columns_x = [self.players_rect.x + x for x in [10, 140, 240, 360, 480]]
        headers = ["IP", "Port", "Size", "Mode", "Player"]

        # Affichage des titres
        header_y = self.players_rect.y + 10
        for i, header in enumerate(headers):
            text = self.font.render(header, True, (255, 255, 255))
            self.screen.blit(text, text.get_rect(centerx=columns_x[i] + 50, y=header_y))

        clip_rect = self.players_rect.copy()
        clip_rect.y += 50
        clip_rect.height -= 50
        self.screen.set_clip(clip_rect)

        for idx, (ip, data) in enumerate(ALL_IP.items()):
            port, taille, mode, joueurs = data
            y_pos = self.players_rect.y + 60 + (idx * self.line_height) - self.scroll_y

            # Couleur unique par partie
            color = self.generate_color(port, taille, mode, joueurs)
            if ip == self.selected_ip:
                color = (200, 200, 200)  # Couleur spéciale pour sélection

            items = [ip, str(port), taille, mode, str(joueurs)]
            for i, item in enumerate(items):
                text = self.font.render(item, True, color)
                self.screen.blit(text, text.get_rect(centerx=columns_x[i] + 50, y=y_pos))

        self.screen.set_clip(None)

        # Slider
        total_lines = len(ALL_IP)
        total_height = total_lines * self.line_height + 60
        if total_height > self.players_rect.height:
            slider_height = max(self.players_rect.height * (self.max_visible_lines / total_lines), 30)
            slider_y = self.players_rect.y + (self.scroll_y / (total_height - self.players_rect.height)) * (self.players_rect.height - slider_height)
            pygame.draw.rect(self.screen, (100, 100, 100), (self.slider_rect.x, slider_y, self.slider_rect.width, slider_height))

        pygame.draw.rect(self.screen, (128, 128, 128), self.join_button)
        join_text = self.font.render("Join", True, (255, 255, 255))
        self.screen.blit(join_text, join_text.get_rect(center=self.join_button.center))

        # Bouton retour (flèche)
        pygame.draw.polygon(self.screen, (128, 128, 128), [
            (self.back_button.x + 35, self.back_button.y + 10),
            (self.back_button.x + 15, self.back_button.y + 25),
            (self.back_button.x + 35, self.back_button.y + 40)
        ])

    def handle_click(self, pos, game_state):
        global SELECTED_IP

        if self.back_button.collidepoint(pos):
            game_state.go_to_main_menu()
            return None

        if self.join_button.collidepoint(pos):
            if self.selected_ip is not None:
                SELECTED_IP = self.selected_ip
                print(f"IP envoyée: {self.selected_ip}")
                return self.selected_ip
            else:
                print("Aucune IP sélectionnée.")
                return None

        if not self.players_rect.collidepoint(pos):
            return None

        for idx, ip in enumerate(ALL_IP.keys()):
            y_pos = self.players_rect.y + 60 + (idx * self.line_height) - self.scroll_y
            ip_rect = pygame.Rect(self.players_rect.x, y_pos, self.players_rect.width, self.line_height)

            if ip_rect.collidepoint(pos):
                self.selected_ip = ip
                SELECTED_IP = ip
                break

        return None

    def scroll(self, direction):
        total_height = len(ALL_IP) * self.line_height + 60
        if total_height > self.players_rect.height:
            self.scroll_y -= direction * 20
            self.scroll_y = max(0, min(self.scroll_y, total_height - self.players_rect.height))
