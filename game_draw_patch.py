import pygame
from game import Hero

# Patch for Hero.draw to use left/right facing sprite

def hero_draw_patch(self, screen, camera_x):
    sprite = self.sprite_right if self.facing_right else self.sprite_left
    if sprite:
        screen.blit(pygame.transform.scale(sprite, (self.width, self.height)), (self.x - camera_x, self.y))
    else:
        pygame.draw.rect(screen, self.color, (self.x - camera_x, self.y, self.width, self.height))

Hero.draw = hero_draw_patch
