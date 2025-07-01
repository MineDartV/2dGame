import pygame
import random
import math
import os
from generate_assets import generate_assets

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
DEBUG_MODE = True

# Character dimensions
PLAYER_WIDTH = 96  # 48*2 for clean pixel art scaling (original frame is 48x64)
PLAYER_HEIGHT = 128  # 64*2 for clean pixel art scaling
GOBLIN_WIDTH = 40
GOBLIN_HEIGHT = 60
PROJECTILE_SPEED = 10

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
BROWN = (139, 69, 19)
SKY_BLUE = (135, 206, 235)
GRASS_GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)

# Generate assets if they don't exist
generate_assets()

# --- Asset loading ---
def load_sprite(filename):
    try:
        img = pygame.image.load(os.path.join('assets', filename)).convert_alpha()
        if DEBUG_MODE:
            # print(f"[DEBUG] Loaded {filename} with size {img.get_size()}")
            pass
        return img
    except Exception as e:
        # print(f"Warning: could not load {filename}: {e}")
        return None

# Projectile settings
PROJECTILE_SIZE = 20  # Size of the projectile box
PROJECTILE_SPEED = 8  # Reduced speed from 15 to 8
PROJECTILE_COOLDOWN = 15  # Cooldown between shots

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
BROWN = (139, 69, 19)
SKY_BLUE = (135, 206, 235)
GRASS_GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
PROJECTILE_COLOR = BLACK  # Black color for projectiles

# Debug mode
DEBUG_MODE = True

import os
import pygame
import math

# Ensure assets directory exists
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')
os.makedirs(ASSETS_DIR, exist_ok=True)

# Projectile image path
PROJECTILE_IMG_PATH = os.path.join(ASSETS_DIR, 'fireball.png')

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

# Terrain class
class Terrain:
    def place_trees(self):
        """Place trees on the terrain, including on hills."""
        tile_size = 32
        min_distance = 2 * tile_size  # Minimum distance between trees
        
        # Place trees across the entire map width
        for x in range(0, self.terrain_width, tile_size):
            # Get the ground height at this position
            ground_height = self.get_ground_height(x)
            
            # Check if this is a suitable spot (not too steep)
            # Get slope by checking height difference with next point
            next_x = min(x + tile_size, self.terrain_width - 1)
            next_height = self.get_ground_height(next_x)
            slope = abs(ground_height - next_height) / tile_size
            
            # Allow trees on moderate slopes (less than 0.5 height change per tile)
            if slope < 0.5:
                # Check if we're not too close to another tree
                too_close = False
                for tree_x in self.trees:
                    if abs(x - tree_x) < min_distance:
                        too_close = True
                        break
                
                # 30% chance to place a tree if not too close to another
                if not too_close and random.random() < 0.3:
                    self.trees.add(x)
                    # Make taller trees on higher ground
                    height_factor = 1.0 - ((ground_height - (WINDOW_HEIGHT - 120)) / 80.0)  # Normalize height
                    tree_height = 3 + int(4 * max(0, min(1, height_factor)))  # 3-7 tiles tall
                    self.tree_data[x] = tree_height

    def __init__(self, grass_img=None, dirt_img=None, stone_img=None, tree_img=None):
        self.grass_img = grass_img
        self.dirt_img = dirt_img
        self.stone_img = stone_img
        self.tree_img = tree_img
        # Start with a much wider initial terrain
        tile_size = 32
        self.terrain_width = WINDOW_WIDTH * 4
        self.points = []
        self.trees = set()
        self.tree_data = {}  # x -> height (in tiles)
        
        # Base height for the terrain
        base_height = WINDOW_HEIGHT - 60
        
        # Create initial terrain points with smooth variation
        for x in range(0, self.terrain_width, tile_size):
            # Add some smooth variation to the height
            noise = math.sin(x / 200) * 20  # Smooth wave pattern
            y = base_height + noise
            self.points.append((x, y))
        
        # Apply smoothing to the terrain
        self._smooth_terrain()
        
        # Now place trees after initial terrain is generated
        self.place_trees()
        
        # Smooth around tree areas to create flatter ground
        self._flatten_around_trees()
        
        # Final smoothing pass
        self._smooth_terrain()
    
    def _smooth_terrain(self):
        """Apply smoothing to the terrain points"""
        if len(self.points) < 3:
            return
            
        # Create a copy of points for reference
        old_points = self.points.copy()
        
        # Smooth each point based on its neighbors
        for i in range(1, len(self.points) - 1):
            x, y = old_points[i]
            prev_x, prev_y = old_points[i-1]
            next_x, next_y = old_points[i+1]
            
            # Average the y position with neighbors
            avg_y = (prev_y + y + next_y) / 3
            
            # Limit the maximum change to prevent steep cliffs
            max_change = 5
            new_y = y + min(max(avg_y - y, -max_change), max_change)
            
            # Keep within bounds
            new_y = max(WINDOW_HEIGHT - 120, min(WINDOW_HEIGHT - 40, new_y))
            self.points[i] = (x, new_y)
    
    def _flatten_around_trees(self):
        """Flatten the terrain around tree positions"""
        if not self.trees:
            return
            
        # For each tree, flatten the area around it
        for tree_x in self.trees:
            # Find the index of the point at or before the tree
            idx = 0
            for i, (x, y) in enumerate(self.points):
                if x > tree_x:
                    idx = max(0, i-1)
                    break
            
            # Flatten an area around the tree (3 points on each side)
            start_idx = max(0, idx - 3)
            end_idx = min(len(self.points) - 1, idx + 3)
            
            if start_idx >= end_idx:
                continue
                
            # Get the average height of this area
            total_y = sum(self.points[i][1] for i in range(start_idx, end_idx + 1))
            avg_y = total_y / (end_idx - start_idx + 1)
            
            # Smooth the area
            for i in range(start_idx, end_idx + 1):
                x, _ = self.points[i]
                # Gradually blend to the average height
                blend = 0.7  # How much to blend towards the average (0-1)
                new_y = self.points[i][1] * (1 - blend) + avg_y * blend
                self.points[i] = (x, new_y)
    
    def extend_terrain_left(self):
        # Extend terrain to the left
        if self.points and self.points[0][0] > 0:
            # Get last point on left
            last_x = self.points[0][0]
            last_y = self.points[0][1]
            
            # Add new points to the left
            tile_size = 32
            for i in range(50):
                new_x = last_x - tile_size
                new_y = last_y + random.randint(-20, 20)
                new_y = max(WINDOW_HEIGHT - 100, min(WINDOW_HEIGHT - 50, new_y))
                self.points.insert(0, (new_x, new_y))
                if random.random() < 0.5:
                    self.trees.add(new_x)
                    if new_x not in self.tree_data:
                        self.tree_data[new_x] = random.randint(3, 5)
                last_x = new_x
            
            # Update terrain width
            self.terrain_width += 500
            
            # Debug: Print extension info
            if DEBUG_MODE:
                # print(f"Extended terrain left to {self.terrain_width} width")
                pass
            
            # Update all points to ensure proper spacing
            for i in range(len(self.points)):
                x, y = self.points[i]
                self.points[i] = (x, y)  # This forces recalculation of points
    
    def extend_terrain_right(self):
        # Extend terrain to the right
        if self.points:
            # Get last point on right
            last_x = self.points[-1][0]
            last_y = self.points[-1][1]
            
            # Add new points to the right
            tile_size = 32
            for i in range(50):
                new_x = last_x + tile_size
                new_y = last_y + random.randint(-20, 20)
                new_y = max(WINDOW_HEIGHT - 100, min(WINDOW_HEIGHT - 50, new_y))
                self.points.append((new_x, new_y))
                self.trees.add(new_x)  # Tree every tile
                last_x = new_x
            
            # Update terrain width
            self.terrain_width += 500
            
            # Debug: Print extension info
            if DEBUG_MODE:
                # print(f"Extended terrain right to {self.terrain_width} width")
                pass
            
            # Update all points to ensure proper spacing
            for i in range(len(self.points)):
                x, y = self.points[i]
                self.points[i] = (x, y)  # This forces recalculation of points
    
    def get_ground_height(self, x):
        # Handle edge cases
        if not self.points:
            return WINDOW_HEIGHT - 50  # Default height if no points
            
        # Clamp x to valid range
        x = max(0, min(x, self.points[-1][0]))
        
        # Find the first point with x > target
        for i in range(1, len(self.points)):
            x1, y1 = self.points[i-1]
            x2, y2 = self.points[i]
            
            if x1 <= x <= x2:
                # Linear interpolation between the two points
                if x1 == x2:
                    return y1
                t = (x - x1) / (x2 - x1)
                # Use cubic interpolation for smoother transitions
                if i > 1 and i < len(self.points) - 1:
                    x0, y0 = self.points[i-2]
                    x3, y3 = self.points[i+1]
                    # Catmull-Rom spline for smoother curves
                    t2 = t * t
                    t3 = t2 * t
                    return 0.5 * ((2 * y1) + 
                                (-y0 + y2) * t + 
                                (2*y0 - 5*y1 + 4*y2 - y3) * t2 + 
                                (-y0 + 3*y1 - 3*y2 + y3) * t3)
                # Fall back to linear interpolation
                return y1 * (1 - t) + y2 * t
                
        # If we get here, return the y of the last point
        return self.points[-1][1]
    
    def draw(self, screen, camera_x):
        # Draw terrain as Terraria-style tiles (sprites)
        tile_size = 32
        
        # First draw all trees (behind everything)
        for x, y in self.points:
            if x in self.trees and self.tree_img and -200 < (x - camera_x) < WINDOW_WIDTH + 200:
                # Position tree so the base is at ground level
                tree_y = y - 256 + tile_size - 5
                tree_x = x - camera_x - 100  # Center the tree on the block
                
                # Draw the tree (behind everything)
                screen.blit(pygame.transform.scale(self.tree_img, (200, 256)), 
                          (tree_x, tree_y))
        
        # Then draw the terrain blocks (on top of trees)
        for i, (x, y) in enumerate(self.points):
            # Draw grass tile at the top
            if self.grass_img:
                screen.blit(pygame.transform.scale(self.grass_img, (tile_size, tile_size)), (x - camera_x, y))
            else:
                pygame.draw.rect(screen, (34, 139, 34), (x - camera_x, y, tile_size, tile_size))
            # Draw dirt tiles below grass
            if self.dirt_img:
                for dy in range(tile_size, tile_size*3, tile_size):
                    screen.blit(pygame.transform.scale(self.dirt_img, (tile_size, tile_size)), (x - camera_x, y + dy))
            else:
                for dy in range(tile_size, tile_size*3, tile_size):
                    pygame.draw.rect(screen, (139, 69, 19), (x - camera_x, y + dy, tile_size, tile_size))
            # Draw stone tiles even deeper
            if self.stone_img:
                for dy in range(tile_size*3, tile_size*5, tile_size):
                    screen.blit(pygame.transform.scale(self.stone_img, (tile_size, tile_size)), (x - camera_x, y + dy))
            else:
                for dy in range(tile_size*3, tile_size*5, tile_size):
                    pygame.draw.rect(screen, (128, 128, 128), (x - camera_x, y + dy, tile_size, tile_size))
        
        # Fallback for missing tree images (drawn after terrain)
        for x, y in self.points:
            if x in self.trees and (self.tree_img is None):
                # Fallback if tree image fails to load
                tree_height = self.tree_data.get(x, 4)
                for h in range(tree_height):
                    pygame.draw.rect(screen, (0, 100, 0), 
                                   (x - camera_x, y - tile_size * (h + 1), tile_size, tile_size))

    def get_visible_terrain(self, camera_x):
        # Get the ground heights for visible terrain
        visible_heights = []
        for x in range(0, self.terrain_width, 32):
            if x + camera_x < WINDOW_WIDTH and x + camera_x > 0:
                visible_heights.append(self.get_ground_height(x))
        return visible_heights

# Game window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Hero vs Goblin")

def load_terrain_assets():
    grass_img = load_sprite('grass.png')
    dirt_img = load_sprite('dirt.png')
    stone_img = load_sprite('stone.png')
    tree_img = load_sprite('tree.png')
    return grass_img, dirt_img, stone_img, tree_img


clock = pygame.time.Clock()

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

    def attack(self):
        if self.attack_cooldown <= 0:
            self.attacking = True
            self.attack_cooldown = 30  # 30 frames cooldown
            return True
        return False
    
    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        if self.health <= 0:
            self.respawn()
    
    def respawn(self):
        self.health = 100
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT - 100

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

class Hero(Character):
    # Class-level variables to store loaded sprites (shared across all instances)
    _sprites_loaded = False
    _anim_frames_right = []
    _anim_frames_left = []
    _idle_right = None
    _idle_left = None
    _jump_right = None
    _jump_left = None
    
    def __init__(self, shirt_color=None, pants_color=None, hair_color=None):
        # Default colors if none provided
        self.shirt_color = shirt_color if shirt_color is not None else (50, 100, 200)  # Blue shirt
        self.pants_color = pants_color if pants_color is not None else (80, 50, 20)    # Brown pants
        self.hair_color = hair_color if hair_color is not None else (139, 69, 19)      # Brown hair
        self.color = self.shirt_color  # For backward compatibility
        
        # Load sprites only once (class-level)
        if not Hero._sprites_loaded:
            try:
                # Load the sprite sheet
                sprite_sheet = load_sprite('base_sheet_character.png')
                if sprite_sheet:
                    # Assuming each frame is 32x32 pixels in the sprite sheet
                    frame_width, frame_height = 32, 32
                    
                    # Extract walking right frames (adjust these coordinates based on your sprite sheet)
                    for i in range(4):  # Assuming 4 frames for walking
                        frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                        frame.blit(sprite_sheet, (0, 0), (i * frame_width, 0, frame_width, frame_height))
                        # Apply color tints to different parts of the character
                        # Create a copy of the original frame for color manipulation
                        colored_frame = frame.copy()
                        
                        # Apply a simple color tint to the character
                        # Create a colored version of the frame
                        colored_frame = frame.copy()
                        
                        # Apply shirt color (top half)
                        for y in range(frame_height // 2):
                            for x in range(frame_width):
                                # Get the original pixel
                                r, g, b, a = frame.get_at((x, y))
                                # Only tint non-transparent pixels
                                if a > 0:
                                    # Blend with shirt color (25% strength)
                                    nr = min(255, r + self.shirt_color[0] // 4)
                                    ng = min(255, g + self.shirt_color[1] // 4)
                                    nb = min(255, b + self.shirt_color[2] // 4)
                                    colored_frame.set_at((x, y), (nr, ng, nb, a))
                        
                        # Apply pants color (bottom half)
                        for y in range(frame_height // 2, frame_height):
                            for x in range(frame_width):
                                # Get the original pixel
                                r, g, b, a = frame.get_at((x, y))
                                # Only tint non-transparent pixels
                                if a > 0:
                                    # Blend with pants color (30% strength)
                                    nr = min(255, r + self.pants_color[0] // 3)
                                    ng = min(255, g + self.pants_color[1] // 3)
                                    nb = min(255, b + self.pants_color[2] // 3)
                                    colored_frame.set_at((x, y), (nr, ng, nb, a))
                        
                        # Apply hair color (top portion)
                        for y in range(frame_height // 3):
                            for x in range(frame_width):
                                # Get the original pixel
                                r, g, b, a = frame.get_at((x, y))
                                # Only tint non-transparent pixels
                                if a > 0:
                                    # Blend with hair color (35% strength)
                                    nr = min(255, r + self.hair_color[0] // 3)
                                    ng = min(255, g + self.hair_color[1] // 3)
                                    nb = min(255, b + self.hair_color[2] // 3)
                                    colored_frame.set_at((x, y), (nr, ng, nb, a))
                        frame = colored_frame
                        Hero._anim_frames_right.append(frame)
                    
                    # Extract walking left frames (flip right frames for left movement)
                    for frame in Hero._anim_frames_right:
                        flipped = pygame.transform.flip(frame, True, False)
                        Hero._anim_frames_left.append(flipped)
                    
                    # Extract idle frame (first frame of walking animation as placeholder)
                    if Hero._anim_frames_right:
                        Hero._idle_right = Hero._anim_frames_right[0]
                        Hero._idle_left = Hero._anim_frames_left[0]
                    
                    # Extract jump frame (use the first frame as placeholder for now)
                    Hero._jump_right = Hero._anim_frames_right[0] if Hero._anim_frames_right else None
                    Hero._jump_left = Hero._anim_frames_left[0] if Hero._anim_frames_left else None
                    
                    Hero._sprites_loaded = True
                    if DEBUG_MODE:
                        # print("[DEBUG] Successfully loaded hero sprites from sprite sheet")
                        pass
                else:
                    # print("Error: Could not load hero sprite sheet")
                    pass
            except Exception as e:
                # print(f"Error loading hero sprites: {e}")
                pass
        
        # Initialize with the idle right sprite
        sprite_list = [Hero._idle_right] if Hero._idle_right else None
        # Adjust the initial y-position to align with the floor
        initial_y = WINDOW_HEIGHT - PLAYER_HEIGHT - 10  # Temporary, will be adjusted in update
        # Use shirt_color for the parent class's color parameter
        super().__init__(100, initial_y, PLAYER_WIDTH, 
                       PLAYER_HEIGHT, self.shirt_color, 100, sprite_list)
        
        # Apply colors to the character
        self.apply_colors()
        # Visual offset for drawing - adjust this to align the sprite with the ground
        # Positive values move the sprite up, negative values move it down
        self.visual_y_offset = 20  # Adjust this to align the sprite with the ground
        
        self.speed = 5.0  # Increased for better responsiveness
        self.attack_damage = 10
        self.projectile_cooldown = 0
        self.JUMP_FORCE = -12  # Negative because y increases downward
        self.GRAVITY = 0.6
        self.facing_right = True
        self.walk_anim_timer = 0
        self.walk_anim_speed = 0.2  # Lower is faster
        self.walk_anim_index = 0
        self.is_moving = False
        self.is_jumping = False
        self.y_velocity = 0  # Vertical velocity for jumping
        self.on_ground = False
        self.jump_img = pygame.Surface((30, 45))
        self.jump_img.fill((200, 50, 50))  # Lighter red for jump
        self.walk_animation = []
        for i in range(4):
            frame = pygame.Surface((30, 50))
            frame.fill((255, 50 + i*20, 50))  # Slight color variation for animation
            self.walk_animation.append(frame)
    
    def update(self, keys=None, terrain=None, camera_x=0):
        if self.projectile_cooldown > 0:
            self.projectile_cooldown -= 1

        if keys is not None and terrain is not None:
            self.is_moving = False
            dx = 0
            dy = 0

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -self.speed
                self.facing_right = False
                self.is_moving = True
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = self.speed
                self.facing_right = True
                self.is_moving = True

            if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and not self.is_jumping and self.on_ground:
                self.y_velocity = self.JUMP_FORCE  # Positive because we're adding to y position
                self.is_jumping = True
                self.on_ground = False

            # Apply gravity
            self.y_velocity = min(self.y_velocity + self.GRAVITY, 15)
            dy += self.y_velocity

            new_x = self.x + dx
            new_y = self.y + dy
            
            # Check for ground collision
            ground_height = terrain.get_ground_height(new_x + self.width/2)
            
            if new_y > ground_height - self.height:
                new_y = ground_height - self.height
                self.y_velocity = 0
                self.is_jumping = False
                self.on_ground = True
            else:
                self.on_ground = False

            # Update position
            self.x = new_x
            self.y = new_y
            
            # Update animation
            if self.is_moving and self.on_ground:
                self.walk_anim_timer += self.walk_anim_speed
                if self.walk_anim_timer >= 1.0:
                    self.walk_anim_timer = 0
                    self.walk_anim_index = (self.walk_anim_index + 1) % len(Hero._anim_frames_right)
            elif not self.is_moving:
                self.walk_anim_timer = 0
                self.walk_anim_index = 0

            # Update collision rect
            self.update_rect()
    
    def apply_colors(self, shirt_color=None, pants_color=None, hair_color=None):
        """Apply colors to different parts of the character"""
        if shirt_color is not None:
            self.shirt_color = shirt_color
        if pants_color is not None:
            self.pants_color = pants_color
        if hair_color is not None:
            self.hair_color = hair_color
            
        # We'll need to reload the sprites with the new colors
        try:
            sprite_sheet = load_sprite('base_sheet_character.png')
            if sprite_sheet:
                frame_width, frame_height = 32, 32
                
                # Clear existing frames
                Hero._anim_frames_right = []
                Hero._anim_frames_left = []
                
                # Reload walking right frames with colors
                for i in range(4):
                    frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                    frame.blit(sprite_sheet, (0, 0), (i * frame_width, 0, frame_width, frame_height))
                    
                    # Apply color tints to different parts
                    colored_frame = frame.copy()
                    
                    # Apply a simple color tint to the character
                    # Create a colored version of the frame
                    colored_frame = frame.copy()
                    
                    # Apply shirt color (top half)
                    for y in range(frame_height // 2):
                        for x in range(frame_width):
                            # Get the original pixel
                            r, g, b, a = frame.get_at((x, y))
                            # Only tint non-transparent pixels
                            if a > 0:
                                # Blend with shirt color (25% strength)
                                nr = min(255, r + self.shirt_color[0] // 4)
                                ng = min(255, g + self.shirt_color[1] // 4)
                                nb = min(255, b + self.shirt_color[2] // 4)
                                colored_frame.set_at((x, y), (nr, ng, nb, a))
                    
                    # Apply pants color (bottom half)
                    for y in range(frame_height // 2, frame_height):
                        for x in range(frame_width):
                            # Get the original pixel
                            r, g, b, a = frame.get_at((x, y))
                            # Only tint non-transparent pixels
                            if a > 0:
                                # Blend with pants color (30% strength)
                                nr = min(255, r + self.pants_color[0] // 3)
                                ng = min(255, g + self.pants_color[1] // 3)
                                nb = min(255, b + self.pants_color[2] // 3)
                                colored_frame.set_at((x, y), (nr, ng, nb, a))
                    
                    # Apply hair color (top portion)
                    for y in range(frame_height // 3):
                        for x in range(frame_width):
                            # Get the original pixel
                            r, g, b, a = frame.get_at((x, y))
                            # Only tint non-transparent pixels
                            if a > 0:
                                # Blend with hair color (35% strength)
                                nr = min(255, r + self.hair_color[0] // 3)
                                ng = min(255, g + self.hair_color[1] // 3)
                                nb = min(255, b + self.hair_color[2] // 3)
                                colored_frame.set_at((x, y), (nr, ng, nb, a))
                    
                    Hero._anim_frames_right.append(colored_frame)
                
                # Update left frames
                Hero._anim_frames_left = [pygame.transform.flip(f, True, False) for f in Hero._anim_frames_right]
                
                # Update other sprites
                if Hero._anim_frames_right:
                    Hero._idle_right = Hero._anim_frames_right[0]
                    Hero._idle_left = Hero._anim_frames_left[0]
                    Hero._jump_right = Hero._anim_frames_right[0]
                    Hero._jump_left = Hero._anim_frames_left[0]
        except Exception as e:
            if DEBUG_MODE:
                print(f"Error applying colors: {e}")
    
    def draw(self, screen, camera_x):
        # Select the appropriate sprite based on state
        if self.is_jumping:
            sprite = Hero._jump_right if self.facing_right else Hero._jump_left
        elif self.is_moving:
            # Use the appropriate walking animation frames based on direction
            frames = Hero._anim_frames_right if self.facing_right else Hero._anim_frames_left
            if frames:  # Make sure we have frames to use
                sprite = frames[self.walk_anim_index % len(frames)]
            else:
                sprite = None
        else:
            sprite = Hero._idle_right if self.facing_right else Hero._idle_left
            
        # Draw the character
        if sprite and hasattr(sprite, 'get_rect'):
            # Apply visual offset for drawing
            draw_y = self.y + self.visual_y_offset
                
            # Use nearest neighbor scaling for crisp pixel art
            scaled = pygame.transform.scale(sprite, (self.width, self.height))
            
            # Apply color to different parts of the character (fallback)
            # This is a simplified version that won't cause visual artifacts
            width, height = scaled.get_width(), scaled.get_height()
            
            # Create a new surface with per-pixel alpha
            colored = pygame.Surface((width, height), pygame.SRCALPHA)
            
            # Copy the original image
            colored.blit(scaled, (0, 0))
            
            # Apply shirt color (top half)
            for y in range(height // 2):
                for x in range(width):
                    r, g, b, a = colored.get_at((x, y))
                    if a > 0:  # Only modify non-transparent pixels
                        # Blend with shirt color (25% strength)
                        nr = min(255, r + self.shirt_color[0] // 4)
                        ng = min(255, g + self.shirt_color[1] // 4)
                        nb = min(255, b + self.shirt_color[2] // 4)
                        colored.set_at((x, y), (nr, ng, nb, a))
            
            # Apply pants color (bottom half)
            for y in range(height // 2, height):
                for x in range(width):
                    r, g, b, a = colored.get_at((x, y))
                    if a > 0:  # Only modify non-transparent pixels
                        # Blend with pants color (30% strength)
                        nr = min(255, r + self.pants_color[0] // 3)
                        ng = min(255, g + self.pants_color[1] // 3)
                        nb = min(255, b + self.pants_color[2] // 3)
                        colored.set_at((x, y), (nr, ng, nb, a))
            
            # Apply hair color (top portion)
            for y in range(height // 3):
                for x in range(width):
                    r, g, b, a = colored.get_at((x, y))
                    if a > 0:  # Only modify non-transparent pixels
                        # Blend with hair color (35% strength)
                        nr = min(255, r + self.hair_color[0] // 3)
                        ng = min(255, g + self.hair_color[1] // 3)
                        nb = min(255, b + self.hair_color[2] // 3)
                        colored.set_at((x, y), (nr, ng, nb, a))
            
            # Update the scaled surface
            scaled = colored
                
            screen.blit(scaled, (self.x - camera_x, draw_y))
        else:
            # Fallback to a colored rectangle if sprite loading failed
            pygame.draw.rect(screen, self.shirt_color, (self.x - camera_x, self.y, self.width, self.height))
    def shoot_projectile(self, vx, vy):
        if DEBUG_MODE:
            # print(f"Attempting to shoot projectile with velocity: ({vx:.2f}, {vy:.2f})")
            # print(f"Cooldown: {self.projectile_cooldown}")
            pass
        if self.projectile_cooldown <= 0:
            projectile = Projectile(self.x + self.width // 2, 
                                  self.y + self.height // 2,
                                  vx, vy)
            self.projectile_cooldown = 30  # Cooldown in frames
            if DEBUG_MODE:
                # print(f"Hero shot projectile at x={self.x}, y={self.y} with velocity=({vx:.2f}, {vy:.2f})")
                # print(f"Projectile created at x: {projectile.x}, y: {projectile.y}")
                if not self.is_jumping:
                    self.walk_anim_index = 0
                self.walk_anim_timer = 0

    # Animation logic has been moved to the update method

def main():
    # print("Starting game initialization...")
    # Initialize pygame and the font system
    pygame.init()
    pygame.font.init()  # Initialize the font module
    # print("Pygame and font modules initialized")
    
    # Load sprites for the game
    stone_img = load_sprite('stone.png')
    tree_img = load_sprite('tree.png')
    hero_img = load_sprite('hero.png')
    goblin_img = load_sprite('goblin.png')
    grass_img = load_sprite('grass.png')
    dirt_img = load_sprite('dirt.png')
    
    # Set up the display
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Hero vs Goblin")
    clock = pygame.time.Clock()
    
    # Load fonts
    try:
        font = pygame.font.SysFont("Arial", 18, bold=True)
        font_big = pygame.font.SysFont("Arial", 64, bold=True)
        font_small = pygame.font.SysFont("Arial", 32)
    except Exception as e:
        # print(f"Warning: Could not load system fonts: {e}")
        # Fallback to default font
        font = pygame.font.Font(None, 24)
        font_big = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 32)
    
    # Create terrain first!
    terrain = Terrain(grass_img, dirt_img, stone_img, tree_img)

    # Create character with custom colors (RGB values 0-255)
    hero = Hero(
        shirt_color=(50, 100, 200),  # Blue shirt
        pants_color=(80, 50, 20),    # Brown pants
        hair_color=(139, 69, 19)     # Brown hair
    )
    goblins = []  # List of goblins
    GOBLIN_RESPAWN_INTERVAL = 180  # Try to spawn every 3 seconds
    goblin_spawn_timer = 0
    MAX_GOBLINS = 5
    
    # Position hero so their feet are at ground level, accounting for visual offset
    hero.y = terrain.get_ground_height(hero.x + hero.width//2) - hero.height + hero.visual_y_offset
    hero.update_rect()

    projectiles = []
    camera_x = 0
    
    
    # Game loop
    running = True
    # print("Entering main game loop...")
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Shoot toward mouse position
                try:
                    mx, my = pygame.mouse.get_pos()
                    hero_cx = hero.x + hero.width // 2
                    hero_cy = hero.y + hero.height // 2
                    # Adjust mouse x for camera
                    world_mx = mx + camera_x
                    dx = world_mx - hero_cx
                    dy = my - hero_cy
                    dist = math.hypot(dx, dy)
                    if dist == 0:
                        dist = 1
                    vx = (dx / dist) * PROJECTILE_SPEED
                    vy = (dy / dist) * PROJECTILE_SPEED
                    
                    # Create a new projectile
                    try:
                        projectile = Projectile(
                            hero_cx,  # x
                            hero_cy,  # y
                            vx,       # velocity x
                            vy        # velocity y
                        )
                        projectiles.append(projectile)
                        # print(f"Fired projectile at ({vx:.1f}, {vy:.1f})")
                    except Exception as e:
                        # print(f"Error creating projectile: {e}")
                        pass
                    
                except Exception as e:
                    # print(f"Error shooting projectile: {e}")
                    pass

        # Get keys
        keys = pygame.key.get_pressed()
        
        # Update hero - handles both movement and animation
        hero.update(keys, terrain, camera_x)
        
        # Update goblins
        for goblin in goblins:
            goblin.update(hero.x, terrain, camera_x)
        
        # Update projectiles
        for projectile in projectiles[:]:  # Create a copy to safely remove projectiles
            projectile.update()
            # Check projectile collision with goblin
            for goblin in goblins:
                if goblin.rect.colliderect(projectile.rect):
                    goblin.health -= 10
                    projectiles.remove(projectile)
                    if goblin.health <= 0:
                        goblins.remove(goblin)
                    break
            # Remove projectile if it goes off screen
            if projectile.x < 0 or projectile.x > terrain.terrain_width:
                projectiles.remove(projectile)
        
        # Collision detection
        for goblin in goblins:
            if goblin.rect.colliderect(hero.rect):
                if goblin.attack_cooldown <= 0:
                    hero.health -= goblin.attack_damage
                    goblin.attack_cooldown = 60
        # Update camera position
        camera_x = hero.x - WINDOW_WIDTH // 2
        # Keep camera within bounds
        camera_x = max(0, min(camera_x, terrain.terrain_width - WINDOW_WIDTH))
        
        # Clear the screen with sky blue
        screen.fill(SKY_BLUE)
        
        # Draw terrain first (background)
        terrain.draw(screen, camera_x)
        
        # Draw all game objects in proper order
        # 1. Draw all projectiles first (behind characters)
        for projectile in projectiles:
            projectile.draw(screen, camera_x)
            
        # 2. Draw all goblins with health bars
        for goblin in goblins:
            goblin.draw(screen, camera_x)
            # Draw health bar above goblin
            bar_width = 40  # Slightly wider for better visibility
            bar_height = 4
            health_ratio = max(0, min(1, goblin.health / 30))  # Clamp between 0 and 1
            bar_x = int(goblin.x - camera_x + (goblin.width - bar_width) // 2)
            bar_y = int(goblin.y - 10)  # Slightly higher above the goblin
            # Background (gray)
            pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
            # Health (red)
            if health_ratio > 0:  # Only draw health if there's some left
                pygame.draw.rect(screen, (255, 50, 50), (bar_x, bar_y, int(bar_width * health_ratio), bar_height))
            
        # 3. Draw the hero (on top of goblins and projectiles)
        # print("About to draw hero")
        hero.draw(screen, camera_x)
        # print("Finished drawing hero")
        
        # Draw UI elements (health bar, etc.) on top of everything
        # --- Draw player health bar ---
        bar_x, bar_y = 20, 20
        bar_width, bar_height = 200, 24
        health_ratio = hero.health / 100
        pygame.draw.rect(screen, (60, 60, 60), (bar_x-2, bar_y-2, bar_width+4, bar_height+4))  # border
        pygame.draw.rect(screen, (180, 0, 0), (bar_x, bar_y, bar_width, bar_height))  # background (red)
        pygame.draw.rect(screen, (0, 200, 0), (bar_x, bar_y, int(bar_width * health_ratio), bar_height))  # green health
        # Draw health number
        health_text = font.render(f"HP: {max(0, int(hero.health))}", True, (255,255,255))
        screen.blit(health_text, (bar_x + 8, bar_y + 2))

        # --- Death screen ---
        if hero.health <= 0:
            # Draw a semi-transparent red overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((200, 0, 0, 140))  # RGBA, 140/255 alpha
            screen.blit(overlay, (0, 0))

            # Draw 'You died' and Respawn button
            font_big = pygame.font.SysFont("Arial", 64, bold=True)
            font_small = pygame.font.SysFont("Arial", 32)
            died_text = font_big.render("You died", True, (255, 255, 255))
            button_text = font_small.render("Respawn", True, (255,255,255))

            # Button dimensions
            button_width, button_height = 220, 60
            button_x = WINDOW_WIDTH//2 - button_width//2
            button_y = WINDOW_HEIGHT//2 + 10
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

            # Draw texts and button
            screen.blit(died_text, (WINDOW_WIDTH//2 - died_text.get_width()//2, WINDOW_HEIGHT//2 - 100))
            pygame.draw.rect(screen, (80, 0, 0), button_rect, border_radius=12)
            pygame.draw.rect(screen, (255, 255, 255), button_rect, 3, border_radius=12)
            screen.blit(button_text, (button_x + button_width//2 - button_text.get_width()//2, button_y + button_height//2 - button_text.get_height()//2))

            pygame.display.flip()
            # Pause game updates until button is clicked
            respawned = False
            while not respawned:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mx, my = pygame.mouse.get_pos()
                        if button_rect.collidepoint(mx, my):
                            # Respawn hero
                            hero.health = 100
                            hero.x = 100
                            hero.y = terrain.get_ground_height(hero.x) - hero.height
                            hero.update_rect()
                            respawned = True
                pygame.time.wait(50)
            just_respawned = True

        # If we just respawned, skip the rest of the frame and start next loop
        if 'just_respawned' in locals() and just_respawned:
            just_respawned = False
            continue

        # Remove projectiles that go off screen
        for projectile in projectiles[:]:  # Create a copy to safely remove projectiles
            if (projectile.x < 0 or projectile.x > terrain.terrain_width or
                projectile.y < 0 or projectile.y > WINDOW_HEIGHT):
                projectiles.remove(projectile)
        
        
        # Draw goblin
        # Removed goblin debug rectangle and health bar
        # print(f"[DEBUG] Drawing goblin: using sprite? {'yes' if goblin_img is not None else 'no'}")
        
        # Draw attack ranges
        if hero.attacking:
            pygame.draw.circle(screen, (255, 255, 0), (hero.x + hero.width//2, hero.y + hero.height//2), hero.attack_range, 2)
        
        # --- Goblin spawn/despawn logic ---
        goblin_spawn_timer += 1
        if goblin_spawn_timer >= GOBLIN_RESPAWN_INTERVAL and len(goblins) < MAX_GOBLINS:
            # Pick a random x not too close to hero
            attempts = 0
            while attempts < 10:
                spawn_x = random.randint(0, terrain.terrain_width - GOBLIN_WIDTH)
                if abs(spawn_x - hero.x) > 400:
                    try:
                        new_goblin = Goblin()
                        new_goblin.x = spawn_x
                        new_goblin.y = terrain.get_ground_height(spawn_x) - GOBLIN_HEIGHT
                        new_goblin.update_rect()
                        new_goblin.despawn_timer = 0
                        goblins.append(new_goblin)
                        # print(f"Spawned new goblin at ({new_goblin.x}, {new_goblin.y})")
                        break
                    except Exception as e:
                        # print(f"Error spawning goblin: {e}")
                        pass
                attempts += 1
            goblin_spawn_timer = 0
        # Despawn goblins if off screen too long
        for goblin in list(goblins):
            # If goblin is on screen, reset timer
            if 0 <= goblin.x - camera_x <= WINDOW_WIDTH:
                goblin.despawn_timer = 0
            else:
                goblin.despawn_timer = getattr(goblin, 'despawn_timer', 0) + 1
                if goblin.despawn_timer > FPS * 10:  # 10 seconds off screen
                    goblins.remove(goblin)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
