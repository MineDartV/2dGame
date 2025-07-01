from PIL import Image, ImageOps
import os

# Sprite sheet location
SHEET_PATH = os.path.join(os.path.dirname(__file__), 'base_sheet_character.png')

# Output folder
OUT_PATH = os.path.dirname(__file__)

# Frame size
FRAME_WIDTH, FRAME_HEIGHT = 48, 64

# Frame coordinates (col, row) for each frame in the sprite sheet grid
FRAMES = {
    'idle': (0, 0),
    'walk1': (1, 0),
    'walk2': (2, 0),
    'walk3': (3, 0),
    'walk4': (0, 1),
    'jump': (1, 1)
}

def colorize(img):
    """Apply color to the grayscale sprite."""
    px = img.load()
    width, height = img.size
    for y in range(height):
        for x in range(width):
            r, g, b, a = px[x, y]
            if a == 0:  # Skip transparent pixels
                continue
            # Map grayscale to colors
            if 60 <= r <= 80:    # Pants (dark gray)
                px[x, y] = (120, 80, 40, 255)     # Brown
            elif 90 <= r <= 120:  # Shirt (medium gray)
                px[x, y] = (60, 120, 200, 255)    # Blue
            elif 140 <= r <= 180: # Skin (light gray)
                px[x, y] = (222, 188, 153, 255)   # Skin tone
            elif r >= 200:        # Eyes/teeth (white)
                px[x, y] = (255, 255, 255, 255)   # White
            else:                 # Outline (black)
                px[x, y] = (0, 0, 0, 255)         # Black
    return img

def make_transparent(img):
    """Make black pixels transparent."""
    img = img.convert("RGBA")
    data = img.getdata()
    new_data = []
    for item in data:
        # Make black pixels transparent
        if item[0] < 50 and item[1] < 50 and item[2] < 50:
            new_data.append((0, 0, 0, 0))
        else:
            new_data.append(item)
    img.putdata(new_data)
    return img

def extract_frames():
    """Extract and process all frames from the sprite sheet."""
    try:
        sheet = Image.open(SHEET_PATH).convert('RGBA')
        print(f"Opened sprite sheet: {SHEET_PATH}")
        print(f"Sheet size: {sheet.size}")
        
        for name, (col, row) in FRAMES.items():
            # Calculate position
            x = col * FRAME_WIDTH
            y = row * FRAME_HEIGHT
            print(f"\nProcessing {name} at position ({x}, {y})")
            
            # Extract frame
            frame = sheet.crop((x, y, x + FRAME_WIDTH, y + FRAME_HEIGHT))
            print(f"  Extracted frame size: {frame.size}")
            
            # Process frame
            frame = colorize(frame)
            frame = make_transparent(frame)
            
            # Save right-facing frame
            right_frame = frame.copy()
            right_path = os.path.join(OUT_PATH, f'hero_{name}_right.png')
            right_frame.save(right_path)
            print(f"  Saved {right_path}")
            
            # Create and save left-facing frame
            left_frame = ImageOps.mirror(frame)
            left_path = os.path.join(OUT_PATH, f'hero_{name}_left.png')
            left_frame.save(left_path)
            print(f"  Saved {left_path}")
        
        print("\nSuccessfully extracted all frames!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting frame extraction...")
    extract_frames()
