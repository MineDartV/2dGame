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
        self.terrain_width = WINDOW_WIDTH * 20  # 20 screens wide
        self.points = []  # Points for the terrain surface
        self.trees = set()  # Set of x-positions where trees are placed
        self.pine_trees = set()  # Set of x-positions where pine trees are placed
        self.bushes = {}  # Dictionary of bushes with their positions and sizes
        self.flowers = {}  # Dictionary of flowers with their positions and sizes
        self.tree_data = {}  # Store additional tree data (height, scale, type)
        self.biome_points = []  # Store biome type at each x position
        self.base_height = WINDOW_HEIGHT - 100
        
        # Cave properties
        self.cave_entrance = None
        self.cave_exit = None
        self.cave_ceiling = []
        self.cave_floor = []
        
        # Generate the initial terrain points
        self._generate_terrain()
        
        # Apply smoothing to the terrain
        self._smooth_terrain()
        
        # Place trees after initial terrain is generated
        self.place_vegetation()
        
        # Smooth around tree areas to create flatter ground
        self._flatten_around_trees()
        
        # Final smoothing pass
        self._smooth_terrain()
        
        # Ensure edges are closed
        self._close_terrain_edges()
    def place_trees(self):
        """Legacy method that now calls place_vegetation for backward compatibility"""
        self.place_vegetation()
        
    def place_vegetation(self):
        """Place trees, bushes and flowers in the grass biome."""
        tile_size = self.tile_size
        min_tree_distance = 4 * tile_size  # Increased minimum distance between trees
        min_veg_distance = tile_size * 1.5  # Slightly more space between vegetation
        
        # Place vegetation only in the grass biome (first 70% of the map)
        grass_biome_width = int(self.terrain_width * 0.7)
        
        # Calculate potential tree positions first
        potential_tree_positions = []
        for x in range(0, grass_biome_width, tile_size * 2):  # Check fewer points for trees
            if self.get_biome_at(x) != 0:
                continue
                
            ground_height = self.get_ground_height(x)
            next_x = min(x + tile_size, self.terrain_width - 1)
            next_height = self.get_ground_height(next_x)
            slope = abs(ground_height - next_height) / tile_size
            
            # Only consider relatively flat ground for trees
            if slope < 0.4:  # More strict slope requirement for trees
                potential_tree_positions.append(x)
        
        # Shuffle to get random distribution
        random.shuffle(potential_tree_positions)
        
        # Place trees first (they take priority)
        for x in potential_tree_positions:
            ground_height = self.get_ground_height(x)
            
            # Check distance to other trees
            too_close = any(abs(x - tree_x) < min_tree_distance for tree_x in self.trees)
            too_close = too_close or any(abs(x - pine_x) < min_tree_distance for pine_x in self.pine_trees)
            
            if not too_close and random.random() < 0.6:  # 60% chance to place a tree at a good spot
                # Randomly choose between regular tree and pine tree (40% regular, 60% pine)
                is_pine = random.random() < 0.6
                
                if is_pine:
                    self.pine_trees.add(x)
                    # Store additional tree data
                    self.tree_data[x] = {
                        'height': random.randint(10, 14),  # Taller pines
                        'scale': random.uniform(0.8, 1.2),  # Random scale variation
                        'type': 'pine'
                    }
                else:
                    self.trees.add(x)
                    # Store additional tree data
                    self.tree_data[x] = {
                        'height': random.randint(7, 10),  # Shorter regular trees
                        'scale': random.uniform(0.9, 1.3),  # Random scale variation
                        'type': 'regular'
                    }
        
        # Place bushes and flowers (only in grass biome)
        for x in range(0, grass_biome_width, tile_size):
            if self.get_biome_at(x) != 0:
                continue
                
            ground_height = self.get_ground_height(x)
            
            # Skip if too close to trees
            too_close_to_tree = any(abs(x - tree_x) < min_veg_distance * 2 for tree_x in self.trees)
            too_close_to_pine = any(abs(x - pine_x) < min_veg_distance * 2 for pine_x in self.pine_trees)
            too_close_to_veg = too_close_to_tree or too_close_to_pine
            
            # Skip if this spot is already occupied
            if x in self.bushes or x in self.flowers or too_close_to_veg:
                continue
                
            # 10% chance for a bush
            if random.random() < 0.1:
                self.bushes[x] = {
                    'y': ground_height - tile_size,  # Position above ground
                    'scale': random.uniform(0.8, 1.2)  # Random scale
                }
            # 15% chance for a flower (but not if we placed a bush)
            elif random.random() < 0.15:
                self.flowers[x] = {
                    'y': ground_height - tile_size,  # Position above ground
                    'type': random.choice(['regular', 'yellow']),  # Random flower type
                    'scale': random.uniform(0.8, 1.2)  # Random scale
                }
                
                if is_pine:
                    self.pine_trees.add(x)
                    # Pine trees - less tall and less stretched
                    scale = random.uniform(0.8, 1.2)
                    height_factor = 0.9 + ((ground_height - (WINDOW_HEIGHT - 120)) / 200.0)
                    tree_height = int(5 + (random.random() * 0.5 + 0.5) * 4)  # 5-9 tiles
                else:
                    self.trees.add(x)
                    # Regular trees - larger and wider
                    scale = random.uniform(1.2, 1.8)
                    height_factor = 0.8 + ((ground_height - (WINDOW_HEIGHT - 120)) / 300.0)
                    tree_height = int(6 + (random.random() * 0.6 + 0.4) * 6)  # 6-12 tiles
                
                    # Store tree data with clamped values
                    self.tree_data[x] = {
                        'height': max(4, min(15, tree_height)),
                        'scale': scale * height_factor,
                        'type': 'pine' if is_pine else 'regular'
                    }
                    
            # Check if position is already occupied
            too_close_to_other_veg = (x in self.bushes or x in self.flowers)
            
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
    
    def _generate_cave(self, start_x, width, height):
        """
        Generate a cave in the terrain
        
        Args:
            start_x: X position to start the cave
            width: Width of the cave in pixels
            height: Height of the cave in pixels
        """
        if not hasattr(self, 'cave_entrance'):
            self.cave_entrance = None
        if not hasattr(self, 'cave_exit'):
            self.cave_exit = None
            
        # Store cave bounds
        self.cave_entrance = start_x
        self.cave_exit = start_x + width
        
        # Initialize cave ceiling and floor if they don't exist
        if not hasattr(self, 'cave_ceiling'):
            self.cave_ceiling = []
        if not hasattr(self, 'cave_floor'):
            self.cave_floor = []
        else:
            # Clear any existing cave data
            self.cave_ceiling.clear()
            self.cave_floor.clear()
        
        # Get ground height at entrance
        ground_height = self.get_ground_height(start_x)
        
        # Create cave ceiling (smooth curve with some noise)
        for x in range(start_x, start_x + width, 10):
            # Create a smooth curve for the ceiling with some noise
            t = (x - start_x) / width
            # Parabolic curve for ceiling with noise
            noise = (random.random() - 0.5) * 15  # Small noise for natural look
            ceiling_y = ground_height - height - 50 * math.sin(math.pi * t) + noise
            self.cave_ceiling.append((x, int(ceiling_y)))
        
        # Create cave floor (smooth curve with some noise)
        for x in range(start_x, start_x + width, 10):
            t = (x - start_x) / width
            # Add some noise to make it look more natural
            noise = (random.random() - 0.5) * 20  # Slightly more noise on floor
            # Parabolic curve for floor with noise
            floor_y = ground_height - 50 * math.sin(math.pi * t) + noise
            self.cave_floor.append((x, int(floor_y)))
            
        # Ensure the cave entrance and exit connect smoothly with the terrain
        if self.cave_ceiling and self.cave_floor:
            # Smooth transition at entrance
            entrance_floor_y = self.cave_floor[0][1]
            entrance_ceiling_y = self.cave_ceiling[0][1]
            
            # Smooth transition at exit
            exit_floor_y = self.cave_floor[-1][1]
            exit_ceiling_y = self.cave_ceiling[-1][1]
            
            # Add points to close the cave at entrance and exit
            self.cave_floor.insert(0, (start_x - 10, entrance_floor_y))
            self.cave_ceiling.insert(0, (start_x - 10, entrance_ceiling_y))
            
            self.cave_floor.append((start_x + width + 10, exit_floor_y))
            self.cave_ceiling.append((start_x + width + 10, exit_ceiling_y))
        
        # Mark the cave area in the terrain
        cave_start_idx = start_x // self.tile_size
        cave_end_idx = (start_x + width) // self.tile_size + 1
        
        for i in range(cave_start_idx, min(cave_end_idx, len(self.points))):
            x, y = self.points[i]
            if start_x <= x <= start_x + width:
                # Lower the terrain to create an entrance/exit
                self.points[i] = (x, y + height // 2)
    
    def _generate_terrain(self):
        """Generate the initial terrain with biomes and hills"""
        # Clear existing points and biome data
        self.points = []
        self.biome_points = []
        
        # Determine cave position in the stone biome
        self.cave_position = int(self.terrain_width * 0.8)  # Place cave at 80% into the map
        
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
            
            # Extreme height difference for stone biome - massive cliffs and canyons
            base_height_biome = base_height + (biome_blend * 350)  # Huge height difference
            
            # Add extreme height variation in stone biome
            if biome_blend > 0.02:  # Start transition very early
                # Massive, dramatic terrain in stone biome
                stone_large = math.sin(x / 300 + 30) * 500 * biome_blend  # Enormous hills (up to 500px)
                # Very steep, cliff-like features
                stone_medium = math.sin(x / 40 + 40) * 300 * (biome_blend ** 1.2)  # Vertical cliffs
                # Add extreme jaggedness
                stone_small = math.sin(x / 15 + 50) * 150 * (biome_blend ** 1.8)  # Very dramatic details
                
                # Combine with emphasis on large features for massive cliffs
                height_variation += stone_large * 0.6 + stone_medium * 0.5 + stone_small * 0.3
                
                # Add occasional extreme cliffs and drops
                if random.random() < 0.1:  # 10% chance for extreme features
                    feature_type = random.choice(['cliff', 'drop', 'spike'])
                    if feature_type == 'cliff' and biome_blend > 0.3:
                        height_variation += random.uniform(100, 250) * biome_blend
                    elif feature_type == 'drop' and biome_blend > 0.5:
                        height_variation -= random.uniform(80, 180) * biome_blend
                    else:  # spike
                        height_variation += random.uniform(150, 350) * biome_blend
            
            # Final height calculation
            y = base_height_biome + height_variation
            
            # Add extreme random noise for more dramatic look
            noise_scale = 80 if biome_blend > 0.2 else 20  # Very dramatic noise in stone biome
            y += (random.random() - 0.5) * noise_scale * (biome_blend ** 0.5)  # Scale noise with biome blend
            
            # Allow for extreme height variations while keeping within screen bounds
            min_height = 20  # Allow very high peaks
            max_height = WINDOW_HEIGHT - 10  # Allow going near screen edges
            y = max(min_height, min(max_height, y))
            
            # In deep stone biome, add occasional extreme vertical drops
            if biome_blend > 0.7 and random.random() < 0.15:  # 15% chance in deep stone
                if random.random() > 0.5:
                    y = min_height + random.random() * 50  # Extreme peak
                else:
                    y = max_height - random.random() * 50  # Extreme valley
            
            # Store the point
            self.points.append((x, int(y)))
            
            # Store the biome blend for this x position
            self.biome_points.append((x, biome_blend))
        
        # Generate the cave in the stone biome
        if self.cave_position and self.terrain_width > 0:
            cave_width = random.randint(400, 600)  # 400-600 pixels wide
            cave_height = random.randint(150, 250)  # 150-250 pixels tall
            self._generate_cave(self.cave_position, cave_width, cave_height)
        
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
                max_change = 2  # Less smoothing for more defined transitions
            elif biome == 1:  # Stone biome
                # Preserve maximum detail in stone biome for extremely sharp cliffs
                max_change = 3  # Even less smoothing for dramatic cliffs
            else:  # Grass biome
                max_change = 5  # Keep grass biome smoother
            
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
        """Get the height of the ground at a specific x position"""
        # First check if we're in the cave
        if hasattr(self, 'cave_entrance') and hasattr(self, 'cave_exit') and hasattr(self, 'cave_floor'):
            if self.cave_entrance is not None and self.cave_exit is not None and hasattr(self, 'cave_floor'):
                if self.cave_entrance <= x <= self.cave_exit and self.cave_floor:
                    # Find the nearest floor points
                    for i in range(len(self.cave_floor) - 1):
                        x1, y1 = self.cave_floor[i]
                        x2, y2 = self.cave_floor[i + 1]
                        
                        if x1 <= x <= x2:
                            # Linear interpolation between the two points
                            t = (x - x1) / (x2 - x1) if x2 != x1 else 0
                            return int(y1 * (1 - t) + y2 * t)
        
        # If not in cave or cave not generated, use regular terrain
        for i in range(len(self.points) - 1):
            x1, y1 = self.points[i]
            x2, y2 = self.points[i + 1]
            
            if x1 <= x <= x2:
                # Linear interpolation between the two points
                t = (x - x1) / (x2 - x1) if x2 != x1 else 0
                return int(y1 * (1 - t) + y2 * t)
        
        # If we get here, return the height of the last point or default height
        return self.points[-1][1] if self.points else WINDOW_HEIGHT - 100

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

    def is_point_in_cave(self, x, y):
        """Check if a point is inside the cave"""
        if not hasattr(self, 'cave_ceiling') or not hasattr(self, 'cave_floor'):
            return False
            
        if not self.cave_ceiling or not self.cave_floor:
            return False

        # Check if x is within cave bounds
        if x < self.cave_entrance or x > self.cave_exit:
            return False
            
        # Find the nearest ceiling and floor points
        for i in range(len(self.cave_ceiling) - 1):
            x1_c, y1_c = self.cave_ceiling[i]
            x2_c, y2_c = self.cave_ceiling[i + 1]
            x1_f, y1_f = self.cave_floor[i]
            x2_f, y2_f = self.cave_floor[i + 1]

            if x1_c <= x <= x2_c:
                # Interpolate ceiling and floor heights at this x
                t = (x - x1_c) / (x2_c - x1_c) if x2_c != x1_c else 0
                ceiling_y = int(y1_c * (1 - t) + y2_c * t)
                floor_y = int(y1_f * (1 - t) + y2_f * t)

                # Check if y is between ceiling and floor
                return ceiling_y <= y <= floor_y

        return False

    def draw_cave(self, screen, camera_x):
        """Draw the cave if visible"""
        if not hasattr(self, 'cave_ceiling') or not hasattr(self, 'cave_floor'):
            return
            
        if not self.cave_ceiling or not self.cave_floor:
            return
            
        # Only draw if cave is visible
        if not (camera_x - 100 < self.cave_exit and camera_x + WINDOW_WIDTH + 100 > self.cave_entrance):
            return

        # Draw cave ceiling
        for i in range(len(self.cave_ceiling) - 1):
            x1, y1 = self.cave_ceiling[i]
            x2, y2 = self.cave_ceiling[i + 1]
            # Only draw if on screen
            if (x1 > camera_x + WINDOW_WIDTH + 100 and x2 > camera_x + WINDOW_WIDTH + 100) or \
               (x1 < camera_x - 100 and x2 < camera_x - 100):
                continue
                
            pygame.draw.line(screen, (80, 80, 100),  # Darker gray for ceiling
                           (x1 - camera_x, y1), 
                           (x2 - camera_x, y2), 4)  # Slightly thicker line

        # Draw cave floor
        for i in range(len(self.cave_floor) - 1):
            x1, y1 = self.cave_floor[i]
            x2, y2 = self.cave_floor[i + 1]
            # Only draw if on screen
            if (x1 > camera_x + WINDOW_WIDTH + 100 and x2 > camera_x + WINDOW_WIDTH + 100) or \
               (x1 < camera_x - 100 and x2 < camera_x - 100):
                continue
                
            pygame.draw.line(screen, (100, 80, 60),  # Brownish color for floor
                           (x1 - camera_x, y1), 
                           (x2 - camera_x, y2), 4)  # Slightly thicker line

    def draw(self, screen, camera_x):
        """Draw the terrain"""
        # Only draw terrain that's visible on screen
        start_x = max(0, camera_x - 100)
        end_x = min(self.terrain_width, camera_x + WINDOW_WIDTH + 100)
        
        # Draw the cave first (behind everything)
        if hasattr(self, 'cave_entrance') and hasattr(self, 'cave_exit'):
            if self.cave_entrance is not None and self.cave_exit is not None:
                if start_x < self.cave_exit and end_x > self.cave_entrance:
                    self.draw_cave(screen, camera_x)

        # Draw the ground using Terraria-style tiles (sprites)
        tile_size = self.tile_size
        
        # Create a surface for the terrain to reduce draw calls
        terrain_surface = pygame.Surface((WINDOW_WIDTH + 200, WINDOW_HEIGHT), pygame.SRCALPHA)
        
        # Draw the ground tiles
        for x in range(int(start_x), int(end_x), tile_size):
            # Skip if this x is beyond our points
            if x >= len(self.points) * tile_size:
                continue
                
            # Get the ground height at this x position
            ground_y = self.get_ground_height(x)
            screen_x = x - camera_x + 100  # Add 100px buffer for off-screen drawing
            
            # Skip if off-screen
            if screen_x < -tile_size or screen_x > WINDOW_WIDTH + tile_size:
                continue
                
            # Determine which tile to draw based on biome and depth
            biome = self.get_biome_at(x)
            if biome < 0.2:  # Grass biome
                # Draw grass on top layer
                terrain_surface.blit(self.grass_img, (screen_x, ground_y - tile_size))
                # Fill below with dirt
                for y in range(ground_y, WINDOW_HEIGHT, tile_size):
                    if y < WINDOW_HEIGHT - 100:  # Don't draw too far below
                        terrain_surface.blit(self.dirt_img, (screen_x, y))
            else:  # Stone biome
                # Draw stone all the way down
                for y in range(ground_y, WINDOW_HEIGHT, tile_size):
                    if y < WINDOW_HEIGHT - 100:
                        terrain_surface.blit(self.stone_img, (screen_x, y))
        
        # Draw the terrain surface to the screen
        screen.blit(terrain_surface, (-100, 0))  # Offset by -100 to account for buffer
        
        # Draw trees and other vegetation on top of the terrain
        for x in range(int(start_x), int(end_x), tile_size):
            # Skip if this x is beyond our points
            if x >= len(self.points) * tile_size:
                continue
                
            screen_x = x - camera_x
            ground_y = self.get_ground_height(x)
            biome = self.get_biome_at(x)
            
            # Skip if off-screen
            if screen_x < -200 or screen_x > WINDOW_WIDTH + 200:
                continue

            # Draw trees (behind everything else)
            # Check for regular trees first
            if x in self.trees and biome < 0.2 and self.tree_img:
                tree_data = self.tree_data.get(x, {'height': 7, 'scale': 1.0, 'type': 'regular'})
                base_height = tree_data.get('height', 7)
                scale = tree_data.get('scale', 1.0)
                
                # Calculate tree dimensions - regular trees are larger
                tree_height = int(base_height * tile_size * scale)
                min_tree_width = int(tile_size * 1.5)
                tree_width = max(min_tree_width, int(tree_height * 0.7))
                
                # Position tree base at ground level
                tree_y = y - tree_height + tile_size - 5
                tree_x = screen_x - (tree_width // 2) + (tile_size // 2)
                
                # Draw the tree with scaled size
                if tree_width > 0 and tree_height > 0:
                    scaled_tree = pygame.transform.scale(self.tree_img, (tree_width, tree_height))
                    screen.blit(scaled_tree, (tree_x, tree_y))
            
            # Check for pine trees (not in an elif, so both types can be checked)
            if x in self.pine_trees and biome < 0.2 and self.pine_tree_img:
                tree_data = self.tree_data.get(x, {'height': 10, 'scale': 1.0, 'type': 'pine'})
                base_height = tree_data.get('height', 10)
                scale = tree_data.get('scale', 1.0)
                
                # Calculate tree dimensions - pines are less stretched
                tree_height = int(base_height * tile_size * scale)
                min_pine_width = int(tile_size * 1.0)
                tree_width = max(min_pine_width, int(tree_height * 0.5))
                
                # Position tree base at ground level, moved down slightly
                tree_y = y - tree_height + tile_size + 5
                tree_x = screen_x - (tree_width // 2) + (tile_size // 2)
                
                # Draw the pine tree with scaled size
                if tree_width > 0 and tree_height > 0:
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
                    flower_img = self.flower_img  # Default to regular flower
                    if flower_data.get('type') == 'yellow' and self.yellow_flower_img:
                        flower_img = self.yellow_flower_img
                        # Yellow flowers are slightly smaller
                        flower_size = int(flower_size * 0.9)
                    
                    # Draw the flower
                    screen.blit(
                        pygame.transform.scale(flower_img, (flower_size, flower_size)),
                        (screen_x - (flower_size // 2) + (tile_size // 2), flower_y)
                    )

        # Draw the terrain tiles
        for i in range(len(self.points) - 1):
            x1, y1 = self.points[i]
            x2, y2 = self.points[i + 1]
            
            # Skip if completely off-screen
            if x2 < camera_x - 100 or x1 > camera_x + WINDOW_WIDTH + 100:
                continue
                
            # Determine biome for this segment
            biome = self.get_biome_at((x1 + x2) // 2)
            
            # Choose the appropriate tile image based on biome
            if biome < 0.5:  # Grass biome
                tile_img = self.grass_img
            else:  # Stone biome
                tile_img = self.stone_img
                
            # Draw the terrain segment
            segment_width = x2 - x1
            if segment_width > 0 and tile_img:
                # Scale the tile to fit the segment width
                scaled_tile = pygame.transform.scale(tile_img, (segment_width, self.tile_size))
                screen.blit(scaled_tile, (x1 - camera_x, y1 - self.tile_size))

        # Draw the cave ceiling and floor if visible
        if hasattr(self, 'cave_ceiling') and hasattr(self, 'cave_floor'):
            if self.cave_entrance is not None and self.cave_exit is not None:
                if camera_x - 100 < self.cave_exit and camera_x + WINDOW_WIDTH + 100 > self.cave_entrance:
                    self.draw_cave(screen, camera_x)
                    
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
                    flower_img = self.flower_img  # Default to regular flower
                    if flower_data.get('type') == 'yellow' and self.yellow_flower_img:
                        flower_img = self.yellow_flower_img
                        # Yellow flowers are slightly smaller
                        flower_size = int(flower_size * 0.9)
                        
                    # Handle flower variants (tinted versions)
                    if 'variant' in flower_data and flower_data['variant'] == 1:
                        # Create a slightly different colored variant once
                        if 'tinted_img' not in flower_data:
                            flower_data['tinted_img'] = flower_img.copy()
                            # Tint the flower (adjust RGB values as needed)
                            flower_data['tinted_img'].fill((255, 200, 200, 255), special_flags=pygame.BLEND_RGB_MULT)
                        flower_img = flower_data['tinted_img']
                
                    # Draw the flower with consistent rotation
                    if flower_size > 0:
                        # Use stored rotation angle or generate a new one
                        if 'angle' not in flower_data:
                            flower_data['angle'] = random.uniform(-10, 10)  # Slight random rotation
                        angle = flower_data['angle']
                        
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

