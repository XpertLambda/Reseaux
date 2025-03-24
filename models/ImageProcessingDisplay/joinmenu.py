import pygame
<<<<<<< HEAD
from GLOBAL_VAR import *
from ImageProcessingDisplay.imagemethods import adjust_sprite

class JoinMenu:
    def __init__(self, screen, game_state):
        self.screen = screen
        self.game_state = game_state
        self.font = pygame.font.Font(MEDIEVALSHARP, 22)

        rect_width, rect_height = 750, 350
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
        self.slider_rect_scroll = pygame.Rect(
            self.players_rect.right - 20,
            self.players_rect.y,
            20,
            self.players_rect.height
        )

        self.selected_ip = None

        # Slider de volume (lié à game_state.volume)
        self.slider_rect = pygame.Rect(screen.get_width() - 320, screen.get_height() - 50, 300, 10)
        self.slider_thumb_rect = pygame.Rect(
            self.slider_rect.x + int(self.game_state.volume * 300),
            self.slider_rect.y - 5,
            10,
            20
        )

    def generate_color(self, port, taille, mode_idx, joueurs):
        seed = hash(f"{port}-{taille}-{mode_idx}-{joueurs}")
        r = (seed & 0xFF0000) >> 16
        g = (seed & 0x00FF00) >> 8
        b = seed & 0x0000FF
        return (r % 256, g % 256, b % 256)

    def draw(self):
        screen_width, screen_height = self.screen.get_size()
        self.screen.blit(adjust_sprite(START_IMG, screen_width, screen_height), (0, 0))
        pygame.draw.rect(self.screen, (0, 0, 0), self.players_rect)

        columns_x = [self.players_rect.x + x for x in [10, 150, 250, 370, 470, 570]]
        headers = ["IP", "Port", "Size", "Mode", "Style", "Players"]
        header_y = self.players_rect.y + 10

        for i, header in enumerate(headers):
            text = self.font.render(header, True, (255, 255, 255))
            self.screen.blit(text, text.get_rect(centerx=columns_x[i] + 50, y=header_y))

        clip_rect = self.players_rect.copy()
        clip_rect.y += 50
        clip_rect.height -= 50
        self.screen.set_clip(clip_rect)

        for idx, (ip, data) in enumerate(ALL_IP.items()):
            port, taille_x, taille_y, mode_idx, style_idx, joueurs = data
            taille = f"{taille_x} x {taille_y}"
            mode_text = mode[mode_idx]
            style_text = style_map[style_idx]

            y_pos = self.players_rect.y + 60 + (idx * self.line_height) - self.scroll_y

            color = self.generate_color(port, taille, mode_idx, joueurs)
            if ip == self.selected_ip:
                color = (200, 200, 200)

            items = [ip, str(port), taille, mode_text, style_text, str(joueurs)]
            for i, item in enumerate(items):
                text = self.font.render(item, True, color)
                self.screen.blit(text, text.get_rect(centerx=columns_x[i] + 50, y=y_pos))

        self.screen.set_clip(None)

        pygame.draw.rect(self.screen, (128, 128, 128), self.join_button)
        join_text = self.font.render("Join", True, (255, 255, 255))
        self.screen.blit(join_text, join_text.get_rect(center=self.join_button.center))

        pygame.draw.polygon(self.screen, (128, 128, 128), [
            (self.back_button.x + 35, self.back_button.y + 10),
            (self.back_button.x + 15, self.back_button.y + 25),
            (self.back_button.x + 35, self.back_button.y + 40)
        ])

        total_lines = len(ALL_IP)
        total_height = total_lines * self.line_height + 60
        if total_height > self.players_rect.height:
            slider_height = max(self.players_rect.height * (self.max_visible_lines / total_lines), 30)
            slider_y = self.players_rect.y + (self.scroll_y / (total_height - self.players_rect.height)) * (self.players_rect.height - slider_height)
            pygame.draw.rect(self.screen, (100, 100, 100), (self.slider_rect_scroll.x, slider_y, self.slider_rect_scroll.width, slider_height))

        # Affichage du slider volume (à droite)
        self.slider_rect.topleft = (screen_width - 320, screen_height - 50)
        self.slider_thumb_rect.topleft = (
            self.slider_rect.x + int(self.game_state.volume * self.slider_rect.width),
            self.slider_rect.y - 5
        )
        self._draw_slider()

    def _draw_slider(self):
        pygame.draw.rect(self.screen, (200, 200, 200), self.slider_rect)
        pygame.draw.rect(self.screen, (0, 0, 255), self.slider_thumb_rect)
        volume_text = f"Volume: {int(self.game_state.volume * 100)}%"
        font = pygame.font.Font(MEDIEVALSHARP, 28)
        text = font.render(volume_text, True, WHITE_COLOR)
        self.screen.blit(text, text.get_rect(center=(self.slider_rect.centerx, self.slider_rect.bottom + 10)))

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
            pass  # clique en dehors = rien

        for idx, ip in enumerate(ALL_IP.keys()):
            y_pos = self.players_rect.y + 60 + (idx * self.line_height) - self.scroll_y
            ip_rect = pygame.Rect(self.players_rect.x, y_pos, self.players_rect.width, self.line_height)

            if ip_rect.collidepoint(pos):
                self.selected_ip = ip
                SELECTED_IP = ip
                break

        # Volume slider interaction
        if self.slider_rect.collidepoint(pos):
            self.game_state.volume = max(0.0, min(1.0, (pos[0] - self.slider_rect.x) / self.slider_rect.width))
            self.slider_thumb_rect.x = self.slider_rect.x + int(self.game_state.volume * self.slider_rect.width)
            pygame.mixer.music.set_volume(self.game_state.volume)

        return None

    def scroll(self, direction):
        total_height = len(ALL_IP) * self.line_height + 60
        if total_height > self.players_rect.height:
            self.scroll_y -= direction * 20
            self.scroll_y = max(0, min(self.scroll_y, total_height - self.players_rect.height))
=======
import os

class JoinMenu:
    def __init__(self):
        pygame.init()
        
        # Définition des dimensions de l'écran
        self.WIDTH, self.HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Join Menu")
        
        # Définition des couleurs
        self.WHITE = (255, 255, 255)
        self.BLUE = (50, 50, 200)
        
        # Chargement de la police et du fond
        base_path = os.path.dirname(__file__)
        self.ttf_path = os.path.join(base_path, "../MedievalSharp-Regular.ttf")
        self.background_path = os.path.join(base_path, "../models/Icons/Building/Towncenter_aoe2DE.png")  # Fond avec archi du jeu
        
        if os.path.exists(self.ttf_path):
            self.font = pygame.font.Font(self.ttf_path, 36)
        else:
            self.font = pygame.font.Font(pygame.font.get_default_font(), 36)
        
        if os.path.exists(self.background_path):
            self.background = pygame.image.load(self.background_path)
            self.background = pygame.transform.scale(self.background, (self.WIDTH, self.HEIGHT))
        else:
            self.background = None
        
        self.clicked = False
    
    def draw_text(self, text, x, y, color=None):
        if color is None:
            color = self.WHITE
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))
    
    def draw_button(self, text, x, y, w, h, color, action=None):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]
        
        pygame.draw.rect(self.screen, color, (x, y, w, h), border_radius=10)
        text_surface = self.font.render(text, True, self.WHITE)
        text_rect = text_surface.get_rect(center=(x + w // 2, y + h // 2))
        self.screen.blit(text_surface, text_rect)
        
        if x + w > mouse[0] > x and y + h > mouse[1] > y and click and not self.clicked:
            if action is not None:
                action()
            self.clicked = True
        elif not click:
            self.clicked = False
    
    def join_party(self):
        print("je rejoins la partie haha")
    
    def run(self):
        running = True
        while running:
            if self.background:
                self.screen.blit(self.background, (0, 0))
            else:
                self.screen.fill((30, 30, 30))
            
            # Affichage des informations
            player_id = "ID: 12345"
            player_ip = "IP: 192.168.1.100"
            self.draw_text(player_id, 300, 200)
            self.draw_text(player_ip, 300, 250)
            
            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            # Affichage du bouton JOIN PARTY bien centré
            self.draw_button("JOIN PARTY", 250, 500, 300, 70, self.BLUE, self.join_party)
            pygame.display.flip()
        
        pygame.quit()

if __name__ == "__main__":
    menu = JoinMenu()
    menu.run()
>>>>>>> 37d17b3da337308f0ffaa5156c2e904311fd7ef8
