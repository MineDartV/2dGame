import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT, DEBUG_MODE
from utils import load_sprite
from character_base import Character
from projectile import Projectile

# Load once (outside of class or inside Hero class as class variable)
STAFF_IMG = load_sprite('wizard_staff.png')

class Hero(Character):
    # Class-level variables to store loaded sprites (shared across all instances)
    _sprites_loaded = False
    _anim_frames_right = []
    _anim_frames_left = []
    _idle_right = None
    _idle_left = None
    _jump_right = None
    _jump_left = None
    
    def __init__(self):
        # Default color for the character (white)
        self.color = (255, 255, 255)
        self.holding_staff = False  # New state variable
        
        # Load sprites only once (class-level)
        if not Hero._sprites_loaded:
            try:
                # Load the sprite sheet
                sprite_sheet = load_sprite('base_sheet_character.png')
                if sprite_sheet:
                    # Assuming each frame is 32x32 pixels in the sprite sheet
                    frame_width, frame_height = 32, 32
                    
                    # Extract walking right frames
                    for i in range(4):  # 4 frames for walking
                        frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                        frame.blit(sprite_sheet, (0, 0), (i * frame_width, 0, frame_width, frame_height))
                        Hero._anim_frames_right.append(frame)
                    
                    # Create left-facing frames by flipping right-facing ones
                    for frame in Hero._anim_frames_right:
                        Hero._anim_frames_left.append(pygame.transform.flip(frame, True, False))
                    
                    # Set up idle and jump frames
                    if Hero._anim_frames_right:
                        Hero._idle_right = Hero._anim_frames_right[0]
                        Hero._idle_left = Hero._anim_frames_left[0]
                        Hero._jump_right = Hero._anim_frames_right[0]
                        Hero._jump_left = Hero._anim_frames_left[0]
                    
                    Hero._sprites_loaded = True
            except Exception as e:
                if DEBUG_MODE:
                    print(f"Error loading hero sprites: {e}")
        
        # Initialize with the idle right sprite
        sprite_list = [Hero._idle_right] if Hero._idle_right else None
        initial_y = WINDOW_HEIGHT - PLAYER_HEIGHT - 10
        
        # Initialize parent class with default white color
        super().__init__(100, initial_y, PLAYER_WIDTH, PLAYER_HEIGHT, 
                       self.color, 100, sprite_list)
        
        # Visual offset for drawing
        self.visual_y_offset = 20
        
        # Movement and animation settings
        self.speed = 5.0
        self.attack_damage = 10
        self.projectile_cooldown = 0
        self.JUMP_FORCE = -12
        self.GRAVITY = 0.6
        self.facing_right = True
        self.walk_anim_timer = 0
        self.walk_anim_speed = 0.2
        self.walk_anim_index = 0
        self.is_moving = False
        self.is_jumping = False
        self.y_velocity = 0
        self.on_ground = False
    
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
            
            # Draw the sprite directly without color modifications
            screen.blit(scaled, (self.x - camera_x, draw_y))
            # --- DRAW STAFF ---
        else:
            # Fallback to a colored rectangle if sprite loading failed
            pygame.draw.rect(screen, (255, 255, 255), (self.x - camera_x, self.y, self.width, self.height))
        if self.holding_staff and STAFF_IMG:
            # Get original staff size and scale it up slightly (1.5x)
            original_width, original_height = STAFF_IMG.get_size()
            scale_factor = 1.5
            staff_width = int(original_width * scale_factor)
            staff_height = int(original_height * scale_factor)
            staff_scaled = pygame.transform.scale(STAFF_IMG, (staff_width, staff_height))
            
            # Rotate staff based on facing direction
            angle = -45 if self.facing_right else 45  # 45 degrees right, -45 degrees left
            staff_rotated = pygame.transform.rotate(staff_scaled, angle)
            
            # Vertical position - hands are about 70% down the character
            hand_offset_y = self.height * 0.7
            
            # Horizontal position - adjust based on facing direction
            if self.facing_right:
                # Position on right side but closer to body when facing right
                staff_x = self.x - camera_x + self.width - (staff_width * 1.1)  # Increased from 0.7 to 0.9 to move left
            else:
                # Position on left side but closer to body when facing left
                staff_x = self.x - camera_x - self.width + (staff_width * 1.7)  # Increased from 0.3 to 0.5 to move right
            
            # Vertical position - align bottom of staff with hands
            staff_y = self.y + hand_offset_y - staff_height
            
            # Draw the staff
            screen.blit(staff_rotated, (staff_x, staff_y))
    def shoot_projectile(self, vx, vy):
        if not self.holding_staff:
            return None  # Can't shoot without the staff
            
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
                pass
            if not self.is_jumping:
                self.walk_anim_index = 0
            self.walk_anim_timer = 0
            return projectile
        return None

    # Animation logic has been moved to the update method