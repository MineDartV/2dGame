import os
import pygame
import random
from pathlib import Path
from settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT, GOBLIN_WIDTH, GOBLIN_HEIGHT,
    DEBUG_MODE, ASSETS_DIR
)
from utils import load_sprite, load_spritesheet
from character_base import Character

# Get the directory containing this file
thisdir = Path(__file__).parent.resolve()

class Goblin(Character):
    def __init__(self):
        # Initialize with default values first
        # Position will be adjusted after loading the sprite
        super().__init__(WINDOW_WIDTH - 100,  # Temporary x position
                        0,  # Will be set after loading sprite
                        GOBLIN_WIDTH, 
                        GOBLIN_HEIGHT, 
                        (34, 139, 34),  # Goblin green
                        50, [])
        
        # Load sprite sheet and set up animations
        self.setup_animations()
        
        # Set initial state
        self.current_state = 'idle'
        self.facing_right = False  # Track direction for flipping sprites
        self.speed = 2.0  # Adjusted for better movement
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
        
        # Animation state
        self.animation_phase = 'idle'  # 'start_run', 'running', 'stop_run'
        self.animation_progress = 0
        self.last_direction = 0  # Track last movement direction for smooth stopping
    def setup_animations(self):
        """Load and set up all animations from the sprite sheet"""
        try:
            # Load the sprite sheet (3 rows: idle, walk, death)
            # Original frame dimensions in the sprite sheet
            original_frame_width, original_frame_height = 256, 341
            
            # Calculate scale factor to fit GOBLIN_WIDTH while maintaining aspect ratio
            self.scale_factor = GOBLIN_WIDTH / original_frame_width
            self.sprite_width = int(original_frame_width * self.scale_factor)
            self.sprite_height = int(original_frame_height * self.scale_factor)
            
            # Update the hitbox to match the sprite size (slightly smaller for better gameplay)
            self.width = int(self.sprite_width * 0.7)
            self.height = self.sprite_height
            
            # Load the sprite sheet once
            sprite_path = thisdir / 'assets' / 'goblin_idle__walk_death.png'
            if not sprite_path.exists():
                # Fallback to ASSETS_DIR if not found in local assets
                sprite_path = ASSETS_DIR / 'goblin_idle__walk_death.png'
                
            if not sprite_path.exists():
                raise FileNotFoundError(f"Could not find goblin sprite sheet at {sprite_path}")
                
            sprite_sheet = pygame.image.load(str(sprite_path)).convert_alpha()
            
            # Helper function to extract a single frame
            def get_frame(row, col):
                x = col * original_frame_width
                y = row * original_frame_height
                frame = pygame.Surface((original_frame_width, original_frame_height), pygame.SRCALPHA)
                frame.blit(sprite_sheet, (0, 0), (x, y, original_frame_width, original_frame_height))
                if self.scale_factor != 1.0:
                    new_width = max(1, int(original_frame_width * self.scale_factor))
                    new_height = max(1, int(original_frame_height * self.scale_factor))
                    frame = pygame.transform.scale(frame, (new_width, new_height))
                return frame
            
            # Create animation sequences
            idle_frames = [get_frame(0, i % 8) for i in range(2)]  # First row, first 2 frames
            
            # Custom walk sequence as specified: 1,2,3,4,3,4,3,4... then 3,2,1 when stopping
            walk_frames = [
                get_frame(1, 0),  # Row 2, Col 1 (start)
                get_frame(1, 1),  # Row 2, Col 2
                get_frame(1, 2),  # Row 2, Col 3
                get_frame(1, 3),  # Row 2, Col 4
            ]
            
            # Death animation (all frames in row 3)
            death_frames = [get_frame(2, i) for i in range(8)]
            
            # Store animations
            self.animations = {
                'idle': idle_frames,
                'walk': walk_frames,
                'death': death_frames
            }
            
            # Animation state
            self.current_animation_name = 'idle'
            self.current_animation = self.animations['idle']
            self.animation_frame = 0
            self.animation_time = 0
            self.animation_speed = 0.2  # Seconds per frame
            
            # Custom walk animation state
            self.walk_phase = 'idle'  # 'start', 'run', 'stop', 'idle'
            self.walk_progress = 0
            
            # Position the goblin on the ground
            ground_height = WINDOW_HEIGHT - self.sprite_height - 10  # 10 pixels above bottom
            self.y = ground_height
            self.x = min(self.x, WINDOW_WIDTH - self.sprite_width - 10)  # Keep within bounds
            
        except Exception as e:
            if DEBUG_MODE:
                print(f"Error loading goblin animations: {e}")
            # Fallback to a simple rectangle if loading fails
            self.animations = {}
    
    def update_animation(self, dt):
        """Update the current animation frame with custom run sequence"""
        if not self.animations:
            return
            
        # Store previous animation state
        prev_animation = self.current_animation_name
        
        # Update animation timer
        self.animation_time += dt
        
        # Determine animation state based on movement and health
        if self.health <= 0:
            self.current_animation_name = 'death'
        elif abs(self.wander_dir) > 0:  # Moving
            if prev_animation != 'walk':
                # Starting to move - begin start sequence
                self.walk_phase = 'start'
                self.walk_progress = 0
                self.animation_frame = 0
                self.animation_time = 0
            self.current_animation_name = 'walk'
        else:  # Not moving
            if prev_animation == 'walk' and self.walk_phase != 'idle':
                # Was moving, now stopping
                if self.walk_phase == 'start':
                    # If was just starting, go back to idle
                    self.walk_phase = 'idle'
                else:
                    # Start stop sequence
                    self.walk_phase = 'stop'
                    self.walk_progress = 0
            self.current_animation_name = 'idle'
        
        # Update current animation
        if self.current_animation_name in self.animations:
            self.current_animation = self.animations[self.current_animation_name]
            
            if self.current_animation_name == 'idle':
                # Simple idle animation (loop first 2 frames)
                frame_duration = 0.5  # seconds per frame
                self.animation_frame = int((self.animation_time / frame_duration) % 2)
                
            elif self.current_animation_name == 'walk':
                if self.walk_phase == 'start':
                    # Start sequence: 0, 1, 2, 3
                    frame_duration = 0.1  # seconds per frame during start
                    frame_count = min(4, int(self.animation_time / frame_duration))
                    self.animation_frame = min(3, frame_count)
                    
                    if frame_count >= 4:
                        self.walk_phase = 'run'
                        self.animation_time = 0
                        
                elif self.walk_phase == 'run':
                    # Running loop: alternate between frames 2 and 3
                    frame_duration = 0.15  # seconds per frame during run
                    frame_count = int(self.animation_time / frame_duration)
                    self.animation_frame = 2 + (frame_count % 2)
                    
                elif self.walk_phase == 'stop':
                    # Stop sequence: 2, 1, 0
                    frame_duration = 0.1  # seconds per frame during stop
                    frame_count = min(3, int(self.animation_time / frame_duration))
                    self.animation_frame = max(0, 2 - frame_count)
                    
                    if frame_count >= 3:
                        self.walk_phase = 'idle'
                        self.animation_time = 0
            
            elif self.current_animation_name == 'death':
                # Death animation (play once)
                frame_duration = 0.15  # seconds per frame during death
                self.animation_frame = min(len(self.current_animation) - 1, 
                                        int(self.animation_time / frame_duration))
        
        # Update facing direction based on movement
        if abs(self.wander_dir) > 0:
            self.facing_right = self.wander_dir > 0
    
    def draw(self, screen, camera_x):
        if not self.animations or not self.current_animation:
            # Fallback to rectangle if no animations loaded
            pygame.draw.rect(screen, self.color, (self.x - camera_x, self.y, self.width, self.height))
            return
            
        # Get the current frame
        if 0 <= self.animation_frame < len(self.current_animation):
            frame = self.current_animation[self.animation_frame]
            
            # Flip the frame if not facing right
            if not self.facing_right:
                frame = pygame.transform.flip(frame, True, False)
            
            # Calculate draw position (centered on the hitbox)
            draw_x = self.x - camera_x - (frame.get_width() - self.width) // 2
            draw_y = self.y - (frame.get_height() - self.height)  # Align bottom with hitbox
                
            # Draw the frame at the calculated position
            screen.blit(frame, (draw_x, draw_y))
    
    def update(self, hero_x, terrain, camera_x, dt=1.0/60.0):
        if not hasattr(self, 'sprite_height') or not self.animations:
            return  # Wait for sprite to load
            
        try:
            # Get ground height at current position
            ground_height = terrain.get_ground_height(self.x + self.width/2)  # Check ground at center
            distance = hero_x - self.x
            chase_range = 300
            
            # Update facing direction based on movement
            if abs(distance) < chase_range:
                self.state = 'chase'
                self.facing_right = distance > 0
            else:
                self.state = 'wander'
                # Only update facing direction when actually moving
                if abs(self.wander_dir) > 0:
                    self.facing_right = self.wander_dir > 0
            
            # Handle movement based on state
            move_speed = self.speed * 60 * dt  # Scale by dt and FPS
            
            if self.state == 'wander':
                if self.wander_timer <= 0:
                    # Pick a new direction and duration
                    self.wander_dir = random.choice([-1, 0, 1])
                    self.wander_timer = random.randint(40, 120)  # frames
                else:
                    self.wander_timer -= 1 * dt * 60  # Scale by FPS
                    self.x += self.wander_dir * move_speed
            elif self.state == 'chase':
                if distance > 0:
                    self.x += move_speed
                else:
                    self.x -= move_speed
            
            # Keep goblin on the ground
            target_y = ground_height - self.height
            if abs(self.y - target_y) > 1:  # Only update if significant difference
                self.y = target_y
            
            # Update position with bounds checking
            self.x = max(0, min(self.x, terrain.terrain_width - self.width))
            
            # Update animation based on current state
            self.update_animation(dt)
            
            # Update rect for collision detection
            self.update_rect()
            
            # Decrement attack cooldown
            if self.attack_cooldown > 0:
                self.attack_cooldown -= dt  # Already in seconds
                
            # Attempt attack only if cooldown is zero and in range
            if abs(distance) < self.attack_range and self.attack_cooldown <= 0:
                if self.attack():
                    self.attack_cooldown = 1.0  # 1 second cooldown
                    if DEBUG_MODE:
                        pass
            
        except Exception as e:
            if DEBUG_MODE:
                print(f"Error updating goblin: {e}")
