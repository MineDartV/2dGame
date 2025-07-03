import pygame
import math
import time
import colorsys
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, SKY_BLUE
from utils import load_sprite

class DayNightCycle:
    def __init__(self):
        import time  # For debug timing
        self.time_of_day = 0.0  # Start at midnight (0 = midnight, 0.25 = sunset, 0.5 = midnight, 0.75 = sunrise, 1.0 = next midnight)
        self.day_duration = 30.0  # seconds for a full day/night cycle (reduced for testing)
        self.night_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        self.last_debug = time.time()
        self.last_transition_time = time.time()  # Initialize with current time
        self.twilight_duration = 0.15  # 15% of day/night cycle for twilight (4.5 seconds with 30s cycle)
        # Debug output removed for performance
        # print(f"Initializing DayNightCycle with WINDOW_WIDTH={WINDOW_WIDTH}, WINDOW_HEIGHT={WINDOW_HEIGHT}")
        # print(f"Day duration: {self.day_duration} seconds")
        
        # Try to load celestial bodies with better error handling
        def load_image(paths, name, default_color, size=(100, 100)):
            for path in paths:
                try:
                    img = pygame.image.load(path).convert_alpha()
                    # Debug output removed for performance
                    # print(f"Loaded {name} from: {path}, original size: {img.get_size()}")
                    # Scale to reasonable size while maintaining aspect ratio
                    img = pygame.transform.scale(img, size)
                    return img
                except Exception as e:
                    # Debug output removed for performance
                    # print(f"Could not load {name} from {path}: {e}")
                    pass
            
            # Create fallback surface if loading failed
            # Debug output removed for performance
            # print(f"Creating fallback {name}")
            surface = pygame.Surface(size, pygame.SRCALPHA)
            pygame.draw.circle(surface, default_color, 
                             (size[0]//2, size[1]//2), 
                             min(size)//2)
            return surface
        
        # Load sun and moon with larger default size
        self.sun = load_sprite("sun.png")
        self.sun = pygame.transform.scale(self.sun, (120, 120))
        self.moon = load_sprite("moon.png")
        self.moon = pygame.transform.scale(self.moon, (120, 120))
        # self.sun = load_image(['assets/sun.png', 'sun.png'], 
        #                     'sun', (255, 255, 0), (120, 120))
        # self.moon = load_image(['assets/moon.png', 'moon.png'], 
        #                      'moon', (200, 200, 200), (100, 100))
        
        # Debug output removed for performance
        # print(f"Final sizes - Sun: {self.sun.get_size()}, Moon: {self.moon.get_size()}")
        
        # Make sure we have valid surfaces
        if not isinstance(self.sun, pygame.Surface) or not isinstance(self.moon, pygame.Surface):
            raise RuntimeError("Failed to initialize sun and moon surfaces")
        
        # Celestial body positions
        self.sun_x = -100  # Start off-screen
        self.sun_y = WINDOW_HEIGHT // 3
        self.moon_x = -100  # Start off-screen
        self.moon_y = WINDOW_HEIGHT // 3
        
        self.is_day = True
        self.transition_speed = 0.5  # Speed of day/night transition
        self.night_alpha = 0  # 0 = full day, 255 = full night
        
    def update(self, dt):
        # Update time of day
        prev_time = self.time_of_day
        self.time_of_day = (self.time_of_day + dt / self.day_duration) % 1.0
        
        # Debug output for time changes - removed for performance
        # if int(prev_time * 100) != int(self.time_of_day * 100):
        #     print(f"Time of day: {self.time_of_day:.2f} (Day: {0.0 <= self.time_of_day < 0.5})")
        
        # Calculate time of day factors (0-1)
        self.day_factor = max(0, min(1, self.time_of_day * 2))  # 0 at midnight, 1 at noon
        self.day_factor = min(self.day_factor, 2 - self.time_of_day * 2)  # 1 at noon, 0 at next midnight
        
        # Track transitions
        current_time = time.time()
        if (prev_time < 0.5 and self.time_of_day >= 0.5) or (prev_time >= 0.5 and self.time_of_day < 0.5):
            # Day/night boundary crossed
            self.last_transition_time = current_time
        
        # Calculate positions for sun and moon in circular paths
        # Full day/night cycle is 24 hours, mapped to 0-1 range (0 = sunrise, 1.0 = next sunrise)
        # Sun rises at 0.0 (east/right), peaks at 0.5 (overhead), sets at 1.0 (west/left)
        # Moon rises at 0.5 (east/right), peaks at 1.0 (overhead), sets at 1.5 (west/left)
        
        # Constants for the circular path
        radius = min(WINDOW_WIDTH, WINDOW_HEIGHT) * 0.6  # Slightly smaller radius for better visibility
        center_x = WINDOW_WIDTH // 2
        center_y = WINDOW_HEIGHT * 0.8  # Center above the middle of the screen
        
        # Convert time of day (0-1) to an angle (0 to 2π)
        # Start at -90° (top of circle) and go clockwise
        angle = (self.time_of_day * 2 * math.pi) - (math.pi / 2)
        
        # Calculate sun position (follows the circular path directly)
        self.sun_x = center_x + math.cos(angle) * radius
        self.sun_y = center_y + math.sin(angle) * radius
        
        # Moon follows the same path but offset by 12 hours (π radians)
        moon_angle = (angle + math.pi) % (2 * math.pi)
        self.moon_x = center_x + math.cos(moon_angle) * radius
        self.moon_y = center_y + math.sin(moon_angle) * radius
        
        # Update day/night state and transition
        was_day = self.is_day
        self.is_day = 0.0 <= self.time_of_day < 0.5
        
        # Calculate night intensity (0 = full day, 1 = full night)
        # Use a sine wave for smoother transitions
        night_intensity = math.sin(self.time_of_day * math.pi)
        
        # Apply a curve to make the transition sharper at the edges
        night_intensity = math.pow(night_intensity, 0.5)  # Adjust the exponent to control the curve
        
        # Scale to 0-255 range for alpha
        self.night_alpha = int(200 * night_intensity)
        self.night_alpha = max(0, min(200, self.night_alpha))  # Clamp between 0 and 200
    
    def get_sky_color(self):
        """Get the current sky color based on time of day"""
        # Base sky colors
        day_color = SKY_BLUE
        twilight_color = (70, 60, 100)  # Purple-blue for twilight
        night_color = (10, 10, 30)  # Dark blue-black for night
        
        # Calculate the horizon line (where y = center_y)
        center_y = WINDOW_HEIGHT * 0.8
        horizon_line = center_y
        
        # Get the current sun and moon positions
        sun_screen_y = self.sun_y - self.sun.get_height() / 2  # Top of sun
        moon_screen_y = self.moon_y - self.moon.get_height() / 2  # Top of moon
        
        # Calculate sun and moon height ratios (-1 to 1, where 0 is horizon)
        sun_height_ratio = (horizon_line - sun_screen_y) / (WINDOW_HEIGHT * 0.4)
        moon_height_ratio = (horizon_line - moon_screen_y) / (WINDOW_HEIGHT * 0.4)
        
        # Normalize time to 0.0-1.0 range
        time_of_day = self.time_of_day % 1.0
        
        # Define the day/night cycle phases
        # Sun rises at 0.0, sets at 0.5
        # Moon rises at 0.5, sets at 0.0
        
        # Calculate sun and moon visibility based on height ratio with smoother transitions
        # Extend the transition zone for smoother changes
        sun_visibility = max(0, min(1, (sun_height_ratio + 1.0) * 0.5))  # Smoother transition from -1 to 1
        moon_visibility = max(0, min(1, (moon_height_ratio + 1.0) * 0.5))  # Smoother transition from -1 to 1
        
        # Determine day/night based on which celestial body is more visible
        # Use a smoothstep function for smoother transitions
        def smoothstep(edge0, edge1, x):
            # Scale, and clamp x to 0..1 range
            x = max(0.0, min(1.0, (x - edge0) / (edge1 - edge0)))
            return x * x * (3.0 - 2.0 * x)  # Smoothstep formula
        
        # Calculate the blend factor between day and night
        # This creates a smooth transition over a longer period
        day_night_blend = (sun_visibility - moon_visibility) * 0.5 + 0.5  # Convert to 0-1 range
        
        # Apply smoothstep to the blend factor for a more gradual transition
        blend = smoothstep(0.0, 1.0, day_night_blend)
        
        # Calculate the final color based on the blend factor
        factor = 1.0 - blend  # 0 = full day, 1 = full night
        current_color = (
            int(day_color[0] * (1 - factor) + night_color[0] * factor),
            int(day_color[1] * (1 - factor) + night_color[1] * factor),
            int(day_color[2] * (1 - factor) + night_color[2] * factor)
        )
        
        # Add twilight effect when both sun and moon are near horizon
        if 0.3 < sun_visibility < 0.7 or 0.3 < moon_visibility < 0.7:
            # Calculate twilight intensity (strongest when both are near horizon)
            twilight_intensity = min(
                smoothstep(0.3, 0.5, sun_visibility) * smoothstep(0.7, 0.5, sun_visibility),
                smoothstep(0.3, 0.5, moon_visibility) * smoothstep(0.7, 0.5, moon_visibility)
            )
            
            # Blend in some twilight color
            current_color = (
                int(current_color[0] * (1 - twilight_intensity) + twilight_color[0] * twilight_intensity * 0.5),
                int(current_color[1] * (1 - twilight_intensity) + twilight_color[1] * twilight_intensity * 0.5),
                int(current_color[2] * (1 - twilight_intensity) + twilight_color[2] * twilight_intensity * 0.5)
            )
        
        # Add a small twilight effect when both sun and moon are near horizon
        if 0.4 < sun_visibility < 0.6 and 0.4 < moon_visibility < 0.6:
            # Blend in some twilight color
            twilight_factor = min(sun_visibility, moon_visibility) * 2 - 0.8
            current_color = (
                int(current_color[0] * 0.7 + twilight_color[0] * 0.3 * twilight_factor),
                int(current_color[1] * 0.7 + twilight_color[1] * 0.3 * twilight_factor),
                int(current_color[2] * 0.7 + twilight_color[2] * 0.3 * twilight_factor)
            )
        
        # Apply the final color with proper day/night factor
        r = int(current_color[0] * (1 - factor) + night_color[0] * factor)
        g = int(current_color[1] * (1 - factor) + night_color[1] * factor)
        b = int(current_color[2] * (1 - factor) + night_color[2] * factor)
        
        # Ensure values are within valid range
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        
        return (r, g, b)
    
    def draw(self, screen):
        if not hasattr(self, 'sun') or not hasattr(self, 'moon'):
            print("ERROR: Sun or moon surface not initialized!")
            return
            
        # No debug visuals in production
        
        # Draw sun
        sun_pos = (int(self.sun_x), int(self.sun_y))
        sun_rect = self.sun.get_rect(center=sun_pos)
        screen.blit(self.sun, sun_rect)
        
        # Draw moon
        moon_pos = (int(self.moon_x), int(self.moon_y))
        moon_rect = self.moon.get_rect(center=moon_pos)
        screen.blit(self.moon, moon_rect)
        
        # Draw night overlay with gradient based on time of day
        if self.night_alpha > 0:
            # Clear the night surface with transparent color
            self.night_surface.fill((0, 0, 0, 0))
            
            # Create a gradient from top to bottom (darker at top)
            for y in range(0, WINDOW_HEIGHT, 2):
                # Calculate gradient factor (0 at bottom, 1 at top)
                gradient = 1.0 - (y / WINDOW_HEIGHT)
                # Calculate alpha based on night intensity and gradient
                alpha = int(self.night_alpha * (0.7 + 0.3 * gradient))
                if alpha > 0:  # Only draw if alpha is greater than 0
                    pygame.draw.line(self.night_surface, (0, 0, 30, alpha), 
                                   (0, y), (WINDOW_WIDTH, y))
            
            # Draw the night overlay
            screen.blit(self.night_surface, (0, 0))
