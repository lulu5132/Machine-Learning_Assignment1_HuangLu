import pygame
import numpy as np

# Colors
COLOR_FLOOR_LIGHT = (245, 245, 245)
COLOR_FLOOR_DARK = (230, 230, 230)
COLOR_SHELF_MAIN = (139, 69, 19) # SaddleBrown
COLOR_SHELF_TOP = (160, 82, 45)  # Sienna
COLOR_SKIN = (255, 220, 177)
COLOR_SHIRT = (50, 150, 250)     # Blue shirt
COLOR_PANTS = (50, 50, 50)
COLOR_ARROW = (50, 205, 50)      # LimeGreen
COLOR_HIGHLIGHT = (255, 215, 0)  # Gold

def create_floor_tile(size):
    """Creates a checkered floor tile surface."""
    surf = pygame.Surface((size, size))
    surf.fill(COLOR_FLOOR_LIGHT)
    # Add subtle texture or pattern
    pygame.draw.rect(surf, COLOR_FLOOR_DARK, (0, 0, size, size), 1)
    pygame.draw.rect(surf, (240, 240, 240), (2, 2, size-4, size-4))
    return surf

def create_shelf_tile(size):
    """Creates a shelf with random products."""
    surf = pygame.Surface((size, size))
    surf.fill(COLOR_SHELF_MAIN)
    
    # Shelf levels
    levels = 3
    margin = 5
    shelf_height = (size - 2 * margin) // levels
    
    for i in range(levels):
        y = margin + i * shelf_height
        # Draw wooden shelf plank
        pygame.draw.rect(surf, COLOR_SHELF_TOP, (2, y + shelf_height - 4, size - 4, 4))
        
        # Draw random products
        num_products = np.random.randint(2, 5)
        for p in range(num_products):
            w = np.random.randint(4, 10)
            h = np.random.randint(6, 12)
            px = np.random.randint(4, size - 14)
            color = (np.random.randint(50, 150), np.random.randint(50, 150), np.random.randint(150, 255))
            pygame.draw.rect(surf, color, (px, y + shelf_height - 4 - h, w, h))
            
    # Side panels
    pygame.draw.rect(surf, (100, 50, 10), (0, 0, 3, size))
    pygame.draw.rect(surf, (100, 50, 10), (size-3, 0, 3, size))
    return surf

def create_character_sprite(size):
    """Creates a simple pixel-art style character."""
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Body dimensions
    w, h = size // 2, size // 2
    x, y = size // 4, size // 4
    
    # Head
    pygame.draw.circle(surf, COLOR_SKIN, (size//2, size//3), size//6)
    
    # Body (Shirt)
    pygame.draw.rect(surf, COLOR_SHIRT, (x, size//2, w, h//1.5))
    
    # Pants
    pygame.draw.rect(surf, COLOR_PANTS, (x, size//2 + h//1.5, w//2 - 1, h//2))
    pygame.draw.rect(surf, COLOR_PANTS, (x + w//2 + 1, size//2 + h//1.5, w//2 - 1, h//2))
    
    # Shoes
    pygame.draw.rect(surf, (20, 20, 20), (x, size - 5, w//2, 5))
    pygame.draw.rect(surf, (20, 20, 20), (x + w//2 + 1, size - 5, w//2, 5))
    
    return surf

def create_target_item_sprite(size):
    """Creates a distinct target item (e.g., Red Apple or Cereal Box)."""
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Example: A Red Apple with a leaf
    center = size // 2
    radius = size // 3
    pygame.draw.circle(surf, (220, 20, 60), (center, center + 2), radius) # Red body
    pygame.draw.circle(surf, (255, 100, 100), (center - 5, center - 5), 4) # Shine
    
    # Stem
    pygame.draw.line(surf, (101, 67, 33), (center, center - radius), (center, center - radius - 5), 3)
    
    # Leaf
    points = [(center, center - radius - 2), (center + 8, center - radius - 6), (center, center - radius - 8)]
    pygame.draw.polygon(surf, (50, 205, 50), points)
    
    return surf

def create_arrow_sprite(size):
    """Creates a bouncy arrow sprite."""
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Draw arrow pointing right (default), can rotate later
    # Arrow body
    pygame.draw.rect(surf, COLOR_ARROW, (0, size//2 - 5, size - 15, 10))
    # Arrow head
    points = [(size - 15, size//2 - 15), (size, size//2), (size - 15, size//2 + 15)]
    pygame.draw.polygon(surf, COLOR_ARROW, points)
    
    # Outline for visibility
    pygame.draw.polygon(surf, (255, 255, 255), points, 2)
    return surf
