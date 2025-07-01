
import openai
import dotenv
import os
from pathlib import Path
from base64 import b64decode, b64encode 
from io import BytesIO
from PIL import Image, ImageFilter



dotenv.load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=API_KEY)

thisdir = Path(__file__).resolve().parent

def generate_assets():
    print("Generating assets...")
    style_prompt = "2d pixel art, game asset style"

    assets = {
        "fireball": {
            "description": "a fireball",
            "size": (32, 32),
        },
        "iceball": {
            "description": "an iceball",
            "size": (32, 32),
        },
        "goblin": {
            "description": "a goblin",
            "size": (32, 32),
        },
        "tree": {
            "description": "pine tree, tall",
            "size": (64, 64),
        },
        "grass": {
            "description": "grass, pixelated, little dirt underneath the bottom, full width going off screen, full length going off screen",
            "size": (32, 32),
        },
        "dirt": {
            "description": "dirt, pixelated and similar to dirt under grass texture",
            "size": (32, 32),
        },
        "stone": {
            "description": "stone",
            "size": (32, 32),
        },
        "wizard_staff": {
            "description": "wizard staff, small and simple, pixelated, dark wood, white tip, long handle",
            "size": (32, 32),
        },
    }

    for asset, details in assets.items():
        savedir = thisdir.joinpath("assets")
        savedir.mkdir(exist_ok=True, parents=True)

        description = details["description"]
        size = details["size"]

        print(f"Generating asset: {asset}")

        # Save the original image first
        savepath = savedir.joinpath(f"{asset}.png")
        prompt = f"{description} {style_prompt}"
        if savepath.exists():
            print(f"Asset {asset} already exists, skipping...")
            continue
        response = client.images.generate(
            model="gpt-image-1",
            background="transparent",
            n=1,
            size="1024x1024",
            # response_format="b64_json",
            prompt=prompt
        )

        image_bytes = b64decode(response.data[0].b64_json)
        savepath.write_bytes(image_bytes)
        
        # Load the image and ensure it has an alpha channel
        image = Image.open(BytesIO(image_bytes))
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Make black/dark background transparent
        datas = image.getdata()
        new_data = []
        for item in datas:
            # If pixel is black or very dark, make it transparent
            if item[0] < 25 and item[1] < 25 and item[2] < 25:
                new_data.append((0, 0, 0, 0))  # Transparent
            else:
                new_data.append(item)  # Keep original
        
        # Update image data
        image.putdata(new_data)
        
        # # Save with transparency
        # image.save(savepath, 'PNG', transparency=0)
        # print(f"Saved {asset}.png with transparent background")

        # Resize to 32x32 with high-quality downsampling
        resized_image = image.resize(size, Image.Resampling.LANCZOS)
        
        # Apply a slight sharpening to counteract blur from downscaling
        resized_image = resized_image.filter(ImageFilter.SHARPEN)
        
        # Save the resized image with transparency
        resized_image.save(savepath.with_stem(f"{asset}"))
        print(f"Saved resized {asset}.png with transparent background")


def main():
    generate_assets()

if __name__ == "__main__":
    main()