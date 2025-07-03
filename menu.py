import pygame
import sys
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, WHITE, BLACK, FONT_NAME

def draw_text(surface, text, size, x, y, color=WHITE):
    try:
        # First try with the specified font
        font = pygame.font.SysFont('Arial', size)
        text_surface = font.render(text, True, color)
    except:
        # Fall back to default font if there's an error
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color)
    
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)
    return text_rect

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=WHITE, text_size=30):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.text = text
        self.text_color = text_color
        self.text_size = text_size
        self.is_hovered = False
    
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)  # Border
        draw_text(surface, self.text, self.text_size, self.rect.centerx, 
                 self.rect.centery - self.text_size//2, self.text_color)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click

class StartMenu:
    def __init__(self, screen):
        self.screen = screen
        self.overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        
        # Create start button
        btn_width, btn_height = 200, 60
        self.start_button = Button(
            WINDOW_WIDTH // 2 - btn_width // 2,
            WINDOW_HEIGHT // 2 - btn_height // 2,
            btn_width, btn_height,
            "START GAME", (50, 150, 50), (70, 200, 70)
        )
        
        # Title
        self.title_font = pygame.font.Font(FONT_NAME, 80)
        self.subtitle_font = pygame.font.Font(FONT_NAME, 30)
    
    def draw(self, world_surface):
        # Draw the world in the background
        self.screen.blit(world_surface, (0, 0))
        
        # Add overlay
        self.screen.blit(self.overlay, (0, 0))
        
        # Draw title
        title = self.title_font.render("MYSTIC REALM", True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4))
        self.screen.blit(title, title_rect)
        
        # Draw subtitle
        subtitle = self.subtitle_font.render("Defeat the Goblins!", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4 + 80))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Draw button
        mouse_pos = pygame.mouse.get_pos()
        self.start_button.check_hover(mouse_pos)
        self.start_button.draw(self.screen)
        
        # Draw controls hint with wrapped text
        controls_text = [
            "WASD to move • LEFT CLICK to shoot",
            "1 to equip/unequip staff • 2 to switch staff type"
        ]
        
        for i, line in enumerate(controls_text):
            controls_surface = self.subtitle_font.render(line, True, (200, 200, 200))
            self.screen.blit(controls_surface, 
                           (WINDOW_WIDTH // 2 - controls_surface.get_width() // 2, 
                            WINDOW_HEIGHT - 80 + i * 30))
        
        pygame.display.flip()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if self.start_button.is_clicked(event.pos, True):
                        return "start_game"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return "start_game"
        
        return "menu"
