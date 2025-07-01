import pygame
import math
import os
from settings import PROJECTILE_IMG_PATH, PROJECTILE_SPEED, DEBUG_MODE



# Projectile class with image support
class Projectile:
    # Class variable to store the generated projectile image
    _projectile_img = None
    # Keep original size but use high-quality source
    _projectile_size = (32, 32)  # Size of the projectile in the game
    
    @classmethod
    def load_projectile_image(cls):
        """Load the projectile image from file"""
        try:
            if os.path.exists(PROJECTILE_IMG_PATH):
                img = pygame.image.load(PROJECTILE_IMG_PATH).convert_alpha()
                # Scale to desired size while maintaining aspect ratio
                img = pygame.transform.scale(img, cls._projectile_size)
                # print("Loaded projectile image from file")
                return img
            else:
                # print(f"Warning: Projectile image not found at {PROJECTILE_IMG_PATH}")
                return cls._create_fallback_image()
        except Exception as e:
            # print(f"Error loading projectile image: {e}")
            return cls._create_fallback_image()
    
    @classmethod
    def _create_fallback_image(cls):
        """Create a simple fallback projectile image"""
        surf = pygame.Surface(cls._projectile_size, pygame.SRCALPHA)
        width, height = cls._projectile_size
        
        # Draw a simple circle for the fireball
        pygame.draw.circle(surf, (255, 100, 0, 255), (width//2, height//2), width//2)
        pygame.draw.circle(surf, (255, 200, 0, 200), (width//2, height//2), width//3)
        
        # Add some glow
        glow = pygame.Surface((width + 4, height + 4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 150, 0, 100), (width//2 + 2, height//2 + 2), width//2 + 2)
        surf.blit(glow, (-2, -2), special_flags=pygame.BLEND_ALPHA_SDL2)
        
        return surf
    
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.speed = PROJECTILE_SPEED
        
        # Load the projectile image if not already done
        if Projectile._projectile_img is None:
            Projectile._projectile_img = Projectile.load_projectile_image()
            
        self.image = Projectile._projectile_img.copy()  # Create a copy for each projectile
        self.rect = self.image.get_rect(center=(x, y))
        
        # Calculate rotation based on velocity
        # We'll use atan2 with (vy, vx) and then add 90 degrees to make the fireball point forward
        angle_rad = math.atan2(vy, vx)
        self.rotation = math.degrees(angle_rad) - 90  # Subtract 90 to make it point forward
        
        # Rotate the image to point in the direction of movement
        self.rotated_image = pygame.transform.rotate(self.image, -self.rotation)  # Negative for correct rotation direction
        self.rect = self.rotated_image.get_rect(center=(x, y))
        
        if DEBUG_MODE:
            # print(f"Created projectile at x={x}, y={y} with velocity=({vx:.2f}, {vy:.2f})")
            pass

    def update(self):
        # Update position
        self.x += self.vx
        self.y += self.vy
        # Update the rectangle position to match the center of the projectile
        self.rect.center = (self.x, self.y)

    def draw(self, screen, camera_x=0):
        # Calculate screen position with camera offset
        screen_x = self.x - camera_x
        
        # Update rotation based on current velocity
        angle_rad = math.atan2(self.vy, self.vx)
        current_rotation = math.degrees(angle_rad) - 90  # Same calculation as in __init__
        
        if abs(current_rotation - self.rotation) > 1:  # Only update if rotation changed significantly
            self.rotation = current_rotation
            # Create a new surface with per-pixel alpha for smooth rotation
            self.rotated_image = pygame.transform.rotate(self.image, -self.rotation)  # Negative for correct direction
            # Create a clean surface to handle the rotation artifacts
            rotated_clean = pygame.Surface(self.rotated_image.get_size(), pygame.SRCALPHA)
            rotated_clean.blit(self.rotated_image, (0, 0))
            self.rotated_image = rotated_clean
            self.rect = self.rotated_image.get_rect(center=(self.x, self.y))
        
        # Calculate the top-left position for drawing
        draw_x = screen_x - self.rotated_image.get_width() // 2
        draw_y = self.y - self.rotated_image.get_height() // 2
        
        # Draw the rotated image with proper alpha blending
        screen.blit(self.rotated_image, (draw_x, draw_y))

        