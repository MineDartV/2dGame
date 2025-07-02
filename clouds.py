import pygame
import random
import math
from settings import WINDOW_WIDTH, WINDOW_HEIGHT
from utils import load_sprite

class Cloud:
    def __init__(self, x, y, scale=1.0):
        self.x = x
        self.y = y
        self.scale = scale
        self.speed = random.uniform(0.2, 0.5) * (0.5 + scale * 0.5)  # Bigger clouds move faster
        self.image = load_sprite('cloud.png')
        if self.image:
            # Scale the cloud image
            width = int(self.image.get_width() * scale)
            height = int(self.image.get_height() * scale)
            self.image = pygame.transform.scale(self.image, (width, height))
        self.width = self.image.get_width() if self.image else 100 * scale
        self.height = self.image.get_height() if self.image else 50 * scale
        
    def update(self):
        # Move cloud from right to left
        self.x -= self.speed
        
    def draw(self, screen, camera_x):
        if self.image:
            screen.blit(self.image, (self.x - camera_x * 0.2, self.y))  # Parallax effect
        else:
            # Fallback: Draw a simple cloud shape
            pygame.draw.ellipse(screen, (255, 255, 255, 200), 
                              (self.x - camera_x * 0.2, self.y, self.width, self.height))

class CloudManager:
    def __init__(self, num_clouds=12):
        self.clouds = []
        self.num_clouds = num_clouds
        self.cloud_img = load_sprite('cloud.png')
        self.generate_clouds()
    
    def generate_clouds(self):
        for _ in range(self.num_clouds):
            self.add_cloud()
    
    def add_cloud(self):
        # Random position in the sky (top 40% of screen)
        x = random.randint(0, WINDOW_WIDTH * 3)  # Start some clouds off-screen
        y = random.randint(0, int(WINDOW_HEIGHT * 0.4))
        # Increase base scale range and add more variety
        base_scale = random.uniform(0.8, 2.5)  # Larger base scale range
        # Add some larger clouds more frequently
        if random.random() > 0.7:  # 30% chance for extra large clouds
            base_scale *= 1.5
        self.clouds.append(Cloud(x, y, base_scale))
    
    def update(self, dt=1.0/60.0):
        # Update all clouds with delta time
        i = 0
        while i < len(self.clouds):
            cloud = self.clouds[i]
            cloud.update()
            
            # Remove clouds that are off-screen to the left
            if cloud.x + cloud.width * 1.5 < 0:  # Add 50% buffer before removing
                self.clouds.pop(i)
                # Add a new cloud at the right side
                self.add_cloud_at_edge()
            else:
                i += 1
        
        # Ensure we always have the desired number of clouds
        while len(self.clouds) < self.num_clouds:
            self.add_cloud_at_edge()
    
    def add_cloud_at_edge(self, x_offset=0):
        # Add a new cloud just outside the right edge of the screen
        x = WINDOW_WIDTH + random.randint(100, 300) + x_offset
        y = random.randint(0, int(WINDOW_HEIGHT * 0.4))
        # Match the larger scale from add_cloud
        base_scale = random.uniform(0.8, 2.5)
        if random.random() > 0.7:  # 30% chance for extra large clouds
            base_scale *= 1.5
        self.clouds.append(Cloud(x, y, base_scale))
        return x  # Return x position for potential chaining
    
    def draw(self, screen, camera_x):
        # Sort clouds by Y position for proper layering
        sorted_clouds = sorted(self.clouds, key=lambda c: c.y)
        for cloud in sorted_clouds:
            cloud.draw(screen, camera_x)
