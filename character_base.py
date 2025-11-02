import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, DEBUG_MODE

class Character:
    def __init__(self, x, y, width, height, color, health, sprite_images=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.health = health
        self.attacking = False
        self.attack_cooldown = 0
        self.attack_range = 50
        self.speed = 3  # Reduced speed for better control
        self.is_jumping = False
        self.jump_count = 0
        self.y_velocity = 0
        self.rect = pygame.Rect(x, y, width, height)
        # Animation support
        self.sprite_images = sprite_images if sprite_images else []
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_delay = 10  # Frames to wait before switching

    def get_current_sprite(self):
        if self.sprite_images:
            return self.sprite_images[self.current_frame]
        return None

    def update_animation(self):
        if self.sprite_images and len(self.sprite_images) > 1:
            self.frame_timer += 1
            if self.frame_timer >= self.frame_delay:
                self.current_frame = (self.current_frame + 1) % len(self.sprite_images)
                self.frame_timer = 0
        
    def update_rect(self):
        self.rect.topleft = (self.x, self.y)
        
    def move(self, keys, terrain, camera_x):
        # Get ground height at current position
        ground_height = terrain.get_ground_height(self.x)
        
        # Horizontal movement
        if keys[pygame.K_a]:
            self.x -= self.speed
            # Keep within bounds
            self.x = max(0, self.x)
            # Extend terrain if moving left and near edge
            if self.x < 100 and terrain.terrain_width > WINDOW_WIDTH:
                terrain.extend_terrain_left()
        if keys[pygame.K_d]:
            self.x += self.speed
            # Keep within bounds
            self.x = min(self.x, terrain.terrain_width - self.width)
            # Extend terrain if moving right and near edge

        # Apply gravity
        self.y_velocity += self.GRAVITY
        self.y += self.y_velocity
        
        # Check for ground collision
        if self.y > ground_height - self.height:
            self.y = ground_height - self.height
            self.y_velocity = 0
            self.is_jumping = False
            self.jump_count = 0
        else:
            if self.y < ground_height - self.height:
                self.y_velocity += 1
                self.y += self.y_velocity
        
        # Keep character within bounds and on terrain
        self.x = max(0, min(self.x, terrain.terrain_width - self.width))
        self.y = max(0, min(self.y, WINDOW_HEIGHT - self.height))
        
        # Update rect position
        self.update_rect()
        
        # Update health if falling off edge
        if self.y > WINDOW_HEIGHT:
            self.health = max(0, self.health - 1)
            if self.health <= 0:
                self.respawn()
            self.y = ground_height - self.height
            self.is_jumping = False
            self.y_velocity = 0
            
        # Ensure health is not negative
        self.health = max(0, self.health)

    def attack(self, target=None):
        if self.attack_cooldown <= 0:
            self.attacking = True
            self.attack_cooldown = 30  # 30 frames cooldown
            if target:
                target.take_damage(self.attack_damage)
            return True
        return False
    
    def take_damage(self, amount):
        # if DEBUG_MODE:
        #     print(f"Character taking {amount} damage. Health before: {self.health}")
        self.health = max(0, self.health - amount)
        # if DEBUG_MODE:
        #     print(f"Health after damage: {self.health}")
        if self.health <= 0:
            # if DEBUG_MODE:
            #     print("Character health <= 0, respawning...")
            self.respawn()
    
    def respawn(self):
        self.health = 100
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT - 100

