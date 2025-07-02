import pygame
from settings import DEBUG_MODE
import pathlib

thisdir = pathlib.Path(__file__).parent.resolve()   

def load_sprite(filename):
    try:
        img = pygame.image.load(thisdir / 'assets' / filename).convert_alpha()
        return img
    except Exception as e:
        if DEBUG_MODE:
            raise e
            print(f"Failed to load {filename}: {e}")
        raise e

def load_spritesheet(filename, frame_width, frame_height, num_frames, rows=1, scale=1.0, row_offset=0):
    """
    Load a sprite sheet and split it into individual frames.
    
    Args:
        filename: Name of the sprite sheet file
        frame_width: Width of each frame in pixels
        frame_height: Height of each frame in pixels
        num_frames: Total number of frames to load
        rows: Number of rows to process (default: 1)
        scale: Scale factor for the sprites (default: 1.0)
        row_offset: Starting row in the sprite sheet (0-based, default: 0)
        
    Returns:
        List of pygame.Surface objects for each frame
    """
    try:
        # Load the sprite sheet
        sheet = pygame.image.load(thisdir / 'assets' / filename).convert_alpha()
        
        frames = []
        frames_per_row = num_frames // rows if rows > 0 else num_frames
        
        for row in range(rows):
            for col in range(frames_per_row):
                # Calculate the position of the current frame
                x = col * frame_width
                y = (row + row_offset) * frame_height
                
                # Create a surface for the frame
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                
                # Only blit if the coordinates are within the sprite sheet bounds
                if (x + frame_width <= sheet.get_width() and 
                    y + frame_height <= sheet.get_height()):
                    frame.blit(sheet, (0, 0), (x, y, frame_width, frame_height))
                
                # Scale if needed
                if scale != 1.0:
                    new_width = max(1, int(frame_width * scale))
                    new_height = max(1, int(frame_height * scale))
                    if new_width > 0 and new_height > 0:  # Ensure valid dimensions
                        frame = pygame.transform.scale(frame, (new_width, new_height))
                
                frames.append(frame)
                
        return frames
    except Exception as e:
        if DEBUG_MODE:
            print(f"Failed to load spritesheet {filename}: {e}")
        raise e