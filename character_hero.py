import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT, DEBUG_MODE
from utils import load_sprite
from character_base import Character
from projectile import Projectile, IceProjectile


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
        # Initialize the parent Character class with default values
        super().__init__(
            x=WINDOW_WIDTH // 2,  # Center of the screen
            y=WINDOW_HEIGHT - 100,  # Near the bottom
            width=PLAYER_WIDTH,
            height=PLAYER_HEIGHT,
            color=(255, 255, 255),  # White
            health=100,  # Starting health
            sprite_images=None
        )
        
        # Hero-specific attributes
        self.holding_staff = False  # Start without staff equipped
        self.staff_type = 'fire'  # 'fire' or 'ice'
        self.staff_img = load_sprite('wizard_staff.png')
        self.ice_staff_img = load_sprite('ice_staff.png')
        
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
        
        # Set up the sprite list
        self.sprite_images = [Hero._idle_right] if Hero._idle_right else None
        self.visual_y_offset = 20  # Visual offset for drawing
        
        # Movement and animation settings
        self.speed = 5.0
        self.attack_damage = 10
        self.projectile_cooldown = 0
        self.JUMP_FORCE = -12
        self.GRAVITY = 0.6
        self.facing_right = True
        self.walk_anim_timer = 0
        self.walk_anim_speed = 0.15  # Adjusted to a moderate speed
        self.walk_anim_index = 0
        self.is_moving = False
        self.is_jumping = False
        self.y_velocity = 0
        self.on_ground = False
    
    def switch_staff(self):
        """Switch between fire and ice staff"""
        if self.holding_staff:
            self.staff_type = 'ice' if self.staff_type == 'fire' else 'fire'
            return True
        return False

    def update(self, keys=None, terrain=None, camera_x=0, dt=1.0/60.0, events=None):
        # Handle staff switching - now handled in event loop
        # The switch_staff method is called from the main game loop on KEYDOWN event

        if self.projectile_cooldown > 0:
            self.projectile_cooldown -= dt * 60  # Convert to frames assuming 60 FPS

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
            
            # Update animation timer with delta time
            if self.is_moving and self.on_ground:
                self.walk_anim_timer += dt * 1.5  # Slightly faster than normal
                if self.walk_anim_timer >= self.walk_anim_speed:
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
        if self.holding_staff:
            # Get the appropriate staff image based on staff type
            staff_img = self.get_active_staff_image()
            if not staff_img:
                return
                
            # Get original staff size and scale it up slightly (1.5x)
            original_width, original_height = staff_img.get_size()
            scale_factor = 1.5
            staff_width = int(original_width * scale_factor)
            staff_height = int(original_height * scale_factor)
            staff_scaled = pygame.transform.scale(staff_img, (staff_width, staff_height))
            
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
    def get_active_staff_image(self):
        """Return the appropriate staff image based on current staff type"""
        return self.ice_staff_img if self.staff_type == 'ice' else self.staff_img

    def shoot_projectile(self, vx, vy):
        if not self.holding_staff:
            return None  # Can't shoot without the staff
            
        if DEBUG_MODE:
            pass
            
        if self.projectile_cooldown <= 0:
            # Create the appropriate projectile type based on staff
            if self.staff_type == 'ice':
                projectile = IceProjectile(self.x + self.width // 2, 
                                        self.y + self.height // 2,
                                        vx, vy)
            else:  # fire staff (default)
                projectile = Projectile(self.x + self.width // 2, 
                                     self.y + self.height // 2,
                                     vx, vy)
            
            self.projectile_cooldown = 30  # Cooldown in frames
            if not self.is_jumping:
                self.walk_anim_index = 0
            self.walk_anim_timer = 0
            return projectile
        return None

    # Animation logic has been moved to the update method