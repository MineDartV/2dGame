import pygame
import math
import random
from utils import load_sprite

class ExplosionEffect:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frame = 0
        self.max_frames = 10  # 10 frames at 60 FPS = ~0.17 seconds
        self.sprite = load_sprite('fireball_explosion.png')
        self.active = True
        
    def update(self):
        self.frame += 1
        if self.frame >= self.max_frames:
            self.active = False
    
    def draw(self, screen, camera_x):
        if not self.active:
            return
            
        # Calculate screen position with camera offset
        screen_x = self.x - camera_x
        
        # Scale factor for the explosion (starts at 0.5, grows to 1.0)
        scale = 0.5 + (self.frame / self.max_frames) * 0.5
        
        # Fade out effect
        alpha = 255 * (1 - (self.frame / self.max_frames))
        
        # Create a scaled and faded version of the sprite
        if hasattr(self, 'sprite') and self.sprite:
            # Scale the sprite
            orig_rect = self.sprite.get_rect()
            new_size = (int(orig_rect.width * scale), int(orig_rect.height * scale))
            scaled = pygame.transform.scale(self.sprite, new_size)
            
            # Create a surface with per-pixel alpha for the fade effect
            scaled = scaled.convert_alpha()
            scaled_alpha = scaled.copy()
            scaled_alpha.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
            
            # Draw the explosion centered at (x, y)
            screen.blit(scaled_alpha, 
                       (screen_x - new_size[0]//2, 
                        self.y - new_size[1]//2))


class IceExplosionEffect:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frame = 0
        self.max_frames = 15  # Slightly longer duration than fire explosion
        self.sprite = load_sprite('iceball_explosion.png')
        self.active = True
        self.particles = []
        self._init_particles()
        
    def _init_particles(self):
        """Create ice shard particles for the explosion"""
        for _ in range(12):  # Create 12 ice shards
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            size = random.randint(3, 8)
            self.particles.append({
                'x': 0,  # Relative to explosion center
                'y': 0,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': size,
                'alpha': 255
            })
        
    def update(self):
        self.frame += 1
        
        # Update particles
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.1  # Gravity
            p['alpha'] = max(0, 255 * (1 - (self.frame / self.max_frames)))
            
        if self.frame >= self.max_frames:
            self.active = False
            
    def draw(self, screen, camera_x):
        if not self.active:
            return
            
        # Calculate screen position with camera offset
        screen_x = self.x - camera_x
        
        # Draw main explosion sprite
        if hasattr(self, 'sprite') and self.sprite:
            # Fade out effect
            alpha = 200 * (1 - (self.frame / self.max_frames))
            
            # Create a surface with per-pixel alpha for the fade effect
            scaled = self.sprite.copy()
            scaled_alpha = scaled.convert_alpha()
            scaled_alpha.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
            
            # Draw the explosion centered at (x, y)
            rect = scaled_alpha.get_rect(center=(int(screen_x), int(self.y)))
            screen.blit(scaled_alpha, rect)
        
        # Draw ice shard particles
        for p in self.particles:
            if p['alpha'] > 0:
                # Create a small ice shard surface
                shard = pygame.Surface((p['size'], p['size']), pygame.SRCALPHA)
                color = (180, 220, 255, int(p['alpha']))
                pygame.draw.rect(shard, color, (0, 0, p['size'], p['size']))
                
                # Draw the shard at its position relative to the explosion
                screen.blit(shard, 
                          (int(screen_x + p['x'] - p['size']//2), 
                           int(self.y + p['y'] - p['size']//2)))
