import pygame
import random
from settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT, GOBLIN_WIDTH, GOBLIN_HEIGHT,
    DEBUG_MODE
)
from utils import load_sprite

from character_base import Character

class Goblin(Character):
    def __init__(self):
        goblin_sprite = load_sprite('goblin.png')
        goblin_sprites = [goblin_sprite] if goblin_sprite else []
        super().__init__(WINDOW_WIDTH - GOBLIN_WIDTH - 100, 
                        WINDOW_HEIGHT - GOBLIN_HEIGHT - 10, 
                        GOBLIN_WIDTH, 
                        GOBLIN_HEIGHT, 
                        (34, 139, 34),  # Goblin green
                        50, goblin_sprites)
        self.speed = 0.7  # Faster for visible wandering
        self.attack_range = 30
        self.attack_cooldown = 0
        self.attack_damage = 5
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        # Physics
        self.GRAVITY = 0.5  # Gravity force
        self.y_velocity = 0  # Vertical velocity
        self.on_ground = False
        # AI state
        self.state = 'wander'  # 'wander' or 'chase'
        self.wander_timer = 0
        self.wander_dir = 0  # -1=left, 0=idle, 1=right
    def draw(self, screen, camera_x):
        sprite = self.get_current_sprite()
        if sprite:
            screen.blit(pygame.transform.scale(sprite, (self.width, self.height)), (self.x - camera_x, self.y))
        else:
            pygame.draw.rect(screen, self.color, (self.x - camera_x, self.y, self.width, self.height))
    
    def update(self, hero_x, terrain, camera_x):
        ground_height = terrain.get_ground_height(self.x)
        distance = hero_x - self.x
        chase_range = 300
        
        # State switching
        if abs(distance) < chase_range:
            self.state = 'chase'
        else:
            self.state = 'wander'
            
        # Handle movement based on state
        if self.state == 'wander':
            if self.wander_timer <= 0:
                # Pick a new direction and duration
                self.wander_dir = random.choice([-1, 0, 1])
                self.wander_timer = random.randint(40, 120)  # frames
            else:
                self.wander_timer -= 1
                self.x += self.wander_dir * self.speed
        elif self.state == 'chase':
            if distance > 0:
                self.x += self.speed
            else:
                self.x -= self.speed
                
        # Apply gravity and ground collision
        self.y_velocity = min(self.y_velocity + self.GRAVITY, 15)  # Terminal velocity
        self.y += self.y_velocity
        
        # Check for ground collision
        if self.y > ground_height - self.height:
            self.y = ground_height - self.height
            self.y_velocity = 0
            self.is_jumping = False
            self.on_ground = True
        else:
            self.on_ground = False
        
        # Update position with bounds checking
        self.x = max(0, min(self.x, terrain.terrain_width - self.width))
        self.y = max(0, min(self.y, WINDOW_HEIGHT - self.height))
        
        # Update rect for collision detection
        self.update_rect()
        
        # Decrement attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            
        # Attempt attack only if cooldown is zero
        if abs(distance) < self.attack_range and self.attack_cooldown <= 0:
            if self.attack():
                self.attack_cooldown = 60  # 1 second at 60 FPS
                if DEBUG_MODE:
                    # print(f"Goblin attacks! Cooldown reset to {self.attack_cooldown}")
                    pass
        
        # Debug output
        if DEBUG_MODE and random.random() < 0.1:
            # print(f"Goblin AI: state={self.state}, wander_dir={self.wander_dir}, distance={distance:.1f}, x={self.x:.1f}, hero_x={hero_x:.1f}")
            pass
