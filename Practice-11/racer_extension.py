import pygame
import random

# Initialize Pygame
pygame.init()

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)      # Color for weight 2 coins
ORANGE = (255, 165, 0)    # Color for weight 3 coins
LIGHT_YELLOW = (255, 255, 150)  # Color for weight 1 coins
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# --- Game Window Setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer Game - Weighted Coins Edition")
clock = pygame.time.Clock()

# --- Load Images ---
# For this example, we create simple colored rectangles as car images.
# In a real game, you would load actual PNG images.
player_car = pygame.Surface((50, 80))
player_car.fill(GREEN)  # Green player car
enemy_car = pygame.Surface((50, 80))
enemy_car.fill(RED)    # Red enemy car

# --- Game Variables ---
player_x = SCREEN_WIDTH // 2 - 25
player_y = SCREEN_HEIGHT - 100
player_speed = 5

enemy_list = []
enemy_speed = 5          # Initial enemy speed
enemy_spawn_timer = 0

coins = []               # List to store coin objects (not just rects)
score = 0
coins_collected = 0      # Track total number of coins collected (not score)
COINS_TO_INCREASE_SPEED = 5  # Increase enemy speed every 5 coins collected

# Font for displaying score and info
font = pygame.font.SysFont("Arial", 30)
small_font = pygame.font.SysFont("Arial", 20)

class Coin:
    """
    Coin class with different weights.
    Weight determines point value and appearance.
    """
    class Weight:
        LIGHT = 1    # Worth 1 point, small size, light color
        NORMAL = 2   # Worth 2 points, medium size, gold color
        HEAVY = 3    # Worth 3 points, large size, orange color
    
    def __init__(self, x, y, weight):
        """
        Initialize a coin with position and weight.
        
        Args:
            x: X-coordinate of the coin
            y: Y-coordinate of the coin
            weight: Weight value (1, 2, or 3)
        """
        self.x = x
        self.y = y
        self.weight = weight
        
        # Size varies based on weight (heavier = larger)
        self.size = 20 + (weight - 1) * 5  # 20, 25, or 30 pixels
        self.rect = pygame.Rect(x, y, self.size, self.size)
        
    def update(self):
        """Update coin position (move downward)."""
        self.y += 5
        self.rect.y = self.y
        
    def draw(self, screen):
        """Draw the coin with color based on weight."""
        # Select color based on weight
        if self.weight == self.Weight.LIGHT:
            color = LIGHT_YELLOW
        elif self.weight == self.Weight.NORMAL:
            color = GOLD
        else:  # HEAVY
            color = ORANGE
            
        # Draw coin as circle
        pygame.draw.circle(screen, color, 
                          (self.x + self.size//2, self.y + self.size//2), 
                          self.size//2)
        # Draw border
        pygame.draw.circle(screen, BLACK, 
                          (self.x + self.size//2, self.y + self.size//2), 
                          self.size//2, 2)
        
        # Draw weight number on the coin
        weight_text = small_font.render(str(self.weight), True, BLACK)
        text_rect = weight_text.get_rect(center=(self.x + self.size//2, self.y + self.size//2))
        screen.blit(weight_text, text_rect)

class Enemy:
    """Enemy car class with speed tracking."""
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.rect = pygame.Rect(x, y, 50, 80)
        
    def update(self):
        """Move enemy downward."""
        self.y += self.speed
        self.rect.y = self.y
        
    def draw(self, screen):
        """Draw the enemy car."""
        screen.blit(enemy_car, (self.x, self.y))

def draw_text(text, color, x, y):
    """Helper function to draw text on the screen."""
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def create_enemy():
    """
    Creates a new enemy car at a random x-position.
    
    Returns:
        Enemy object with current enemy speed
    """
    enemy_x = random.randint(0, SCREEN_WIDTH - 50)
    return Enemy(enemy_x, -80, enemy_speed)

def create_coin():
    """
    Creates a new coin with random weight at random x-position.
    Different weights have different spawn probabilities:
    - Light (40% chance) - worth 1 point
    - Normal (40% chance) - worth 2 points  
    - Heavy (20% chance) - worth 3 points
    
    Returns:
        Coin object with random weight
    """
    coin_x = random.randint(0, SCREEN_WIDTH - 30)
    
    # Random weight selection with different probabilities
    rand = random.randint(1, 100)
    if rand <= 40:      # 40% chance for light coin
        weight = Coin.Weight.LIGHT
    elif rand <= 80:    # 40% chance for normal coin
        weight = Coin.Weight.NORMAL
    else:               # 20% chance for heavy coin
        weight = Coin.Weight.HEAVY
        
    return Coin(coin_x, -30, weight)

def increase_enemy_speed():
    """
    Increase enemy speed when player collects N coins.
    Global enemy_speed variable is modified.
    """
    global enemy_speed
    enemy_speed += 1
    # Update speed for all existing enemies
    for enemy in enemy_list:
        enemy.speed = enemy_speed
    print(f"Speed increased! Current enemy speed: {enemy_speed}")

# --- Main Game Loop ---
running = True
while running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Player Movement (Arrow Keys) ---
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < SCREEN_WIDTH - 50:
        player_x += player_speed

    # --- Enemy Management ---
    # Spawn enemies at regular intervals
    enemy_spawn_timer += 1
    if enemy_spawn_timer > 60:  # Spawn a new enemy every second (60 frames)
        enemy_list.append(create_enemy())
        enemy_spawn_timer = 0

    # Move enemies downwards and remove those off-screen
    for enemy in enemy_list[:]:  # Iterate over a copy of the list to safely remove items
        enemy.update()
        if enemy.y > SCREEN_HEIGHT:
            enemy_list.remove(enemy)

    # --- Coin Management ---
    # Randomly spawn coins (5% chance each frame)
    if random.randint(1, 100) < 5:
        coins.append(create_coin())

    # Move coins downwards and remove off-screen coins
    for coin in coins[:]:
        coin.update()
        if coin.y > SCREEN_HEIGHT:
            coins.remove(coin)

    # --- Collision Detection ---
    player_rect = pygame.Rect(player_x, player_y, 50, 80)

    # Check collision with enemies (Game Over)
    for enemy in enemy_list:
        if player_rect.colliderect(enemy.rect):
            running = False  # End game on collision

    # Check collision with coins (Increase score based on weight)
    for coin in coins[:]:
        if player_rect.colliderect(coin.rect):
            # Add points based on coin weight
            score += coin.weight
            coins_collected += 1
            coins.remove(coin)
            
            # Check if we need to increase enemy speed
            if coins_collected % COINS_TO_INCREASE_SPEED == 0:
                increase_enemy_speed()

    # --- Drawing ---
    screen.fill(WHITE)  # Clear screen with white background

    # Draw player car
    screen.blit(player_car, (player_x, player_y))

    # Draw enemies
    for enemy in enemy_list:
        enemy.draw(screen)

    # Draw coins
    for coin in coins:
        coin.draw(screen)

    # Display game information
    draw_text(f"Score: {score}", BLACK, SCREEN_WIDTH - 120, 10)
    draw_text(f"Coins: {coins_collected}", BLACK, SCREEN_WIDTH - 120, 45)
    draw_text(f"Speed: {enemy_speed}", BLACK, SCREEN_WIDTH - 120, 80)
    
    # Display instructions
    instruction_text = small_font.render("← → Move | Collect coins (1,2,3 pts) | Speed↑ every 5 coins", True, BLACK)
    screen.blit(instruction_text, (10, SCREEN_HEIGHT - 30))

    # Update display
    pygame.display.update()
    clock.tick(FPS)

# --- Game Over Screen ---
# Show final score before quitting
screen.fill(WHITE)
game_over_text = font.render("GAME OVER!", True, RED)
final_score_text = font.render(f"Final Score: {score}", True, BLACK)
coins_collected_text = font.render(f"Coins Collected: {coins_collected}", True, BLACK)
max_speed_text = font.render(f"Max Enemy Speed: {enemy_speed}", True, BLACK)

screen.blit(game_over_text, (SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2 - 60))
screen.blit(final_score_text, (SCREEN_WIDTH//2 - 90, SCREEN_HEIGHT//2 - 20))
screen.blit(coins_collected_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 20))
screen.blit(max_speed_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 60))

pygame.display.update()
pygame.time.wait(3000)  # Show game over screen for 3 seconds

# Quit the game properly
pygame.quit()