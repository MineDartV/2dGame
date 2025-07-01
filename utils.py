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