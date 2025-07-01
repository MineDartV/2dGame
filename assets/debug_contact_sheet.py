import os
from PIL import Image
from PIL import ImageDraw

def create_contact_sheet():
    # Frame order for the contact sheet (right-facing frames only)
    frame_names = [
        'idle_right',
        'walk1_right',
        'walk2_right',
        'walk3_right',
        'walk4_right',
        'jump_right'
    ]
    
    # Load all frames
    frames = []
    for name in frame_names:
        try:
            img = Image.open(f'hero_{name}.png')
            frames.append(img)
            print(f"Loaded hero_{name}.png with size {img.size}")
        except Exception as e:
            print(f"Error loading hero_{name}.png: {e}")
    
    if not frames:
        print("No frames loaded!")
        return
    
    # Calculate contact sheet dimensions
    cols = min(3, len(frames))  # Maximum 3 columns
    rows = (len(frames) + cols - 1) // cols
    frame_width, frame_height = frames[0].size
    padding = 10
    
    # Create contact sheet with dark gray background
    contact_width = cols * (frame_width + padding) + padding
    contact_height = rows * (frame_height + padding) + padding
    contact_sheet = Image.new('RGBA', (contact_width, contact_height), (40, 40, 40, 255))
    
    # Draw grid
    draw = ImageDraw.Draw(contact_sheet)
    
    # Paste frames onto contact sheet with labels
    for i, (frame, name) in enumerate(zip(frames, frame_names)):
        row = i // cols
        col = i % cols
        x = col * (frame_width + padding) + padding
        y = row * (frame_height + padding) + padding
        
        # Paste frame
        contact_sheet.paste(frame, (x, y), frame)
        
        # Add frame name label
        label = name.replace('_right', '')
        text_x = x + (frame_width - len(label) * 6) // 2  # Approximate text centering
        text_y = y + frame_height + 2
        draw.text((text_x, text_y), label, fill=(255, 255, 255))
    
    # Save contact sheet
    output_path = 'contact_sheet.png'
    contact_sheet.save(output_path)
    print(f"Saved {output_path}")
    print(f"Contact sheet size: {contact_width}x{contact_height}")
    print(f"Frames: {len(frames)} ({cols}x{rows} grid)")

if __name__ == "__main__":
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print("Creating contact sheet...")
    create_contact_sheet()
