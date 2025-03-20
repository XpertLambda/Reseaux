import pygame
from GLOBAL_VAR import *
from ImageProcessingDisplay.imagemethods import adjust_sprite

class JoinMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(MEDIEVALSHARP, 28)

        rect_width, rect_height = 500, 300
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

    def draw(self):
        screen_width, screen_height = self.screen.get_size()
        self.screen.blit(adjust_sprite(START_IMG, screen_width, screen_height), (0, 0))
        pygame.draw.rect(self.screen, (0, 0, 0), self.players_rect)

        header_text = self.font.render("IP                   Port", True, (255, 255, 255))
        self.screen.blit(header_text, (self.players_rect.x + 20, self.players_rect.y + 10))

        clip_rect = self.players_rect.copy()
        clip_rect.y += 50
        clip_rect.height -= 50
        self.screen.set_clip(clip_rect)

        for idx, (ip, port) in enumerate(ALL_IP.items()):
            y_pos = self.players_rect.y + 60 + (idx * self.line_height) - self.scroll_y
            ip_rect = pygame.Rect(self.players_rect.x + 20, y_pos, 300, self.line_height)

            # Griser si sélectionnée
            color = (100, 100, 100) if ip == self.selected_ip else (255, 255, 255)

            player_text = self.font.render(f"{ip}", True, color)
            port_text = self.font.render(f"{port}", True, color)

            self.screen.blit(player_text, (self.players_rect.x + 20, y_pos))
            self.screen.blit(port_text, (self.players_rect.x + 250, y_pos))

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

    def handle_click(self, pos):
        global SELECTED_IP

        if self.join_button.collidepoint(pos):
            if self.selected_ip is not None:
                SELECTED_IP = self.selected_ip
                print(f"IP envoyée: {self.selected_ip}")
                return self.selected_ip  # Renvoie directement l'IP sélectionnée
            else:
                print("Aucune IP sélectionnée.")
                return None

        if not self.players_rect.collidepoint(pos):
            return None

        # Gestion des clics sur les adresses IP
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
