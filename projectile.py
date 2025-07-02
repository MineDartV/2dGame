import pygame
import math
import os
import random
from settings import PROJECTILE_IMG_PATH, PROJECTILE_SPEED, DEBUG_MODE, ICEBALL_IMG_PATH
from effects import ExplosionEffect, IceExplosionEffect



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
        self.active = True
        self.gravity = 0.1  # Reduced gravity for flatter arc
        self.lifetime = 240  # Increased lifetime to 4 seconds at 60 FPS
        
        # Load the projectile image if not already done
        if Projectile._projectile_img is None:
            Projectile._projectile_img = Projectile.load_projectile_image()
            
        self.image = Projectile._projectile_img.copy()  # Create a copy for each projectile
        self.rect = self.image.get_rect(center=(x, y))
        
        # Calculate rotation based on velocity
        angle_rad = math.atan2(vy, vx)
        self.rotation = math.degrees(angle_rad) - 90  # Subtract 90 to make it point forward
        
        # Rotate the image to point in the direction of movement
        self.rotated_image = pygame.transform.rotate(self.image, -self.rotation)  # Negative for correct rotation direction
        self.rect = self.rotated_image.get_rect(center=(x, y))
        
        # For collision detection
        self.radius = max(self.rect.width, self.rect.height) // 2 * 0.7  # Slightly smaller than visual for better feel
        
        if DEBUG_MODE:
            # print(f"Created projectile at x={x}, y={y} with velocity=({vx:.2f}, {vy:.2f})")
            pass

    def update(self, terrain=None, dt=1.0/60.0):
        if not self.active:
            return False  # Indicates this projectile should be removed
            
        # Apply gravity with delta time
        self.vy += self.gravity * dt * 60  # Scale by 60 to match original behavior at 60 FPS
        
        # Update position with delta time
        self.x += self.vx * dt * 60  # Scale by 60 to match original behavior at 60 FPS
        self.y += self.vy * dt * 60  # Scale by 60 to match original behavior at 60 FPS
        
        # Update the rectangle position to match the center of the projectile
        self.rect.center = (self.x, self.y)
        
        # Check for ground collision if terrain is provided
        if terrain:
            ground_height = terrain.get_ground_height(self.x)
            if self.y + self.rect.height/2 >= ground_height:
                self.active = False
                # Create appropriate explosion effect based on projectile type
                if isinstance(self, IceProjectile):
                    return IceExplosionEffect(self.x, ground_height - self.rect.height/2)
                return ExplosionEffect(self.x, ground_height - self.rect.height/2)
        
        # Decrease lifetime with delta time
        self.lifetime -= dt * 60  # Scale by 60 to match original behavior at 60 FPS
        if self.lifetime <= 0:
            self.active = False
            if isinstance(self, IceProjectile):
                return IceExplosionEffect(self.x, self.y)
            return ExplosionEffect(self.x, self.y)  # Small explosion when timing out
            
        return None

    def draw(self, screen, camera_x=0):
        if not self.active:
            return
            
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
        
        # Add subtle pulsing effect
        pulse = math.sin(pygame.time.get_ticks() * 0.02) * 0.1 + 1.0
        if pulse > 1.0:  # Only scale up, not down
            scaled_img = pygame.transform.scale_by(self.rotated_image, (pulse, pulse))
            # Adjust position to keep centered
            offset_x = (scaled_img.get_width() - self.rotated_image.get_width()) // 2
            offset_y = (scaled_img.get_height() - self.rotated_image.get_height()) // 2
            screen.blit(scaled_img, (draw_x - offset_x, draw_y - offset_y))
        else:
            screen.blit(self.rotated_image, (draw_x, draw_y))


# Ice Projectile class that inherits from Projectile
class IceProjectile(Projectile):
    """Ice projectile that freezes enemies on impact"""
    # Class variable to store the generated projectile image
    _projectile_img = None
    is_ice = True  # Mark as ice projectile for effect handling
    
    @classmethod
    def load_projectile_image(cls):
        """Load the ice projectile image from file"""
        if cls._projectile_img is None:
            try:
                if os.path.exists(ICEBALL_IMG_PATH):
                    img = pygame.image.load(ICEBALL_IMG_PATH).convert_alpha()
                    # Scale to desired size while maintaining aspect ratio
                    img = pygame.transform.scale(img, cls._projectile_size)
                    cls._projectile_img = img
                    print("Loaded ice projectile image")
                else:
                    print(f"Warning: Iceball image not found at {ICEBALL_IMG_PATH}")
                    cls._projectile_img = cls._create_fallback_image()
            except Exception as e:
                print(f"Error loading ice projectile image: {e}")
                cls._projectile_img = cls._create_fallback_image()
        return cls._projectile_img
    
    @classmethod
    def _create_fallback_image(cls):
        """Create a simple fallback ice projectile image"""
        surf = pygame.Surface(cls._projectile_size, pygame.SRCALPHA)
        width, height = cls._projectile_size
        
        # Draw a simple circle for the iceball
        pygame.draw.circle(surf, (100, 200, 255, 255), (width//2, height//2), width//2)
        pygame.draw.circle(surf, (200, 240, 255, 200), (width//2, height//2), width//3)
        
        # Add some glow
        glow = pygame.Surface((width + 4, height + 4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (150, 220, 255, 100), (width//2 + 2, height//2 + 2), width//2 + 2)
        surf.blit(glow, (-2, -2), special_flags=pygame.BLEND_ALPHA_SDL2)
        
        return surf
    
    def __init__(self, x, y, vx, vy):
        # Initialize the base Projectile class first
        super().__init__(x, y, vx, vy)
        
        # Override with ice-themed properties
        self.damage = 15  # Slightly more damage than fireball
        self.gravity = 0.08  # Slightly less gravity for flatter arc
        
        # Load ice projectile image
        if IceProjectile._projectile_img is None:
            IceProjectile._projectile_img = IceProjectile.load_projectile_image()
        
        # Update the image and rect for ice projectile
        self.image = IceProjectile._projectile_img.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.rotated_image = pygame.transform.rotate(self.image, -self.rotation)
        
        if DEBUG_MODE:
            print(f"Created ice projectile at ({x}, {y}) with velocity ({vx:.1f}, {vy:.1f})")
    
    def update(self, terrain=None, dt=1.0/60.0):
        # Call the parent class's update method with delta time
        result = super().update(terrain, dt)
        
        # Additional ice-specific behavior can be added here
        return result