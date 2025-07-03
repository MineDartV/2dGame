
# Constants
import os
import sys
from pathlib import Path

# Initialize pygame for font loading
try:
    import pygame
except ImportError:
    print("Warning: pygame not found. Font loading will be limited.")

# Get the root directory of the project
ROOT_DIR = Path(__file__).parent.resolve()
ASSETS_DIR = ROOT_DIR / 'assets'

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

# Default font settings - will be updated after pygame is initialized
FONT_NAME = None

def init_fonts():
    """Initialize font settings after pygame is available"""
    global FONT_NAME
    try:
        # Try to load a built-in font first
        FONT_NAME = pygame.font.get_default_font()
        if not FONT_NAME:
            # Fall back to a common system font
            FONT_NAME = 'Arial'
        # Initialize a font to verify it works
        pygame.font.SysFont(FONT_NAME, 16)
    except Exception as e:
        print(f"Warning: Could not load font: {e}")
        try:
            # Try a different approach to get a system font
            FONT_NAME = pygame.font.match_font('arial')
            if not FONT_NAME:
                FONT_NAME = None
        except:
            FONT_NAME = None
    
    if not FONT_NAME:
        print("Warning: Could not load any fonts, text rendering will fail")
    else:
        print(f"Using font: {FONT_NAME}")

# Ensure assets directory exists
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')
FONTS_DIR = os.path.join(ASSETS_DIR, 'fonts')
os.makedirs(FONTS_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

# Projectile image paths
PROJECTILE_IMG_PATH = os.path.join(ASSETS_DIR, 'fireball.png')
ICEBALL_IMG_PATH = os.path.join(ASSETS_DIR, 'iceball.png')


