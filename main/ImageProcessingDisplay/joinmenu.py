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

    def draw(self):
        screen_width, screen_height = self.screen.get_size()
        self.screen.blit(adjust_sprite(START_IMG, screen_width, screen_height), (0, 0))
        pygame.draw.rect(self.screen, (0, 0, 0), self.players_rect)

        # Position de départ pour les colonnes
        ip_x = self.players_rect.x + 10
        port_x = ip_x + 140
        taille_x = port_x + 100
        mode_x = taille_x + 120
        joueurs_x = mode_x + 100

        # Affichage des titres centrés sur leur colonne
        header_y = self.players_rect.y + 10
        self.screen.blit(self.font.render("IP", True, (255, 255, 255)), (ip_x, header_y))
        self.screen.blit(self.font.render("Port", True, (255, 255, 255)), (port_x, header_y))
        self.screen.blit(self.font.render("Size", True, (255, 255, 255)), (taille_x, header_y))
        self.screen.blit(self.font.render("Mode", True, (255, 255, 255)), (mode_x, header_y))
        self.screen.blit(self.font.render("Player", True, (255, 255, 255)), (joueurs_x, header_y))

        clip_rect = self.players_rect.copy()
        clip_rect.y += 50
        clip_rect.height -= 50
        self.screen.set_clip(clip_rect)

        for idx, (ip, data) in enumerate(ALL_IP.items()):
            port, taille, mode, joueurs = data
            y_pos = self.players_rect.y + 60 + (idx * self.line_height) - self.scroll_y

            color = (100, 100, 100) if ip == self.selected_ip else (255, 255, 255)

            # Affichage des données centrées sous chaque titre
            self.screen.blit(self.font.render(ip, True, color), (ip_x, y_pos))
            self.screen.blit(self.font.render(str(port), True, color), (port_x, y_pos))
            self.screen.blit(self.font.render(taille, True, color), (taille_x, y_pos))
            self.screen.blit(self.font.render(mode, True, color), (mode_x, y_pos))
            self.screen.blit(self.font.render(str(joueurs), True, color), (joueurs_x, y_pos))

        self.screen.set_clip(None)

        # Affichage du slider
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
