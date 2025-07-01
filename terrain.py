import pygame
import math
import random
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, DEBUG_MODE
from utils import load_sprite


def load_terrain_assets():
    grass_img = load_sprite('grass.png')
    dirt_img = load_sprite('dirt.png')
    stone_img = load_sprite('stone.png')
    tree_img = load_sprite('tree.png')
    return grass_img, dirt_img, stone_img, tree_img


# Terrain class
class Terrain:
    def place_trees(self):
        """Place trees on the terrain, including on hills."""
        tile_size = 32
        min_distance = 2 * tile_size  # Minimum distance between trees
        
        # Place trees across the entire map width
        for x in range(0, self.terrain_width, tile_size):
            # Get the ground height at this position
            ground_height = self.get_ground_height(x)
            
            # Check if this is a suitable spot (not too steep)
            # Get slope by checking height difference with next point
            next_x = min(x + tile_size, self.terrain_width - 1)
            next_height = self.get_ground_height(next_x)
            slope = abs(ground_height - next_height) / tile_size
            
            # Allow trees on moderate slopes (less than 0.5 height change per tile)
            if slope < 0.5:
                # Check if we're not too close to another tree
                too_close = False
                for tree_x in self.trees:
                    if abs(x - tree_x) < min_distance:
                        too_close = True
                        break
                
                # 30% chance to place a tree if not too close to another
                if not too_close and random.random() < 0.3:
                    self.trees.add(x)
                    # Make taller trees on higher ground
                    height_factor = 1.0 - ((ground_height - (WINDOW_HEIGHT - 120)) / 80.0)  # Normalize height
                    tree_height = 3 + int(4 * max(0, min(1, height_factor)))  # 3-7 tiles tall
                    self.tree_data[x] = tree_height

    def __init__(self, grass_img=None, dirt_img=None, stone_img=None, tree_img=None):
        self.grass_img = grass_img
        self.dirt_img = dirt_img
        self.stone_img = stone_img
        self.tree_img = tree_img
        # Start with a much wider initial terrain
        tile_size = 32
        self.terrain_width = WINDOW_WIDTH * 4
        self.points = []
        self.trees = set()
        self.tree_data = {}  # x -> height (in tiles)
        
        # Base height for the terrain
        base_height = WINDOW_HEIGHT - 60
        
        # Create initial terrain points with smooth variation
        for x in range(0, self.terrain_width, tile_size):
            # Add some smooth variation to the height
            noise = math.sin(x / 200) * 20  # Smooth wave pattern
            y = base_height + noise
            self.points.append((x, y))
        
        # Apply smoothing to the terrain
        self._smooth_terrain()
        
        # Now place trees after initial terrain is generated
        self.place_trees()
        
        # Smooth around tree areas to create flatter ground
        self._flatten_around_trees()
        
        # Final smoothing pass
        self._smooth_terrain()
    
    def _smooth_terrain(self):
        """Apply smoothing to the terrain points"""
        if len(self.points) < 3:
            return
            
        # Create a copy of points for reference
        old_points = self.points.copy()
        
        # Smooth each point based on its neighbors
        for i in range(1, len(self.points) - 1):
            x, y = old_points[i]
            prev_x, prev_y = old_points[i-1]
            next_x, next_y = old_points[i+1]
            
            # Average the y position with neighbors
            avg_y = (prev_y + y + next_y) / 3
            
            # Limit the maximum change to prevent steep cliffs
            max_change = 5
            new_y = y + min(max(avg_y - y, -max_change), max_change)
            
            # Keep within bounds
            new_y = max(WINDOW_HEIGHT - 120, min(WINDOW_HEIGHT - 40, new_y))
            self.points[i] = (x, new_y)
    
    def _flatten_around_trees(self):
        """Flatten the terrain around tree positions"""
        if not self.trees:
            return
            
        # For each tree, flatten the area around it
        for tree_x in self.trees:
            # Find the index of the point at or before the tree
            idx = 0
            for i, (x, y) in enumerate(self.points):
                if x > tree_x:
                    idx = max(0, i-1)
                    break
            
            # Flatten an area around the tree (3 points on each side)
            start_idx = max(0, idx - 3)
            end_idx = min(len(self.points) - 1, idx + 3)
            
            if start_idx >= end_idx:
                continue
                
            # Get the average height of this area
            total_y = sum(self.points[i][1] for i in range(start_idx, end_idx + 1))
            avg_y = total_y / (end_idx - start_idx + 1)
            
            # Smooth the area
            for i in range(start_idx, end_idx + 1):
                x, _ = self.points[i]
                # Gradually blend to the average height
                blend = 0.7  # How much to blend towards the average (0-1)
                new_y = self.points[i][1] * (1 - blend) + avg_y * blend
                self.points[i] = (x, new_y)
    
    def extend_terrain_left(self):
        # Extend terrain to the left
        if self.points and self.points[0][0] > 0:
            # Get last point on left
            last_x = self.points[0][0]
            last_y = self.points[0][1]
            
            # Add new points to the left
            tile_size = 32
            for i in range(50):
                new_x = last_x - tile_size
                new_y = last_y + random.randint(-20, 20)
                new_y = max(WINDOW_HEIGHT - 100, min(WINDOW_HEIGHT - 50, new_y))
                self.points.insert(0, (new_x, new_y))
                if random.random() < 0.5:
                    self.trees.add(new_x)
                    if new_x not in self.tree_data:
                        self.tree_data[new_x] = random.randint(3, 5)
                last_x = new_x
            
            # Update terrain width
            self.terrain_width += 500
            
            # Debug: Print extension info
            if DEBUG_MODE:
                # print(f"Extended terrain left to {self.terrain_width} width")
                pass
            
            # Update all points to ensure proper spacing
            for i in range(len(self.points)):
                x, y = self.points[i]
                self.points[i] = (x, y)  # This forces recalculation of points
    
    def extend_terrain_right(self):
        # Extend terrain to the right
        if self.points:
            # Get last point on right
            last_x = self.points[-1][0]
            last_y = self.points[-1][1]
            
            # Add new points to the right
            tile_size = 32
            for i in range(50):
                new_x = last_x + tile_size
                new_y = last_y + random.randint(-20, 20)
                new_y = max(WINDOW_HEIGHT - 100, min(WINDOW_HEIGHT - 50, new_y))
                self.points.append((new_x, new_y))
                self.trees.add(new_x)  # Tree every tile
                last_x = new_x
            
            # Update terrain width
            self.terrain_width += 500
            
            # Debug: Print extension info
            if DEBUG_MODE:
                # print(f"Extended terrain right to {self.terrain_width} width")
                pass
            
            # Update all points to ensure proper spacing
            for i in range(len(self.points)):
                x, y = self.points[i]
                self.points[i] = (x, y)  # This forces recalculation of points
    
    def get_ground_height(self, x):
        # Handle edge cases
        if not self.points:
            return WINDOW_HEIGHT - 50  # Default height if no points
            
        # Clamp x to valid range
        x = max(0, min(x, self.points[-1][0]))
        
        # Find the first point with x > target
        for i in range(1, len(self.points)):
            x1, y1 = self.points[i-1]
            x2, y2 = self.points[i]
            
            if x1 <= x <= x2:
                # Linear interpolation between the two points
                if x1 == x2:
                    return y1
                t = (x - x1) / (x2 - x1)
                # Use cubic interpolation for smoother transitions
                if i > 1 and i < len(self.points) - 1:
                    x0, y0 = self.points[i-2]
                    x3, y3 = self.points[i+1]
                    # Catmull-Rom spline for smoother curves
                    t2 = t * t
                    t3 = t2 * t
                    return 0.5 * ((2 * y1) + 
                                (-y0 + y2) * t + 
                                (2*y0 - 5*y1 + 4*y2 - y3) * t2 + 
                                (-y0 + 3*y1 - 3*y2 + y3) * t3)
                # Fall back to linear interpolation
                return y1 * (1 - t) + y2 * t
                
        # If we get here, return the y of the last point
        return self.points[-1][1]
    
    def draw(self, screen, camera_x):
        # Draw terrain as Terraria-style tiles (sprites)
        tile_size = 32
        
        # First draw all trees (behind everything)
        for x, y in self.points:
            if x in self.trees and self.tree_img and -200 < (x - camera_x) < WINDOW_WIDTH + 200:
                # Position tree so the base is at ground level
                tree_y = y - 256 + tile_size - 5
                tree_x = x - camera_x - 100  # Center the tree on the block
                
                # Draw the tree (behind everything)
                screen.blit(pygame.transform.scale(self.tree_img, (200, 256)), 
                          (tree_x, tree_y))
        
        # Then draw the terrain blocks (on top of trees)
        for i, (x, y) in enumerate(self.points):
            # Draw grass tile at the top
            if self.grass_img:
                screen.blit(pygame.transform.scale(self.grass_img, (tile_size, tile_size)), (x - camera_x, y))
            else:
                pygame.draw.rect(screen, (34, 139, 34), (x - camera_x, y, tile_size, tile_size))
            # Draw dirt tiles below grass
            if self.dirt_img:
                for dy in range(tile_size, tile_size*3, tile_size):
                    screen.blit(pygame.transform.scale(self.dirt_img, (tile_size, tile_size)), (x - camera_x, y + dy))
            else:
                for dy in range(tile_size, tile_size*3, tile_size):
                    pygame.draw.rect(screen, (139, 69, 19), (x - camera_x, y + dy, tile_size, tile_size))
            # Draw stone tiles even deeper
            if self.stone_img:
                for dy in range(tile_size*3, tile_size*5, tile_size):
                    screen.blit(pygame.transform.scale(self.stone_img, (tile_size, tile_size)), (x - camera_x, y + dy))
            else:
                for dy in range(tile_size*3, tile_size*5, tile_size):
                    pygame.draw.rect(screen, (128, 128, 128), (x - camera_x, y + dy, tile_size, tile_size))
        
        # Fallback for missing tree images (drawn after terrain)
        for x, y in self.points:
            if x in self.trees and (self.tree_img is None):
                # Fallback if tree image fails to load
                tree_height = self.tree_data.get(x, 4)
                for h in range(tree_height):
                    pygame.draw.rect(screen, (0, 100, 0), 
                                   (x - camera_x, y - tile_size * (h + 1), tile_size, tile_size))

    def get_visible_terrain(self, camera_x):
        # Get the ground heights for visible terrain
        visible_heights = []
        for x in range(0, self.terrain_width, 32):
            if x + camera_x < WINDOW_WIDTH and x + camera_x > 0:
                visible_heights.append(self.get_ground_height(x))
        return visible_heights

