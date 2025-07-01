
# Constants
import os


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
BLACK = (0, 0, 0)  # Added from the second set
PROJECTILE_COLOR = BLACK  # Black color for projectiles

# Projectile settings
PROJECTILE_SIZE = 20  # Size of the projectile box
PROJECTILE_SPEED = 8  # Reduced speed from 15 to 8
PROJECTILE_COOLDOWN = 15  # Cooldown between shots

# Colors
# Removed duplicate color constants. Consolidated into the first set.

# Debug mode
DEBUG_MODE = True


# Ensure assets directory exists
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')
os.makedirs(ASSETS_DIR, exist_ok=True)

# Projectile image path
PROJECTILE_IMG_PATH = os.path.join(ASSETS_DIR, 'fireball.png')


