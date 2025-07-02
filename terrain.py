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
    pine_tree_img = load_sprite('pine_tree.png')
    bush_img = load_sprite('bush.png')
    flower_img = load_sprite('flower.png')
    yellow_flower_img = load_sprite('yellow_flower.png')
    return grass_img, dirt_img, stone_img, tree_img, pine_tree_img, bush_img, flower_img, yellow_flower_img


# Terrain class
class Terrain:
    def place_vegetation(self):
        """Place trees, bushes and flowers in the grass biome."""
        tile_size = 32
        min_tree_distance = 3 * tile_size  # Minimum distance between trees
        min_veg_distance = tile_size  # Minimum distance between vegetation
        
        # Place vegetation only in the grass biome (first 70% of the map)
        grass_biome_width = int(self.terrain_width * 0.7)
        
        for x in range(0, grass_biome_width, tile_size // 2):  # Check more points for better coverage
            # Skip if this is in the stone biome
            if self.get_biome_at(x) != 0:
                continue
                
            # Get the ground height at this position
            ground_height = self.get_ground_height(x)
            
            # Check if this is a suitable spot (not too steep)
            next_x = min(x + tile_size, self.terrain_width - 1)
            next_height = self.get_ground_height(next_x)
            slope = abs(ground_height - next_height) / tile_size
            
            # Only place vegetation on relatively flat ground
            if slope >= 0.5:
                continue
                
            # Check distance to other objects
            too_close_to_tree = any(abs(x - tree_x) < min_tree_distance for tree_x in self.trees)
            too_close_to_bush = any(abs(x - bush_x) < min_veg_distance for bush_x in self.bushes)
            too_close_to_flower = any(abs(x - flower_x) < min_veg_distance for flower_x in self.flowers)
            
            # 40% chance to place a tree if not too close to another tree (increased from 25%)
            if (not too_close_to_tree and random.random() < 0.40 and 
                x % (tile_size * 2) == 0):  # Only check every other tile for trees
                
                # Randomly choose between regular tree and pine tree (40% regular, 60% pine)
                is_pine = random.random() < 0.6
                
                if is_pine:
                    self.pine_trees.add(x)
                    # Pine trees - less tall and less stretched
                    scale = random.uniform(0.8, 1.2)  # Reduced scale range
                    height_factor = 0.9 + ((ground_height - (WINDOW_HEIGHT - 120)) / 200.0)  # Less height variation
                    tree_height = int(5 + (random.random() * 0.5 + 0.5) * 4)  # 5-9 tiles (shorter)
                else:
                    self.trees.add(x)
                    # Regular trees - larger and wider
                    scale = random.uniform(1.2, 1.8)  # Increased scale for larger trees
                    height_factor = 0.8 + ((ground_height - (WINDOW_HEIGHT - 120)) / 300.0)
                    tree_height = int(6 + (random.random() * 0.6 + 0.4) * 6)  # 6-12 tiles (taller)
                
                self.tree_data[x] = {
                    'height': max(4, min(15, tree_height)),  # Clamp height
                    'scale': scale * height_factor,
                    'type': 'pine' if is_pine else 'regular'  # Store tree type
                }
                
            # Check distance to other vegetation
            too_close_to_other_veg = (too_close_to_bush or too_close_to_flower or 
                                     x in self.bushes or x in self.flowers)
            
            # 30% chance to place a bush if not too close to other objects
            if (not too_close_to_other_veg and random.random() < 0.30 and 
                x % tile_size == 0):
                # Store y position and size for consistent rendering
                self.bushes[x] = {
                    'y': ground_height,  # Use ground_height instead of ground_y
                    'size': random.uniform(0.8, 1.2)
                }
            # 15% chance to start a flower patch (3-5 flowers)
            elif (not too_close_to_other_veg and random.random() < 0.15 and 
                  x % (tile_size * 4) == 0):  # Ensure patches are spread out
                # Create a patch of 3-5 flowers
                flower_count = random.randint(3, 5)
                for i in range(flower_count):
                    # Offset each flower slightly
                    offset_x = x + random.randint(-tile_size, tile_size)
                    # Ensure we're still in the grass biome
                    if (0 <= offset_x < grass_biome_width and 
                        self.get_biome_at(offset_x) < 0.2 and
                        offset_x not in self.flowers):
                        # Get ground height at the offset position and store all random values
                        offset_ground = self.get_ground_height(offset_x)
                        # Generate and store all random values at creation time
                        y_offset = random.randint(0, 2)  # Reduced vertical variation
                        size = random.uniform(0.6, 0.9)
                        variant = random.choice([0, 1, 2])
                        angle = random.uniform(-10, 10)  # Store rotation at creation time
                        
                        # Randomly choose between regular and yellow flower (70% regular, 30% yellow)
                        is_yellow = random.random() < 0.3
                        
                        # Position flowers slightly lower (add 5 pixels to y position)
                        self.flowers[offset_x] = {
                            'y': offset_ground + y_offset + 5,  # Lowered by 5 pixels
                            'size': size,
                            'variant': variant,
                            'angle': angle,  # Store the rotation angle
                            'type': 'yellow' if is_yellow else 'regular'  # Store flower type
                        }
    
    # Keep the old method name for compatibility but make it call the new method
    def place_trees(self):
        """Legacy method that now calls place_vegetation for backward compatibility"""
        self.place_vegetation()

    def __init__(self, grass_img, dirt_img, stone_img, tree_img, pine_tree_img, bush_img, flower_img, yellow_flower_img):
        self.grass_img = grass_img
        self.dirt_img = dirt_img
        self.stone_img = stone_img
        self.tree_img = tree_img
        self.pine_tree_img = pine_tree_img
        self.bush_img = bush_img
        self.flower_img = flower_img
        self.yellow_flower_img = yellow_flower_img
        self.tile_size = 32  # Size of each tile in pixels
        self.terrain_width = WINDOW_WIDTH * 20  # Increased from 6 to 20 screens wide
        self.points = []  # Points for the terrain surface
        self.trees = set()  # Set of x-positions where trees are placed
        self.pine_trees = set()  # Set of x-positions where pine trees are placed
        self.bushes = {}  # Dictionary of bushes with their positions and sizes
        self.flowers = {}  # Dictionary of flowers with their positions and sizes
        self.tree_data = {}  # Store additional tree data (height, scale, type)
        self.biome_points = []  # Store biome type at each x position
        self.base_height = WINDOW_HEIGHT - 100
        
        # Generate the initial terrain points
        self._generate_terrain()
        
        # Apply smoothing to the terrain
        self._smooth_terrain()
        
        # Place trees after initial terrain is generated
        self.place_trees()
        
        # Smooth around tree areas to create flatter ground
        self._flatten_around_trees()
        
        # Final smoothing pass
        self._smooth_terrain()
        
        # Ensure edges are closed
        self._close_terrain_edges()
    
    def _generate_terrain(self):
        """Generate the initial terrain with biomes and hills"""
        # Clear existing points and biome data
        self.points = []
        self.biome_blend = {}
        
        # Terrain generation parameters
        base_height = WINDOW_HEIGHT - 80  # Slightly higher base
        tile_size = 32
        
        # Generate points with noise and height variation
        for x in range(0, self.terrain_width, tile_size):
            # Calculate biome blend (0 = grass, 1 = stone)
            # Generate biome transitions (first 70% grass, then 15% transition, then 15% stone)
            biome_transition_start = int(self.terrain_width * 0.7)
            biome_transition_end = int(self.terrain_width * 0.85)
            
            if x < biome_transition_start:
                biome_blend = 0.0  # Full grass biome
            elif x > biome_transition_end:
                biome_blend = 1.0  # Full stone biome
            else:
                # Smooth transition between biomes
                t = (x - biome_transition_start) / (biome_transition_end - biome_transition_start)
                biome_blend = t * t * (3 - 2 * t)  # Smoothstep for smoother transition
            
            # Base height with multiple layers of noise for organic feel
            # Adjusted wave parameters for larger world
            large_wave = math.sin(x / 600) * 60  # Wider, more gradual hills
            medium_wave = math.sin(x / 200 + 10) * 35  # Medium features
            small_wave = math.sin(x / 70 + 20) * 15    # Fine details
            
            # Combine waves with different weights for natural look
            height_variation = large_wave * 0.4 + medium_wave * 0.4 + small_wave * 0.2
            
            # Adjust height based on biome (stone biome is higher and more varied)
            base_height_biome = base_height + (biome_blend * 60)  # Increased from 40 to 60
            
            # Add more dramatic height variation in stone biome
            if biome_blend > 0.2:  # Start transition earlier (was 0.3)
                # More dramatic and varied hills in stone biome
                stone_large = math.sin(x / 180 + 30) * 70 * biome_blend  # Wider, more gradual stone hills
                stone_medium = math.sin(x / 80 + 40) * 40 * (biome_blend ** 1.5)  # Medium stone features
                stone_small = math.sin(x / 30 + 50) * 15 * (biome_blend ** 2)  # Small details
                height_variation += stone_large * 0.5 + stone_medium * 0.35 + stone_small * 0.15
            
            # Final height calculation
            y = base_height_biome + height_variation
            
            # Add some random noise for natural look
            y += (random.random() - 0.5) * 8  # Slightly more variation for larger world
            
            # Clamp height to reasonable values
            y = max(100, min(WINDOW_HEIGHT - 40, y))
            
            # Store the point
            self.points.append((x, int(y)))
            
            # Store the biome blend for this x position
            self.biome_blend[x] = biome_blend
        
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
            
            # Get biome at this point to adjust smoothing
            biome = self.get_biome_at(x)
            
            # Average the y position with neighbors
            avg_y = (prev_y + y + next_y) / 3
            
            # Adjust smoothing intensity based on biome
            if isinstance(biome, float) and 0 < biome < 1:  # Transition area
                # Smoother transitions in the blend area
                max_change = 3
            elif biome == 1:  # Stone biome
                # Preserve more detail in stone biome
                max_change = 7
            else:  # Grass biome
                max_change = 5
            
            new_y = y + min(max(avg_y - y, -max_change), max_change)
            
            # Keep within reasonable bounds
            new_y = max(WINDOW_HEIGHT - 200, min(WINDOW_HEIGHT - 40, new_y))
            self.points[i] = (x, new_y)
    
    def _close_terrain_edges(self):
        """Ensure the terrain is closed at both edges"""
        if not self.points:
            return
            
        # Close left edge
        left_x, left_y = self.points[0]
        self.points.insert(0, (left_x - self.tile_size, left_y + 100))  # Slope down to the left
        self.points.insert(0, (left_x - self.tile_size * 2, left_y + 200))  # Further down
        self.biome_points.insert(0, (left_x - self.tile_size, 0))  # Keep as grass biome
        self.biome_points.insert(0, (left_x - self.tile_size * 2, 0))
        
        # Close right edge
        right_x, right_y = self.points[-1]
        self.points.append((right_x + self.tile_size, right_y + 100))  # Slope down to the right
        self.points.append((right_x + self.tile_size * 2, right_y + 200))  # Further down
        self.biome_points.append((right_x + self.tile_size, 1))  # Keep as stone biome
        self.biome_points.append((right_x + self.tile_size * 2, 1))
        
        # Update terrain width to account for the added points
        self.terrain_width = self.points[-1][0] - self.points[0][0]
    
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
    
    def get_biome_at(self, x):
        """Get the biome at a specific x coordinate"""
        if not self.biome_points:
            return 0  # Default to grass biome
            
        # Find the two closest points for interpolation
        left = None
        right = None
        
        for point_x, biome in self.biome_points:
            if point_x <= x:
                left = (point_x, biome)
            else:
                right = (point_x, biome)
                break
        
        # Handle edge cases
        if left is None:
            return right[1] if right is not None else 0
        if right is None:
            return left[1]
            
        # If we found both left and right points, interpolate between them
        if left[0] == right[0]:
            return left[1]
            
        # Linear interpolation between the two closest points
        t = (x - left[0]) / (right[0] - left[0])
        
        # If both biomes are the same type, return that type
        if isinstance(left[1], (int, float)) and isinstance(right[1], (int, float)):
            if left[1] == right[1]:
                return left[1]
            # If we're in a transition zone between biomes, return the blend value
            if 0 < left[1] < 1 or 0 < right[1] < 1:
                return left[1] * (1 - t) + right[1] * t
        
        # Default to the closer point's biome
        return left[1] if t < 0.5 else right[1]

    def draw(self, screen, camera_x):
        # Draw terrain as Terraria-style tiles (sprites)
        tile_size = self.tile_size
        
        # First draw all trees (behind everything)
        for x, y in self.points:
            # Only draw trees in grass biome (blend < 0.2)
            biome = self.get_biome_at(x)
            screen_x = x - camera_x
            
            # Skip if off-screen
            if screen_x < -200 or screen_x > WINDOW_WIDTH + 200:
                continue
                
            # Draw trees (behind everything else)
            # Draw regular trees
            if (x in self.trees and biome < 0.2 and self.tree_img):
                tree_data = self.tree_data.get(x, {'height': 7, 'scale': 1.0, 'type': 'regular'})
                base_height = tree_data.get('height', 7)  # Default to 7 tiles if not specified
                scale = tree_data.get('scale', 1.0)  # Scale factor for the tree
                
                # Calculate tree dimensions - regular trees are larger
                tree_height = int(base_height * tile_size * scale)
                # Wider minimum width for larger trees
                min_tree_width = int(tile_size * 1.5)  # Increased minimum width
                tree_width = max(min_tree_width, int(tree_height * 0.7))  # Wider aspect ratio
                
                # Position tree base at ground level
                tree_y = y - tree_height + tile_size - 5
                tree_x = screen_x - (tree_width // 2) + (tile_size // 2)  # Center the tree
                
                # Draw the tree with scaled size
                if tree_width > 0 and tree_height > 0:  # Ensure valid dimensions
                    scaled_tree = pygame.transform.scale(self.tree_img, (tree_width, tree_height))
                    screen.blit(scaled_tree, (tree_x, tree_y))
                    screen.blit(scaled_tree, (tree_x, tree_y))
            
            # Draw pine trees
            elif (x in self.pine_trees and biome < 0.2 and self.pine_tree_img):
                tree_data = self.tree_data.get(x, {'height': 10, 'scale': 1.0, 'type': 'pine'})
                base_height = tree_data.get('height', 10)  # Pine trees are taller
                scale = tree_data.get('scale', 1.0)
                
                # Calculate tree dimensions - pines are less stretched
                tree_height = int(base_height * tile_size * scale)
                # Keep a minimum width and cap the height/width ratio
                min_pine_width = int(tile_size * 1.0)  # Increased minimum width
                tree_width = max(min_pine_width, int(tree_height * 0.5))  # Wider aspect ratio
                
                # Position tree base at ground level, moved down slightly
                tree_y = y - tree_height + tile_size + 5  # Moved down 10px from -5 to +5
                tree_x = screen_x - (tree_width // 2) + (tile_size // 2)  # Center the tree
                
                # Draw the pine tree with scaled size
                if tree_width > 0 and tree_height > 0:  # Ensure valid dimensions
                    scaled_tree = pygame.transform.scale(self.pine_tree_img, (tree_width, tree_height))
                    screen.blit(scaled_tree, (tree_x, tree_y))
                
        # Draw bushes (on top of terrain but behind player)
        for x, bush_data in self.bushes.items():
            screen_x = x - camera_x
            if -100 < screen_x < WINDOW_WIDTH + 100:
                # Get ground height at this x position
                ground_y = self.get_ground_height(x)
                
                # Use pre-calculated size and y position, with net raise of 5 pixels
                # Slightly larger bushes with more variation
                bush_scale = bush_data.get('size', 1.0) * 1.8  # Slightly larger than before
                bush_size = int(tile_size * bush_scale)
                bush_y = ground_y - bush_size + (tile_size // 2) - 5  # Net raise of 5 pixels
                
                # Only draw if in grass biome and image is loaded
                if self.get_biome_at(x) < 0.2 and self.bush_img and bush_size > 0:
                    screen.blit(
                        pygame.transform.scale(self.bush_img, (bush_size, bush_size)),
                        (screen_x - (bush_size // 2) + (tile_size // 2), bush_y)
                    )
        
        # Draw flowers (on top of bushes but behind player)
        for x, flower_data in self.flowers.items():
            screen_x = x - camera_x
            if -100 < screen_x < WINDOW_WIDTH + 100:
                # Get ground height at this x position
                ground_y = self.get_ground_height(x)
                
                # Use pre-calculated size and y position, with net raise of 5 pixels
                # Further increase flower size and add variation
                flower_scale = flower_data.get('size', 0.7) * 2.0  # Double the base size
                flower_size = int(tile_size * flower_scale)
                # Lower flower position by reducing the vertical offset (changed from -5 to +5)
                flower_y = ground_y - flower_size + (tile_size // 3) + 5
                
                # Only draw if in grass biome and image is loaded
                if self.get_biome_at(x) < 0.2 and self.flower_img and flower_size > 0:
                    # Choose the appropriate flower image
                    if flower_data.get('type') == 'yellow':
                        flower_img = self.yellow_flower_img
                        # Yellow flowers are slightly smaller
                        flower_size = int(flower_size * 0.9)
                    else:
                        flower_img = self.flower_img
                        # Apply color variation to regular flowers
                        if 'variant' in flower_data and flower_data['variant'] == 1:
                            # Create a slightly different colored variant once
                            if 'tinted_img' not in flower_data:
                                flower_data['tinted_img'] = self.flower_img.copy()
                                # Tint the flower (adjust RGB values as needed)
                                flower_data['tinted_img'].fill((255, 200, 200, 255), special_flags=pygame.BLEND_RGB_MULT)
                            flower_img = flower_data['tinted_img']
                    
                    # Draw the flower with consistent rotation
                    if flower_size > 0:
                        # Use stored rotation angle
                        angle = flower_data.get('angle', 0)
                        # Create a rotated version of the flower
                        if 'rotated_flower' not in flower_data or 'last_size' not in flower_data or flower_data['last_size'] != flower_size:
                            scaled_flower = pygame.transform.scale(flower_img, (flower_size, flower_size))
                            flower_data['rotated_flower'] = pygame.transform.rotate(scaled_flower, angle)
                            flower_data['last_size'] = flower_size
                        
                        rotated_flower = flower_data['rotated_flower']
                        # Adjust position to account for rotation
                        draw_x = screen_x - (rotated_flower.get_width() // 2) + (tile_size // 2)
                        draw_y = flower_y - (rotated_flower.get_height() - flower_size) // 2
                        screen.blit(rotated_flower, (draw_x, draw_y))
        
        # Then draw the terrain blocks (on top of trees)
        for i, (x, y) in enumerate(self.points):
            biome = self.get_biome_at(x)
            screen_x = x - camera_x
            
            # Skip drawing if off-screen
            if screen_x < -tile_size or screen_x > WINDOW_WIDTH + tile_size:
                continue
            
            # Draw top layer with biome blending
            if biome < 0.1:  # Full grass biome
                # Draw grass with dirt underneath
                if self.grass_img:
                    screen.blit(pygame.transform.scale(self.grass_img, (tile_size, tile_size)), 
                              (screen_x, y))
                else:
                    pygame.draw.rect(screen, (34, 139, 34), (screen_x, y, tile_size, tile_size))
                
                # Dirt layer below grass
                if self.dirt_img:
                    for dy in range(tile_size, tile_size*3, tile_size):
                        screen.blit(pygame.transform.scale(self.dirt_img, (tile_size, tile_size)), 
                                  (screen_x, y + dy))
                else:
                    for dy in range(tile_size, tile_size*3, tile_size):
                        pygame.draw.rect(screen, (139, 69, 19), 
                                       (screen_x, y + dy, tile_size, tile_size))
            
            elif biome > 0.9:  # Full stone biome
                # Cobblestone top layer
                if self.stone_img:
                    screen.blit(pygame.transform.scale(self.stone_img, (tile_size, tile_size)), 
                              (screen_x, y))
                else:
                    pygame.draw.rect(screen, (128, 128, 128), 
                                   (screen_x, y, tile_size, tile_size))
            
            else:  # Transition area
                # Blend between grass and stone
                if self.grass_img and self.stone_img:
                    # Create a surface for blending
                    grass_surf = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                    stone_surf = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                    
                    # Scale and draw the grass and stone
                    grass_img = pygame.transform.scale(self.grass_img, (tile_size, tile_size))
                    stone_img = pygame.transform.scale(self.stone_img, (tile_size, tile_size))
                    
                    grass_surf.blit(grass_img, (0, 0))
                    stone_surf.blit(stone_img, (0, 0))
                    
                    # Apply alpha based on biome blend
                    grass_surf.set_alpha(int(255 * (1 - biome)))
                    stone_surf.set_alpha(int(255 * biome))
                    
                    # Draw both surfaces
                    screen.blit(grass_surf, (screen_x, y))
                    screen.blit(stone_surf, (screen_x, y))
                    
                    # Draw dirt layer with transition
                    if self.dirt_img and self.stone_img:
                        for dy in range(tile_size, tile_size*3, tile_size):
                            dirt_surf = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                            dirt_img = pygame.transform.scale(self.dirt_img, (tile_size, tile_size))
                            stone_img = pygame.transform.scale(self.stone_img, (tile_size, tile_size))
                            
                            dirt_surf.blit(dirt_img, (0, 0))
                            stone_surf = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                            stone_surf.blit(stone_img, (0, 0))
                            
                            dirt_surf.set_alpha(int(255 * (1 - biome)))
                            stone_surf.set_alpha(int(255 * biome * 0.7))  # Slight transparency for stone in transition
                            
                            screen.blit(dirt_surf, (screen_x, y + dy))
                            screen.blit(stone_surf, (screen_x, y + dy))
                else:
                    # Fallback to color blending
                    grass_color = (34, 139, 34)
                    stone_color = (128, 128, 128)
                    blend_color = (
                        int(grass_color[0] * (1 - biome) + stone_color[0] * biome),
                        int(grass_color[1] * (1 - biome) + stone_color[1] * biome),
                        int(grass_color[2] * (1 - biome) + stone_color[2] * biome)
                    )
                    pygame.draw.rect(screen, blend_color, 
                                   (screen_x, y, tile_size, tile_size))
            
            # Draw stone layer below everything
            if self.stone_img:
                # Start stone layer higher in stone biome
                start_dy = tile_size if biome > 0.5 else tile_size*3
                for dy in range(start_dy, tile_size*5, tile_size):
                    screen.blit(pygame.transform.scale(self.stone_img, (tile_size, tile_size)), 
                              (screen_x, y + dy))
            else:
                # Fallback to colored rectangles
                start_dy = tile_size if biome > 0.5 else tile_size*3
                for dy in range(start_dy, tile_size*5, tile_size):
                    pygame.draw.rect(screen, (100, 100, 100), 
                                   (screen_x, y + dy, tile_size, tile_size))
        
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

