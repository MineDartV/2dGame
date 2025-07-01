import pygame
import random
import math
import pygame
import math

from settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS,
    GOBLIN_WIDTH, GOBLIN_HEIGHT,
    SKY_BLUE, PROJECTILE_SPEED
)
from generate_assets import generate_assets
from utils import load_sprite
from character_hero import Hero
from character_goblin import Goblin
from terrain import Terrain
from projectile import Projectile

# Generate assets if they don't exist
generate_assets()

# Game window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Hero vs Goblin")

clock = pygame.time.Clock()


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
                    
                    # Use hero's shoot_projectile method which checks for staff
                    projectile = hero.shoot_projectile(vx, vy)
                    if projectile:  # Only add if hero is holding staff and cooldown allows
                        projectiles.append(projectile)
                    
                except Exception as e:
                    # print(f"Error shooting projectile: {e}")
                    pass
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    hero.holding_staff = not hero.holding_staff  # Toggle staff visibility
                    print("Holding staff")

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
