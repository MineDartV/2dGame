import pygame
import os
from settings import DEBUG_MODE

def load_sprite(filename):
    try:
        img = pygame.image.load(os.path.join('assets', filename)).convert_alpha()
        return img
    except Exception as e:
        if DEBUG_MODE:
            print(f"Failed to load {filename}: {e}")
        return None