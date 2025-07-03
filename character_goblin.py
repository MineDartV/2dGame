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
        self.attack_range = 100  # Increased attack range for better testing
        self.attack_cooldown = 0
        self.attack_damage = 5
        self.attack_animation_timer = 0
        self.is_attacking = False
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
        self.animation_phase = 'idle'  # 'start', 'run', 'stop', 'idle'
        self.animation_progress = 0
        self.last_direction = 0  # Track last movement direction for smooth stopping
        self.walk_frame = 0  # Current frame in walk animation
        self.walk_frame_time = 0  # Time since last frame change

    def setup_animations(self):
        """Load and set up all animations from the sprite sheets"""
        try:
            # Load the run sprite sheet (goblin_run.png)
            run_sprite_path = thisdir / 'assets' / 'goblin_run.png'
            if not run_sprite_path.exists():
                run_sprite_path = ASSETS_DIR / 'goblin_run.png'
                
            if not run_sprite_path.exists():
                raise FileNotFoundError(f"Could not find goblin run sprite at {run_sprite_path}")
                
            # Load the main sprite sheet for idle and death
            sprite_path = thisdir / 'assets' / 'goblin_idle__walk_death.png'
            if not sprite_path.exists():
                sprite_path = ASSETS_DIR / 'goblin_idle__walk_death.png'
                
            if not sprite_path.exists():
                raise FileNotFoundError(f"Could not find goblin sprite sheet at {sprite_path}")
                
            # Load and process run sprite sheet
            run_sprite_sheet = pygame.image.load(str(run_sprite_path)).convert_alpha()
            sprite_sheet = pygame.image.load(str(sprite_path)).convert_alpha()
            
            # Frame dimensions - adjusted to match actual sprite sheet
            original_frame_width, original_frame_height = 256, 341  # For idle/death
            run_frame_width, run_frame_height = 253, 282  # Updated run animation frame size
            
            # Target size for all sprites
            target_width = 32
            target_height = 38  # Slightly taller to prevent floating
            
            # Calculate scale factors for each sprite sheet
            idle_scale = target_width / original_frame_width
            run_scale = target_width / run_frame_width
            
            # Set sprite dimensions to target size
            self.sprite_width = target_width
            self.sprite_height = target_height
            
            # Update the hitbox to match the sprite size (slightly smaller for better gameplay)
            self.width = int(self.sprite_width * 0.7)
            self.height = self.sprite_height
            
            # Helper function to extract and scale a single frame
            def get_frame(sheet, row, col, frame_width, frame_height, scale, is_run_sheet=False):
                # Add 1 pixel padding to prevent edge artifacts
                x = col * frame_width + (1 if is_run_sheet and col > 0 else 0)
                y = row * frame_height
                
                # Adjust width to prevent overlap with next frame
                width = frame_width - (1 if is_run_sheet and col < 3 else 0)
                
                # Create a clean surface with the exact frame size
                frame = pygame.Surface((width, frame_height), pygame.SRCALPHA)
                frame.blit(sheet, (0, 0), (x, y, width, frame_height))
                
                # Scale to target size while maintaining aspect ratio
                return pygame.transform.scale(frame, (target_width, target_height))
            
            # Create animation sequences
            # Idle animation (from main sprite sheet)
            idle_frames = [get_frame(sprite_sheet, 0, i % 8, original_frame_width, original_frame_height, idle_scale) 
                          for i in range(2)]
            
            # Run animation (from goblin_run.png)
            run_sheet_width = run_sprite_sheet.get_width()
            run_frame_count = run_sheet_width // run_frame_width
            
            # Get all run frames (1-4) with proper scaling and edge handling
            run_frames = [get_frame(run_sprite_sheet, 0, i, run_frame_width, run_frame_height, run_scale, is_run_sheet=True) 
                        for i in range(min(4, run_frame_count))]
            
            # Create ping-pong sequence: 1-2-3-4-3-2-1-2...
            walk_frames = run_frames + run_frames[-2:0:-1]
            
            # Death animation (from main sprite sheet)
            death_frames = [get_frame(sprite_sheet, 2, i, original_frame_width, original_frame_height, idle_scale) 
                          for i in range(8)]
            
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
            
            # Position the goblin on the ground - moved down further
            ground_height = WINDOW_HEIGHT - self.sprite_height - 15 + 20  # 15 pixels above bottom, plus 20 pixel shift down
            self.y = ground_height + 10  # Additional 10 pixels down to fix floating
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
                # Starting to move - begin walk sequence
                self.walk_phase = 'start'
                self.animation_time = 0
                self.walk_frame = 0
            self.current_animation_name = 'walk'
        else:  # Not moving
            if prev_animation == 'walk' and self.walk_phase != 'idle':
                # Was moving, now stopping
                self.walk_phase = 'stop'
                self.animation_time = 0
            self.current_animation_name = 'idle'
        
        # Update current animation
        if self.current_animation_name in self.animations:
            self.current_animation = self.animations[self.current_animation_name]
            
            if self.current_animation_name == 'idle':
                # Simple idle animation (loop first 2 frames)
                frame_duration = 0.2  # seconds per frame
                self.animation_frame = int((self.animation_time / frame_duration) % 2)
                
            elif self.current_animation_name == 'walk':
                frame_duration = 0.1  # seconds per frame during walk
                
                # Update walk frame with ping-pong effect
                self.walk_frame_time += dt
                if self.walk_frame_time >= frame_duration:
                    # Total frames in the ping-pong sequence: 1-2-3-4-3-2 (6 frames total)
                    self.walk_frame = (self.walk_frame + 1) % 6
                    self.walk_frame_time = 0
                
                self.animation_frame = self.walk_frame
                
            elif self.current_animation_name == 'death':
                # Death animation (play once)
                frame_duration = 0.15  # seconds per frame during death
                self.animation_frame = min(len(self.current_animation) - 1, 
                                        int(self.animation_time / frame_duration))
        
        # Facing direction is now handled in the update method
    
    def draw(self, screen, camera_x):
        if not self.animations or not self.current_animation:
            # Fallback to rectangle if no animations loaded
            pygame.draw.rect(screen, self.color, (self.x - camera_x, self.y, self.width, self.height))
            return
            
        # Get the current frame
        if 0 <= self.animation_frame < len(self.current_animation):
            frame = self.current_animation[self.animation_frame]
            
            # For run animation, we need to handle facing direction specially
            if self.current_animation_name == 'walk':
                # Always draw the frame as-is (facing right)
                # We'll flip it if needed using the transform
                if not self.facing_right:
                    frame = pygame.transform.flip(frame, True, False)
                
                # Calculate position to keep feet planted
                draw_x = self.x - camera_x - (frame.get_width() - self.width) // 2
                draw_y = self.y + self.height - frame.get_height()
            else:
                # For other animations, use the normal flip logic
                if not self.facing_right:
                    frame = pygame.transform.flip(frame, True, False)
                
                # Standard positioning for non-walk animations
                draw_x = self.x - camera_x - (frame.get_width() - self.width) // 2
                draw_y = self.y - (frame.get_height() - self.height)
            
            # Draw the frame at the calculated position
            screen.blit(frame, (draw_x, draw_y))
            
            # Draw health bar above the goblin
            health_bar_width = 40
            health_bar_height = 5
            health_bar_x = draw_x + (frame.get_width() - health_bar_width) // 2
            health_bar_y = draw_y - 10  # Position above the goblin's head
            
            # Draw health bar background (red)
            pygame.draw.rect(screen, (255, 0, 0), 
                          (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
            
            # Calculate current health width
            health_ratio = max(0, min(1, self.health / 50))  # 50 is max health for goblins
            current_health_width = int(health_bar_width * health_ratio)
            
            # Draw current health (green)
            health_color = (
                int(255 * (1 - health_ratio * 0.5)),  # Red component
                int(255 * health_ratio),  # Green component
                0  # Blue component
            )
            pygame.draw.rect(screen, health_color, 
                          (health_bar_x, health_bar_y, current_health_width, health_bar_height))
    
    def update(self, hero_x, terrain, camera_x, dt=1.0/60.0, hero=None):
        if not hasattr(self, 'sprite_height') or not self.animations:
            return  # Wait for sprite to load
            
        try:
            # Get ground height at current position
            ground_height = terrain.get_ground_height(self.x + self.width/2)  # Check ground at center
            distance = hero_x - self.x
            chase_range = 300
            
            # Check if goblin is off-screen and should change direction
            screen_left = camera_x
            screen_right = camera_x + WINDOW_WIDTH
            
            # Update facing direction based on movement and screen position
            if abs(distance) < chase_range:
                self.state = 'chase'
                # Always face the hero when chasing
                self.facing_right = distance > 0
            else:
                self.state = 'wander'
                
                # If goblin is off-screen to the left and moving left
                if self.x < screen_left and not self.facing_right:
                    self.facing_right = True
                    self.wander_dir = 1  # Force movement to the right
                # If goblin is off-screen to the right and moving right
                elif self.x > screen_right and self.facing_right:
                    self.facing_right = False
                    self.wander_dir = -1  # Force movement to the left
                # Otherwise, update facing based on wander direction if not off-screen
                elif self.wander_dir != 0:
                    self.facing_right = self.wander_dir > 0
            
            # Handle movement based on state
            move_speed = self.speed * 60 * dt  # Scale by dt and FPS
            
            if self.state == 'wander':
                if self.wander_timer <= 0:
                    # Pick a new direction and duration
                    new_dir = random.choice([-1, 0, 1])
                    # Update facing direction immediately when direction changes
                    if new_dir != self.wander_dir:
                        self.wander_dir = new_dir
                        self.facing_right = self.wander_dir > 0
                    self.wander_timer = random.randint(40, 120)  # frames
                else:
                    self.wander_timer -= 1 * dt * 60  # Scale by FPS
                    self.x += self.wander_dir * move_speed
            elif self.state == 'chase':
                if distance > 0:
                    self.x += move_speed
                    self.facing_right = True
                else:
                    self.x -= move_speed
                    self.facing_right = False
            
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
                
            # Calculate actual distance to hero for attack check
            if hero is not None:  # Make sure we have a hero to attack
                # Simple distance check using x position only for now
                dx = abs(hero.x - self.x)
                
                # Debug output for distance checking
                if DEBUG_MODE and random.random() < 0.1:  # Print occasionally to avoid spam
                    print(f"Goblin to hero x-distance: {dx}, Attack range: {self.attack_range}")
                    print(f"Attack cooldown: {self.attack_cooldown}, Is attacking: {self.is_attacking}")
                
                # Simplified attack condition - only check x distance
                if dx < self.attack_range and self.attack_cooldown <= 0 and not self.is_attacking:
                    if DEBUG_MODE:
                        print("\n=== GOBLIN ATTACK STARTING ===")
                        print(f"Hero position: ({hero.x}, {hero.y}), Health: {hero.health}")
                        print(f"Goblin position: ({self.x}, {self.y})")
                    
                    self.is_attacking = True
                    self.attack_animation_timer = 0.3  # 300ms attack animation
                    
                    # Deal damage immediately when attack starts for better responsiveness
                    if hasattr(hero, 'take_damage'):
                        try:
                            if DEBUG_MODE:
                                print(f"Calling hero.take_damage({self.attack_damage})")
                            hero.take_damage(self.attack_damage)
                            self.attack_cooldown = 1.0  # 1 second between attacks
                            if DEBUG_MODE:
                                print(f"Attack successful! Hero health: {hero.health}")
                                print("=== GOBLIN ATTACK COMPLETE ===\n")
                        except Exception as e:
                            if DEBUG_MODE:
                                print(f"ERROR in goblin attack: {e}")
                                print("=== GOBLIN ATTACK FAILED ===\n")
                    else:
                        if DEBUG_MODE:
                            print("ERROR: Hero has no take_damage method!")
                            print("=== GOBLIN ATTACK FAILED ===\n")
                    
                # Handle attack animation
                if self.is_attacking:
                    self.attack_animation_timer -= dt
                    if self.attack_animation_timer <= 0:
                        self.is_attacking = False
                
                # Update cooldown
                if self.attack_cooldown > 0:
                    self.attack_cooldown -= dt
            
        except Exception as e:
            if DEBUG_MODE:
                print(f"Error updating goblin: {e}")
