# racer.py - Game objects and logic for Racer (TSIS 3)
# Contains player, enemies, obstacles, coins, power-ups, and their movement

import pygame
import random
import os

# X-coordinates for the three lanes (center positions of each lane)
LANES = [200, 300, 400]
# Base speed for moving objects (pixels per frame)
SPEED_BASE = 5

def load_image(name, width, height):
    """
    Load an image from assets/images folder, scale it, and return a Surface.
    If the image file is missing, return a magenta rectangle as a fallback.
    """
    path = os.path.join('assets', 'images', name)
    try:
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, (width, height))
    except FileNotFoundError:
        # Fallback: create a solid magenta rectangle
        surf = pygame.Surface((width, height))
        surf.fill((255, 0, 255))
        return surf

class Player(pygame.sprite.Sprite):
    """Player's car sprite that can be controlled with left/right arrows."""
    def __init__(self, color_name):
        super().__init__()
        filename = f"player_{color_name}.png"          # e.g. player_red.png
        self.image = load_image(filename, 40, 70)      # load car image
        self.rect = self.image.get_rect(center=(300, 500))   # starting position
        self.speed = 6                                 # base movement speed
        self.shield_active = False                     # protection from collision
        self.nitro_active = False                      # speed boost active
        self.powerup_timer = 0                         # time when power-up expires
        self.crashes_allowed = 0                       # extra lives from Repair

    def update(self):
        """Handle keyboard input and power-up expiration."""
        keys = pygame.key.get_pressed()
        # Increase player speed if nitro is active
        current_speed = self.speed * 1.5 if self.nitro_active else self.speed
        # Move left (but not beyond road edge 150)
        if keys[pygame.K_LEFT] and self.rect.left > 150:
            self.rect.x -= current_speed
        # Move right (road edge at 450 - car width 40 = 410, but limit to 450 is safe)
        if keys[pygame.K_RIGHT] and self.rect.right < 450:
            self.rect.x += current_speed

        # Check if any active power-up has timed out
        if (self.nitro_active or self.shield_active) and pygame.time.get_ticks() > self.powerup_timer:
            self.nitro_active = False
            self.shield_active = False

class Enemy(pygame.sprite.Sprite):
    """Enemy car that moves downwards. Speed depends on difficulty and coin bonus."""
    def __init__(self, difficulty, speed_boost=0):
        super().__init__()
        self.image = load_image("enemy.png", 40, 70)   # load enemy car image
        # Start above the screen in a random lane
        self.rect = self.image.get_rect(center=(random.choice(LANES), -100))
        # Base speed based on difficulty level
        if difficulty == "easy":
            base = SPEED_BASE - 2    # e.g., 3
        elif difficulty == "normal":
            base = SPEED_BASE        # 5
        else:  # hard
            base = SPEED_BASE + 2    # 7
        base = max(2, base)          # ensure speed never below 2
        self.speed = base + speed_boost   # add extra speed from collected coins

    def update(self):
        """Move enemy downwards and remove when off screen."""
        self.rect.y += self.speed
        if self.rect.top > 600:
            self.kill()

class Obstacle(pygame.sprite.Sprite):
    """Static obstacle (barrier, oil, pothole) that spawns in a lane."""
    def __init__(self):
        super().__init__()
        # Use obstacle image or fallback rectangle
        self.image = load_image("obstacle.png", 40, 40)
        self.rect = self.image.get_rect(center=(random.choice(LANES), -50))

    def update(self):
        """Move obstacle downwards at base speed and remove off screen."""
        self.rect.y += SPEED_BASE
        if self.rect.top > 600:
            self.kill()

class Coin(pygame.sprite.Sprite):
    """Collectible coin with weighted value (1,2,5) and different colors."""
    def __init__(self):
        super().__init__()
        # Weight determines value: 1 (gold), 2 (silver), 5 (bronze)
        self.weight = random.choice([1, 2, 5])
        if self.weight == 1:
            color = (255, 215, 0)    # gold
        elif self.weight == 2:
            color = (192, 192, 192)  # silver
        else:
            color = (255, 140, 0)    # bronze (orange)
        # Create a coin shape using a circle (no external image needed)
        self.image = pygame.Surface((25, 25), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (12, 12), 12)          # filled circle
        pygame.draw.circle(self.image, (255, 255, 255), (12, 12), 12, 2)  # white border
        self.rect = self.image.get_rect(center=(random.choice(LANES), -50))

    def update(self):
        """Move coin downwards and remove off screen."""
        self.rect.y += SPEED_BASE
        if self.rect.top > 600:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    """Power-up item: Nitro, Shield, or Repair."""
    def __init__(self):
        super().__init__()
        # Randomly choose one of the three power-up types
        self.type = random.choice(["Nitro", "Shield", "Repair"])
        img_name = self.type.lower() + ".png"   # e.g. "nitro.png"
        self.image = load_image(img_name, 30, 30)
        self.rect = self.image.get_rect(center=(random.choice(LANES), -50))

    def update(self):
        """Move power-up downwards and remove off screen."""
        self.rect.y += SPEED_BASE
        if self.rect.top > 600:
            self.kill()