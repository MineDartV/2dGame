from PIL import Image, ImageOps
import os

# Sprite sheet location
SHEET_PATH = os.path.join(os.path.dirname(__file__), 'base_sheet_character.png')

# Output folder
OUT_PATH = os.path.dirname(__file__)

# Frame size (updated to match the sprite sheet grid)
FRAME_WIDTH, FRAME_HEIGHT = 48, 64  # Adjusted to fit the sprite sheet layout

# Animation frame positions (row, col) - updated to match the actual sprite sheet
ANIM_FRAMES = {
    'idle':      (0, 0),  # Top-left frame
    'walk1':     (0, 1),  # Next frame to the right
    'walk2':     (0, 2),  # And so on...
    'walk3':     (0, 3),
    'walk4':     (1, 0),  # Next row
    'jump':      (1, 1),  # Jump frame
}

# Classic Terraria palette (approx)
SKIN = (222, 188, 153)
SHIRT = (60, 120, 200)
PANTS = (120, 80, 40)
HAIR = (100, 60, 30)
OUTLINE = (40, 40, 60)

# Robust palette mapping: map all shades of gray
# These are approximate ranges for the mannequin sheet
SKIN_RANGE = [(140, 180)]  # Light gray
PANTS_RANGE = [(80, 130)]  # Darker gray
SHIRT_RANGE = [(180, 230)] # Lighter gray
OUTLINE_RANGE = [(60, 100)]

# Simple hair overlay (rectangle, for demo)
# Hair overlay removed for now to avoid blocky artifacts.
# def add_hair(img):
#     return img

from collections import deque

def flood_fill_transparency(img):
    px = img.load()
    w, h = img.size
    visited = set()
    q = deque()
    # Add all edge pixels
    for x in range(w):
        q.append((x, 0))
        q.append((x, h-1))
    for y in range(h):
        q.append((0, y))
        q.append((w-1, y))
    while q:
        x, y = q.popleft()
        if (x, y) in visited:
            continue
        visited.add((x, y))
        if 0 <= x < w and 0 <= y < h and px[x, y][:3] == (0, 0, 0):
            px[x, y] = (0, 0, 0, 0)
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < w and 0 <= ny < h:
                    q.append((nx, ny))
    return img

def colorize(img):
    px = img.load()
    width, height = img.size
    for y in range(height):
        for x in range(width):
            r, g, b, a = px[x, y]
            # Skip transparent pixels
            if a == 0:
                continue
            # Map grayscale to colors
            if 60 <= r <= 80:  # Pants (dark gray)
                px[x, y] = (120, 80, 40, 255)  # Brown pants
            elif 90 <= r <= 120:  # Shirt (medium gray)
                px[x, y] = (60, 120, 200, 255)  # Blue shirt
            elif 140 <= r <= 180:  # Skin (light gray)
                px[x, y] = (222, 188, 153, 255)  # Skin color
            elif r >= 200:  # Eyes/teeth (white)
                px[x, y] = (255, 255, 255, 255)
            else:  # Outline (black)
                px[x, y] = (0, 0, 0, 255)
    # Flood fill from edges to mark background black as transparent
    visited = set()
    q = deque()
    # Add all edge pixels
    for i in range(width):
        q.append((i, 0))
        q.append((i, height-1))
    for j in range(height):
        q.append((0, j))
        q.append((width-1, j))
    while q:
        x, y = q.popleft()
        if (x, y) in visited:
            continue
        visited.add((x, y))
        if 0 <= x < width and 0 <= y < height and px[x, y][:3] == (0, 0, 0):
            px[x, y] = (0, 0, 0, 0)
            # Add neighbors
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < width and 0 <= ny < height:
                    q.append((nx, ny))
    return img

sheet = Image.open(SHEET_PATH)

# Analyze the idle frame for unique RGB values
idle_row, idle_col = ANIM_FRAMES['idle']
x0, y0 = idle_col * FRAME_WIDTH, idle_row * FRAME_HEIGHT
idle_frame = sheet.crop((x0, y0, x0+FRAME_WIDTH, y0+FRAME_HEIGHT))
unique_colors = set()
for y in range(idle_frame.height):
    for x in range(idle_frame.width):
        unique_colors.add(idle_frame.getpixel((x, y))[:3])
print('Unique RGB values in idle frame:', unique_colors)

def extract_frame(sheet, row, col, name):
    # Calculate the exact position of the frame in the sheet
    x0 = col * FRAME_WIDTH
    y0 = row * FRAME_HEIGHT
    
    # Extract the frame
    frame = sheet.crop((x0, y0, x0 + FRAME_WIDTH, y0 + FRAME_HEIGHT)).convert('RGBA')
    
    # Create a new image with the exact size and transparent background
    new_frame = Image.new('RGBA', (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    
    # Colorize the frame
    colored_frame = colorize(frame)
    
    # Apply transparency
    transparent_frame = flood_fill_transparency(colored_frame)
    
    # Paste the processed frame onto the new transparent background
    new_frame.paste(transparent_frame, (0, 0), transparent_frame)
    
    # Save the right-facing frame
    right_filename = os.path.join(OUT_PATH, f'hero_{name}_right.png')
    new_frame.save(right_filename)
    
    # Create and save the left-facing frame (mirrored)
    left_frame = Image.new('RGBA', (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    mirrored = ImageOps.mirror(new_frame)
    left_frame.paste(mirrored, (0, 0), mirrored)
    
    left_filename = os.path.join(OUT_PATH, f'hero_{name}_left.png')
    left_frame.save(left_filename)
    
    # Verify the saved images
    try:
        img = Image.open(right_filename)
        if img.size != (FRAME_WIDTH, FRAME_HEIGHT):
            print(f"Warning: {right_filename} has incorrect dimensions: {img.size}")
    except Exception as e:
        print(f"Error verifying {right_filename}: {e}")
        
    try:
        img = Image.open(left_filename)
        if img.size != (FRAME_WIDTH, FRAME_HEIGHT):
            print(f"Warning: {left_filename} has incorrect dimensions: {img.size}")
    except Exception as e:
        print(f"Error verifying {left_filename}: {e}")

# Process all frames
for name, (row, col) in ANIM_FRAMES.items():
    extract_frame(sheet, row, col, name)

print('Extracted and robustly colored Terraria-style hero frames!')
