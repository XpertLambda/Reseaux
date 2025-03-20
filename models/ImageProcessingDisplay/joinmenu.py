import pygame
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
