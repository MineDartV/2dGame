from PIL import Image
import os

# Path to the downloaded sprite sheet
SHEET_PATH = os.path.join(os.path.dirname(__file__), 'base_sheet_character.png')

# Output paths
RIGHT_PATH = os.path.join(os.path.dirname(__file__), 'hero_right.png')
LEFT_PATH = os.path.join(os.path.dirname(__file__), 'hero_left.png')

# --- CONFIGURE THESE BASED ON THE SHEET LAYOUT ---
# These are typical for Terraria-style sheets, but adjust if needed:
FRAME_WIDTH = 20  # width of one character frame (pixels)
FRAME_HEIGHT = 40 # height of one character frame (pixels)
RIGHT_FRAME_X = 0 # x offset of the right-facing standing frame (column index * FRAME_WIDTH)
RIGHT_FRAME_Y = 0 # y offset of the standing frame (row index * FRAME_HEIGHT)

# Load the sheet
sheet = Image.open(SHEET_PATH)

# Extract right-facing standing frame
right_frame = sheet.crop((RIGHT_FRAME_X, RIGHT_FRAME_Y, RIGHT_FRAME_X+FRAME_WIDTH, RIGHT_FRAME_Y+FRAME_HEIGHT))
right_frame.save(RIGHT_PATH)

# Extract left-facing standing frame
# If the sheet has a true left-facing frame, adjust LEFT_FRAME_X and LEFT_FRAME_Y accordingly.
# Otherwise, flip the right-facing frame horizontally.
left_frame = right_frame.transpose(Image.FLIP_LEFT_RIGHT)
left_frame.save(LEFT_PATH)

print(f"Extracted hero_right.png and hero_left.png from {SHEET_PATH}")
