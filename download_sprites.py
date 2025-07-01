import os
import requests
from PIL import Image

# Create sprites directory
if not os.path.exists('sprites'):
    os.makedirs('sprites')

# Download and process sprites
def download_and_process_sprite(url, filename, size=(32, 48)):
    try:
        # Download the image
        response = requests.get(url)
        response.raise_for_status()
        
        # Save the image
        with open(f'sprites/{filename}', 'wb') as f:
            f.write(response.content)
        
        # Open and resize the image
        img = Image.open(f'sprites/{filename}')
        img = img.resize(size, Image.Resampling.LANCZOS)
        img.save(f'sprites/{filename}')
        
        print(f"Successfully downloaded and processed {filename}")
        return True
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        return False

# URLs for the sprites
HERO_URL = "https://opengameart.org/sites/default/files/the_knight_free_sprite.png"
GOBLIN_URL = "https://opengameart.org/sites/default/files/goblin-sprite.png"

download_and_process_sprite(HERO_URL, 'hero.png')
download_and_process_sprite(GOBLIN_URL, 'goblin.png')
