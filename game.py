import pygame
import random
import math
import sys

from settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, DEBUG_MODE,
    GOBLIN_WIDTH, GOBLIN_HEIGHT,
    SKY_BLUE, PROJECTILE_SPEED, WHITE, BLACK, FONT_NAME
)
from utils import load_sprite
from character_hero import Hero
from character_goblin import Goblin
from terrain import Terrain
from projectile import Projectile
from clouds import CloudManager
from effects import ExplosionEffect, IceExplosionEffect
from day_night_cycle import DayNightCycle
from menu import StartMenu

# Game states
GAME_STATE_MENU = "menu"
GAME_STATE_PLAYING = "playing"
GAME_STATE_GAME_OVER = "game_over"

class Game:
    def __init__(self):
        # Initialize pygame and create window
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()  # Initialize the mixer module
        
        # Set up display with double buffering
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.DOUBLEBUF)
        pygame.display.set_caption("Mystic Realm")
        
        # Create a clock for frame rate control
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.show_fps = True  # Toggle FPS display with F3
        self.last_fps_update = 0
        self.fps_text = ""
        
        # For dirty rectangle updates
        self.last_screen = None
        
        # Load the icon image
        try:
            icon = load_sprite("game.png")
            icon = pygame.transform.scale(icon, (32, 32))
            pygame.display.set_icon(icon)
        except Exception as e:
            print(f"Warning: Could not load game icon: {e}")
        
        # Initialize fonts
        from settings import init_fonts
        init_fonts()
        
        # Game state
        self.state = GAME_STATE_MENU
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game objects (initialized in reset_game)
        self.hero = None
        self.goblins = []
        self.terrain = None
        self.cloud_manager = None
        self.day_night_cycle = None
        self.projectiles = []
        self.explosion_effects = []
        self.camera_x = 0
        
        # UI - Initialize fonts after pygame is ready
        try:
            self.font = pygame.font.SysFont('Arial', 36)
            self.small_font = pygame.font.SysFont('Arial', 24)
        except Exception as e:
            print(f"Warning: Could not initialize fonts: {e}")
            # Fallback to default font
            self.font = pygame.font.Font(None, 36)
            self.small_font = pygame.font.Font(None, 24)
        
        # Menu
        self.menu = StartMenu(self.screen)
        
        # Initialize game objects
        self.reset_game()
        
        # Load and play background music
        self.load_background_music()
    
    def load_background_music(self):
        """Load and play the background music in a loop"""
        try:
            music_path = "assets/sound/hero_vs_goblin_mystical_forest_theme_loopable.wav"
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.5)  # Set volume to 50%
            pygame.mixer.music.play(-1)  # -1 means loop indefinitely
        except Exception as e:
            print(f"Could not load background music: {e}")
    
    def reset_game(self):
        """Reset all game objects to their initial state"""
        # Load all terrain sprites
        grass_img = load_sprite('grass.png')
        dirt_img = load_sprite('dirt.png')
        stone_img = load_sprite('stone.png')
        tree_img = load_sprite('tree.png')
        pine_tree_img = load_sprite('pine_tree.png')
        bush_img = load_sprite('bush.png')
        flower_img = load_sprite('flower.png')
        yellow_flower_img = load_sprite('yellow_flower.png')
        
        # Create terrain with all required sprites
        self.terrain = Terrain(
            grass_img, 
            dirt_img, 
            stone_img, 
            tree_img, 
            pine_tree_img, 
            bush_img, 
            flower_img, 
            yellow_flower_img
        )
        
        # Create hero
        self.hero = Hero()
        self.hero.x = WINDOW_WIDTH // 4  # Start 1/4 from the left
        self.hero.y = WINDOW_HEIGHT - 200  # Start above ground
        
        # Create goblins
        self.goblins = []
        for i in range(3):  # Start with 3 goblins
            goblin = Goblin()
            goblin.x = WINDOW_WIDTH * 2 + i * 300  # Spread them out
            goblin.y = WINDOW_HEIGHT - 200
            self.goblins.append(goblin)
        
        # Create cloud manager
        self.cloud_manager = CloudManager()
        
        # Create day/night cycle
        self.day_night_cycle = DayNightCycle()
        
        # Clear projectiles and effects
        self.projectiles = []
        self.explosion_effects = []
        
        # Reset camera
        self.camera_x = 0
    
    def handle_events(self):
        """Handle all pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Handle key events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GAME_STATE_PLAYING:
                        self.state = GAME_STATE_MENU
                    else:
                        self.running = False
                
                # Toggle staff with 1
                if event.key == pygame.K_1 and self.state == GAME_STATE_PLAYING:
                    self.hero.holding_staff = not self.hero.holding_staff
                    # Debug: Staff holding state
                    # print(f"Holding staff: {self.hero.holding_staff}")
                
                # Switch staff type with 2 (only when holding staff)
                if event.key == pygame.K_2 and self.state == GAME_STATE_PLAYING and self.hero.holding_staff and self.hero.projectile_cooldown <= 0:
                    if self.hero.switch_staff():
                        self.hero.projectile_cooldown = 10  # Cooldown for switching
                        # Debug: Staff switching
                        # print(f"Switched to {self.hero.staff_type} staff")
            
            # Handle mouse clicks for shooting
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.state == GAME_STATE_PLAYING:
                if self.hero.holding_staff and self.hero.projectile_cooldown <= 0:
                    self.shoot_projectile()
    
    def shoot_projectile(self):
        """Shoot a projectile from the hero towards the mouse position"""
        try:
            # Get mouse position
            mx, my = pygame.mouse.get_pos()
            
            # Calculate hero's center point in world coordinates
            hero_cx = self.hero.x + self.hero.width // 2
            hero_cy = self.hero.y + self.hero.height // 2
            
            # Convert mouse position to world coordinates
            world_mx = mx + self.camera_x
            world_my = my  # Y is not affected by camera scrolling
            
            # Calculate direction vector from hero to mouse
            dx = world_mx - hero_cx
            dy = world_my - hero_cy
            
            # Normalize the direction vector
            dist = math.hypot(dx, dy)
            if dist == 0:
                dist = 1
            
            # Calculate velocity components
            vx = (dx / dist) * PROJECTILE_SPEED
            vy = (dy / dist) * PROJECTILE_SPEED
            
            # Use hero's shoot_projectile method which checks for staff
            projectile = self.hero.shoot_projectile(vx, vy)
            if projectile:  # Only add if hero is holding staff and cooldown allows
                self.projectiles.append(projectile)
                if DEBUG_MODE:
                    staff_type = self.hero.staff_type if hasattr(self.hero, 'staff_type') else 'unknown'
                    # Debug: Projectile firing
                    # print(f"Fired {staff_type} projectile: {projectile.__class__.__name__}")
                    
        except Exception as e:
            if DEBUG_MODE:
                # Debug: Projectile error
                # print(f"Error shooting projectile: {e}")
                pass
    
    def update(self, dt):
        """Update game state"""
        if self.state != GAME_STATE_PLAYING:
            return
            
        if DEBUG_MODE and random.random() < 0.01:  # Print every ~100 frames to avoid spam
            print(f"Hero position: ({self.hero.x:.1f}, {self.hero.y:.1f}), Health: {self.hero.health}")
            for i, goblin in enumerate(self.goblins):
                print(f"  Goblin {i}: pos=({goblin.x:.1f}, {goblin.y:.1f}), attacking={goblin.is_attacking}, cooldown={goblin.attack_cooldown:.2f}")
        
        # Update hero
        keys = pygame.key.get_pressed()
        self.hero.update(keys, self.terrain, self.camera_x, dt)
        
        # Update goblins
        for goblin in self.goblins:
            goblin.update(self.hero.x, self.terrain, self.camera_x, dt, self.hero)
        
        # Update projectiles
        for projectile in self.projectiles[:]:
            explosion = projectile.update(self.terrain, dt)
            if explosion:
                self.explosion_effects.append(explosion)
                self.projectiles.remove(projectile)
                continue
            
            # Check projectile collision with goblins
            for goblin in self.goblins[:]:
                if goblin.rect.colliderect(projectile.rect):
                    # Calculate damage based on projectile type
                    damage = getattr(projectile, 'damage', 10)
                    goblin.health -= damage
                    
                    # Debug output
                    if DEBUG_MODE:
                        projectile_type = 'ice' if hasattr(projectile, 'is_ice') and projectile.is_ice else 'fire'
                        # Debug: Projectile hit
                        # print(f"{projectile_type.capitalize()} projectile hit goblin for {damage} damage!")
                    
                    # Create explosion effect
                    if hasattr(projectile, 'is_ice') and projectile.is_ice:
                        self.explosion_effects.append(IceExplosionEffect(projectile.x, projectile.y))
                    else:
                        self.explosion_effects.append(ExplosionEffect(projectile.x, projectile.y))
                    
                    # Remove projectile if it hits something
                    if projectile in self.projectiles:
                        self.projectiles.remove(projectile)
                    
                    # Remove goblin if health is 0
                    if goblin.health <= 0:
                        if DEBUG_MODE:
                            # Debug: Goblin defeated
                            # print("Goblin defeated!")
                            pass
                        self.goblins.remove(goblin)
                    break
            
            # Remove projectiles that go off-screen
            if (not projectile.active or 
                projectile.x < self.camera_x - 100 or 
                projectile.x > self.camera_x + WINDOW_WIDTH + 100 or
                projectile.y < -100 or 
                projectile.y > WINDOW_HEIGHT + 100):
                if projectile in self.projectiles:
                    self.projectiles.remove(projectile)
        
        # Update explosion effects
        for effect in self.explosion_effects[:]:
            effect.update(dt)
            if not effect.active:
                self.explosion_effects.remove(effect)
        
        # Update day/night cycle
        self.day_night_cycle.update(dt)
        
        # Update clouds
        self.cloud_manager.update(dt)
        
        # Update camera to follow hero
        self.update_camera()
        
        # Check for game over
        if self.hero.health <= 0:
            self.state = GAME_STATE_GAME_OVER
    
    def is_visible(self, obj, camera_x):
        """Check if an object is within the visible screen area"""
        # Add some padding to the visibility check to account for objects that are
        # partially off-screen but still need to be rendered
        padding = 100
        obj_right = getattr(obj, 'x', 0) + getattr(obj, 'width', 0)
        screen_right = camera_x + WINDOW_WIDTH + padding
        
        return (obj_right > camera_x - padding and 
                getattr(obj, 'x', 0) < screen_right)
    
    def update_camera(self):
        """Update camera position to follow the hero"""
        # Center camera on hero with some lookahead
        target_x = self.hero.x - WINDOW_WIDTH // 3
        
        # Smooth camera movement
        self.camera_x += (target_x - self.camera_x) * 0.1
        
        # Keep camera within level bounds
        self.camera_x = max(0, min(self.camera_x, self.terrain.terrain_width - WINDOW_WIDTH))
    
    def draw(self, full_redraw=False):
        """Draw everything to the screen with optimized updates"""
        # Store the current screen for dirty rectangle updates
        if full_redraw or self.last_screen is None:
            self.last_screen = self.screen.copy()
        
        # Only update what's necessary
        update_rects = []
            
        # Draw background elements if needed
        if full_redraw or self.camera_x != getattr(self, '_last_camera_x', -9999):
            self.screen.fill(SKY_BLUE)
            self.cloud_manager.draw(self.screen, self.camera_x)
            self.terrain.draw(self.screen, self.camera_x)
            update_rects.append(pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))

        # Draw game objects
        for goblin in self.goblins:
            if self.is_visible(goblin, self.camera_x):
                rect = goblin.draw(self.screen, self.camera_x)
                if rect:
                    update_rects.append(rect)

        # Draw hero
        hero_rect = self.hero.draw(self.screen, self.camera_x)
        if hero_rect:
            update_rects.append(hero_rect)

        # Draw projectiles and effects
        for obj in self.projectiles + self.explosion_effects:
            if hasattr(obj, 'x') and self.is_visible(obj, self.camera_x):
                rect = obj.draw(self.screen, self.camera_x)
                if rect:
                    update_rects.append(rect)

        # Draw day/night cycle if it's visible
        if hasattr(self.day_night_cycle, 'is_visible') and self.day_night_cycle.is_visible():
            self.day_night_cycle.draw(self.screen)
            update_rects.append(pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))

        # Draw HUD
        self.draw_hud()

        # Draw game over screen if needed
        if self.state == GAME_STATE_GAME_OVER:
            self.draw_game_over()

        # Update FPS counter if enabled
        if hasattr(self, 'show_fps') and self.show_fps:
            self.draw_fps()

        # Update only the changed areas of the screen
        if not full_redraw and hasattr(self, 'show_fps') and not self.show_fps and update_rects:
            pygame.display.update(update_rects)
        else:
            pygame.display.flip()

        # Store the last camera position for next frame
        self._last_camera_x = self.camera_x

        # Store the current screen for next frame's dirty rects
        self.last_screen = self.screen.copy()

        return update_rects

    def draw_hud(self):
        # Create a surface for HUD elements
        hud_surface = pygame.Surface((WINDOW_WIDTH, 100), pygame.SRCALPHA)
        
        # Health bar background (red)
        health_bar_width = 200
        health_bar_height = 20
        health_bar_x = 20
        health_bar_y = 20
        
        # Draw health bar background
        pygame.draw.rect(hud_surface, (100, 0, 0), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        
        # Calculate current health width
        health_ratio = max(0, min(1, self.hero.health / 100))  # Ensure between 0 and 1
        current_health_width = int(health_bar_width * health_ratio)
        
        # Draw current health (green)
        health_color = (
            int(255 * (1 - health_ratio * 0.5)),  # Red component
            int(255 * health_ratio),               # Green component
            0                                     # Blue component
        )
        pygame.draw.rect(hud_surface, health_color, 
                        (health_bar_x, health_bar_y, current_health_width, health_bar_height))
        
        # Draw health bar border
        pygame.draw.rect(hud_surface, WHITE, (health_bar_x, health_bar_y, health_bar_width, health_bar_height), 1)
        
        # Health text
        health_text = self.small_font.render(f"{self.hero.health}/100", True, WHITE)
        health_text_x = health_bar_x + (health_bar_width - health_text.get_width()) // 2
        health_text_y = health_bar_y + (health_bar_height - health_text.get_height()) // 2
        hud_surface.blit(health_text, (health_text_x, health_text_y))

        # Staff status with icon
        staff_icon_size = 30
        staff_icon_y = health_bar_y + health_bar_height + 10
        
        if self.hero.holding_staff:
            # Draw staff type icon
            staff_icon = self.hero.ice_staff_img if self.hero.staff_type == 'ice' else self.hero.staff_img
            if staff_icon:
                # Scale icon
                icon_ratio = staff_icon_size / max(staff_icon.get_size())
                new_size = (int(staff_icon.get_width() * icon_ratio), 
                           int(staff_icon.get_height() * icon_ratio))
                staff_icon = pygame.transform.scale(staff_icon, new_size)
                hud_surface.blit(staff_icon, (health_bar_x, staff_icon_y))
            
            # Staff text
            staff_text = self.small_font.render(f"{self.hero.staff_type.capitalize()} Staff", True, WHITE)
            hud_surface.blit(staff_text, (health_bar_x + staff_icon_size + 10, staff_icon_y + 5))
        else:
            staff_text = self.small_font.render("Staff: Unequipped", True, (150, 150, 150))
            hud_surface.blit(staff_text, (health_bar_x, staff_icon_y + 5))

        # Controls hint (only if not in game over state)
        if self.state != GAME_STATE_GAME_OVER:
            controls = self.small_font.render("1: Toggle Staff | 2: Switch Staff Type", True, (200, 200, 200))
            self.screen.blit(controls, (WINDOW_WIDTH - controls.get_width() - 20, WINDOW_HEIGHT - 40))
            
        # Draw the HUD surface to the screen
        self.screen.blit(hud_surface, (0, 0))

    def draw_fps(self):
        """Draw FPS counter in the top-right corner"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_fps_update > 200:  # Update FPS counter every 200ms
            self.fps_text = f"FPS: {int(self.clock.get_fps())}"
            self.last_fps_update = current_time

        if self.fps_text:
            fps_surface = self.small_font.render(self.fps_text, True, (255, 255, 0))
            self.screen.blit(fps_surface, (WINDOW_WIDTH - 100, 10))

    def draw_game_over(self):
        """Draw game over screen"""
        # Dark overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Game over text
        game_over = self.font.render("GAME OVER", True, (255, 50, 50))
        self.screen.blit(game_over, 
                        (WINDOW_WIDTH // 2 - game_over.get_width() // 2, 
                         WINDOW_HEIGHT // 3))

        # Restart prompt
        restart = self.small_font.render("Press R to restart or ESC to quit", True, WHITE)
        self.screen.blit(restart, 
                        (WINDOW_WIDTH // 2 - restart.get_width() // 2, 
                         WINDOW_HEIGHT // 2))

    def run(self):
        """Main game loop with optimized rendering"""
        last_time = pygame.time.get_ticks()
        full_redraw = True  # Force full redraw on first frame

        while self.running:
            # Calculate delta time
            current_time = pygame.time.get_ticks()
            dt = (current_time - last_time) / 1000.0  # Convert to seconds
            last_time = current_time
            
            # Handle events
            self.handle_events()
            
            # Update game state
            self.update(dt)
            
            # Draw everything
            self.draw(full_redraw)
            full_redraw = False  # After first frame, only update what's necessary
            
            # Cap the frame rate
            self.clock.tick(self.fps)
            
            # Toggle FPS display with F3
            keys = pygame.key.get_pressed()
            if keys[pygame.K_F3]:
                self.show_fps = not self.show_fps
                pygame.time.delay(200)  # Small delay to prevent rapid toggling
    
    def draw_fps(self):
        """Draw FPS counter in the top-right corner"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_fps_update > 200:  # Update FPS counter every 200ms
            self.fps_text = f"FPS: {int(self.clock.get_fps())}"
            self.last_fps_update = current_time
        
        if self.fps_text:
            fps_surface = self.small_font.render(self.fps_text, True, (255, 255, 0))
            self.screen.blit(fps_surface, (WINDOW_WIDTH - 100, 10))
    
    def draw_game_over(self):
        """Draw game over screen"""
        # Dark overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over = self.font.render("GAME OVER", True, (255, 50, 50))
        self.screen.blit(game_over, 
                        (WINDOW_WIDTH // 2 - game_over.get_width() // 2, 
                         WINDOW_HEIGHT // 3))
        
        # Restart prompt
        restart = self.small_font.render("Press R to restart or ESC to quit", True, WHITE)
        self.screen.blit(restart, 
                        (WINDOW_WIDTH // 2 - restart.get_width() // 2, 
                         WINDOW_HEIGHT // 2))
    
    def run(self):
        """Main game loop with optimized rendering"""
        last_time = pygame.time.get_ticks()
        full_redraw = True  # Force full redraw on first frame
        
        while self.running:
            # Calculate delta time
            current_time = pygame.time.get_ticks()
            dt = (current_time - last_time) / 1000.0  # Convert to seconds
            last_time = current_time
            
            # Cap the frame rate
            self.clock.tick(self.fps)
            
            # Handle events
            self.handle_events()
            
            # Toggle FPS display with F3
            keys = pygame.key.get_pressed()
            if keys[pygame.K_F3] and not getattr(self, '_f3_pressed', False):
                self.show_fps = not self.show_fps
                full_redraw = True
            self._f3_pressed = keys[pygame.K_F3]
            
            # Update game state
            if self.state == GAME_STATE_MENU:
                # Draw the world in the background (but don't update it)
                if full_redraw:
                    self.screen.fill(SKY_BLUE)
                    self.cloud_manager.draw(self.screen, 0)
                    self.terrain.draw(self.screen, 0)
                
                # Show menu
                menu_result = self.menu.handle_events()
                if menu_result == "start_game":
                    self.state = GAME_STATE_PLAYING
                    full_redraw = True
                
                # Always redraw menu to handle animations
                self.menu.draw(pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT)))
                
            elif self.state == GAME_STATE_PLAYING:
                self.update(dt)
                self.draw(full_redraw)
                full_redraw = False
                
            elif self.state == GAME_STATE_GAME_OVER:
                # Force full redraw for game over screen
                self.draw(True)
                
                # Check for restart
                if keys[pygame.K_r]:
                    self.reset_game()
                    self.state = GAME_STATE_PLAYING
                    full_redraw = True
        
        # Clean up
        pygame.quit()
        sys.exit()

def main():
    """Main entry point"""
    game = Game()
    game.run()
    

    # Load sprites for the game
    stone_img = load_sprite('stone.png')
    tree_img = load_sprite('tree.png')
    hero_img = load_sprite('hero.png')
    goblin_img = load_sprite('goblin.png')
    grass_img = load_sprite('grass.png')
    dirt_img = load_sprite('dirt.png')
    bush_img = load_sprite('bush.png')
    flower_img = load_sprite('flower.png')
    pine_tree_img = load_sprite('pine_tree.png')
    yellow_flower_img = load_sprite('yellow_flower.png')
    
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
    
    # Create terrain and clouds
    terrain = Terrain(grass_img, dirt_img, stone_img, tree_img, pine_tree_img, 
                     bush_img, flower_img, yellow_flower_img)
    clouds = CloudManager(num_clouds=15)  # Add cloud system
    
    # Initialize day/night cycle
    day_night_cycle = DayNightCycle()

    # Create character with default colors from sprite sheet
    hero = Hero()
    goblins = []  # List of goblins
    GOBLIN_RESPAWN_INTERVAL = 180  # Try to spawn every 3 seconds
    goblin_spawn_timer = 0
    MAX_GOBLINS = 5
    
    # Position hero so their feet are at ground level, accounting for visual offset
    hero.y = terrain.get_ground_height(hero.x + hero.width//2) - hero.height + hero.visual_y_offset
    hero.update_rect()

    projectiles = []
    explosion_effects = []  # List to store active explosion effects
    camera_x = 0
    
    
    # Game loop
    running = True
    last_time = pygame.time.get_ticks()
    # print("Entering main game loop...")
    while running:
        # Calculate delta time in seconds
        current_time = pygame.time.get_ticks()
        dt = (current_time - last_time) / 1000.0  # Convert to seconds
        dt = min(dt, 0.1)  # Cap delta time to prevent large jumps
        last_time = current_time
        
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
                    
                    # Use hero's shoot_projectile method which checks for staff
                    projectile = hero.shoot_projectile(vx, vy)
                    if projectile:  # Only add if hero is holding staff and cooldown allows
                        projectiles.append(projectile)
                        if DEBUG_MODE:
                            staff_type = hero.staff_type if hasattr(hero, 'staff_type') else 'unknown'
                            # Debug: Projectile firing
                    # print(f"Fired {staff_type} projectile: {projectile.__class__.__name__}")
                    
                except Exception as e:
                    # print(f"Error shooting projectile: {e}")
                    pass
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    hero.holding_staff = not hero.holding_staff  # Toggle staff visibility
                    # Debug: Staff holding state
                    # print(f"Holding staff: {hero.holding_staff}")
                elif event.key == pygame.K_2 and hero.holding_staff and hero.projectile_cooldown <= 0:
                    if hero.switch_staff():
                        hero.projectile_cooldown = 10  # Small cooldown to prevent rapid switching
                        # Debug: Staff switching
                        # print(f"Switched to {hero.staff_type} staff")

        # Get keys
        keys = pygame.key.get_pressed()
        
        # Update hero - handles both movement and animation
        hero.update(keys, terrain, camera_x, dt)
        
        # Update all goblins and pass hero for attack targeting
        for goblin in goblins:
            goblin.update(hero.x, terrain, camera_x, dt, hero)  # Pass hero for attack targeting
        
        # Update day/night cycle
        day_night_cycle.update(dt)
        
        # Update projectiles and handle explosions
        for projectile in projectiles[:]:  # Create a copy to safely remove projectiles
            # Update projectile and check for explosions
            explosion = projectile.update(terrain, dt)
            if explosion:
                explosion_effects.append(explosion)
                projectiles.remove(projectile)
                continue
                
            # Check projectile collision with goblin
            for goblin in goblins[:]:  # Create a copy to safely remove goblins
                if goblin.rect.colliderect(projectile.rect):
                    # Calculate damage based on projectile type
                    damage = getattr(projectile, 'damage', 10)  # Default to 10 damage if not specified
                    goblin.health -= damage
                    
                    # Debug output
                    if DEBUG_MODE:
                        projectile_type = 'ice' if hasattr(projectile, 'is_ice') and projectile.is_ice else 'fire'
                        # Debug: Projectile hit
                        # print(f"{projectile_type.capitalize()} projectile hit goblin for {damage} damage!")
                    
                    # Create appropriate explosion effect based on projectile type
                    if hasattr(projectile, 'is_ice') and projectile.is_ice:
                        explosion_effects.append(IceExplosionEffect(projectile.x, projectile.y))
                    else:
                        explosion_effects.append(ExplosionEffect(projectile.x, projectile.y))
                        
                    if projectile in projectiles:  # Check if not already removed
                        projectiles.remove(projectile)
                        
                    if goblin.health <= 0:
                        if DEBUG_MODE:
                            # Debug: Goblin defeated
                            # print("Goblin defeated!")
                            pass
                        self.goblins.remove(goblin)
                    break
                    
            # Remove projectile if it's no longer active or goes off screen
            if (not projectile.active or 
                projectile.x < 0 or 
                projectile.x > terrain.terrain_width or
                projectile.y > WINDOW_HEIGHT):
                if projectile in projectiles:  # Check if not already removed
                    projectiles.remove(projectile)
        
        # Update explosion effects
        for effect in explosion_effects[:]:
            effect.update()
            if not effect.active:
                explosion_effects.remove(effect)
        
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
        
        # Clear the screen with current sky color
        screen.fill(day_night_cycle.get_sky_color())
        
        # Draw day/night cycle (sun/moon)
        day_night_cycle.draw(screen)
        
        # Update and draw clouds (behind everything else)
        clouds.update()
        clouds.draw(screen, camera_x)
        
        # Draw terrain first (background)
        terrain.draw(screen, camera_x)
        
        # Draw all game objects in proper order
        # 1. Draw all projectiles first (behind characters)
        for projectile in projectiles:
            projectile.draw(screen, camera_x)
            
        # 1.5 Draw all explosion effects (at the same depth as projectiles)
        for effect in explosion_effects:
            effect.draw(screen, camera_x)
            
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
