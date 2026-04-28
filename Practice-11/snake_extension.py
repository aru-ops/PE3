import pygame
import random
import time

# Initialize Pygame
pygame.init()

# --- Constants ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
CELL_SIZE = 20
FPS = 10  # Base frames per second

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 150, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# --- Snake Class ---
class Snake:
    def __init__(self):
        # Start with 5 segments in the middle of the screen
        start_x = SCREEN_WIDTH // 2
        start_y = SCREEN_HEIGHT // 2
        self.body = [
            (start_x, start_y),
            (start_x - CELL_SIZE, start_y),
            (start_x - 2 * CELL_SIZE, start_y),
            (start_x - 3 * CELL_SIZE, start_y),
            (start_x - 4 * CELL_SIZE, start_y)
        ]
        self.direction = RIGHT
        self.grow_flag = False

    def move(self):
        """Move the snake by adding a new head and removing the tail."""
        head = self.body[0]
        dx, dy = self.direction
        new_head = (head[0] + dx * CELL_SIZE, head[1] + dy * CELL_SIZE)

        # Insert new head
        self.body.insert(0, new_head)

        # If not growing, remove the tail
        if not self.grow_flag:
            self.body.pop()
        else:
            self.grow_flag = False

    def grow(self):
        """Set flag to grow the snake on the next move."""
        self.grow_flag = True

    def check_collision(self):
        """Check if the snake hits the wall or itself."""
        head = self.body[0]

        # Wall collision
        if (head[0] < 0 or head[0] >= SCREEN_WIDTH or
            head[1] < 0 or head[1] >= SCREEN_HEIGHT):
            return True

        # Self collision
        if head in self.body[1:]:
            return True

        return False

    def draw(self, screen):
        """Draw the snake on the screen."""
        for i, segment in enumerate(self.body):
            if i == 0:  # Head
                color = DARK_GREEN
            else:       # Body
                color = GREEN
            pygame.draw.rect(screen, color,
                           (segment[0], segment[1], CELL_SIZE, CELL_SIZE))

# --- Special Food Class (with weight and timer) ---
class SpecialFood:
    """
    Food class with different weights and expiration timer.
    Weight determines point value, size, color, and lifetime.
    """
    class Weight:
        LIGHT = 1    # Worth 1 point, stays 5 seconds
        NORMAL = 2   # Worth 2 points, stays 3 seconds
        HEAVY = 3    # Worth 3 points, stays 2 seconds
    
    def __init__(self, snake_body, position=None):
        """
        Initialize special food with random weight and position.
        
        Args:
            snake_body: Current snake body positions (to avoid spawning on snake)
            position: Optional specific position (if None, generates random)
        """
        self.weight = self.generate_random_weight()
        self.position = position if position else self.generate_random_position(snake_body)
        self.spawn_time = time.time()
        
        # Set lifetime based on weight (heavier food disappears faster)
        self.lifetime = {
            self.Weight.LIGHT: 5.0,   # 5 seconds
            self.Weight.NORMAL: 3.0,  # 3 seconds
            self.Weight.HEAVY: 2.0    # 2 seconds
        }[self.weight]
        
        # Set color based on weight
        self.color = {
            self.Weight.LIGHT: BLUE,
            self.Weight.NORMAL: ORANGE,
            self.Weight.HEAVY: PURPLE
        }[self.weight]
        
        # Size increases with weight
        self.size = CELL_SIZE + (self.weight - 1) * 2  # 20, 22, or 24 pixels
        
    def generate_random_weight(self):
        """
        Generate random weight with different probabilities.
        Light: 50% chance, Normal: 30% chance, Heavy: 20% chance
        """
        rand = random.randint(1, 100)
        if rand <= 50:      # 50% chance for light food
            return self.Weight.LIGHT
        elif rand <= 80:    # 30% chance for normal food
            return self.Weight.NORMAL
        else:               # 20% chance for heavy food
            return self.Weight.HEAVY
            
    def generate_random_position(self, snake_body):
        """Generate a random position that is not occupied by the snake."""
        while True:
            x = random.randint(0, (SCREEN_WIDTH // CELL_SIZE) - 1) * CELL_SIZE
            y = random.randint(0, (SCREEN_HEIGHT // CELL_SIZE) - 1) * CELL_SIZE
            if (x, y) not in snake_body:
                return (x, y)
                
    def is_expired(self):
        """Check if the food has expired (disappeared)."""
        return time.time() - self.spawn_time > self.lifetime
        
    def get_remaining_time(self):
        """Get remaining time before food disappears."""
        remaining = self.lifetime - (time.time() - self.spawn_time)
        return max(0, remaining)
        
    def draw(self, screen):
        """Draw the food with timer indicator."""
        # Draw food rectangle
        offset = (CELL_SIZE - self.size) // 2
        pygame.draw.rect(screen, self.color,
                        (self.position[0] + offset, self.position[1] + offset, 
                         self.size, self.size))
        
        # Draw weight number on food
        font = pygame.font.SysFont("Arial", 12)
        weight_text = font.render(str(self.weight), True, WHITE)
        text_rect = weight_text.get_rect(center=(self.position[0] + CELL_SIZE//2, 
                                                  self.position[1] + CELL_SIZE//2))
        screen.blit(weight_text, text_rect)
        
        # Draw timer indicator (shrinking circle or bar)
        remaining_percent = self.get_remaining_time() / self.lifetime
        timer_height = 3
        timer_width = int(CELL_SIZE * remaining_percent)
        pygame.draw.rect(screen, WHITE,
                        (self.position[0], self.position[1] - 5, 
                         timer_width, timer_height))

# --- Game Setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game - Special Food Edition")
clock = pygame.time.Clock()

# --- Game Variables ---
snake = Snake()
special_foods = []  # List of SpecialFood objects (can have multiple)
score = 0
level = 1
foods_for_next_level = 3  # Foods needed to advance to the next level
foods_eaten = 0

# Spawn timer for special food
food_spawn_timer = 0
FOOD_SPAWN_DELAY = 90  # Frames between food spawns (about 1.5 seconds at 60 FPS)

# Font for UI
font = pygame.font.SysFont("Arial", 24)
small_font = pygame.font.SysFont("Arial", 16)

def draw_text(text, color, x, y):
    """Helper function to draw text on the screen."""
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def show_game_over():
    """Display a game over message and wait for user input."""
    # Create overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    game_over_text = font.render("GAME OVER!", True, RED)
    restart_text = small_font.render("Press R to restart or ESC to quit", True, WHITE)
    final_score = small_font.render(f"Final Score: {score}", True, YELLOW)
    
    screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
    screen.blit(final_score, (SCREEN_WIDTH//2 - final_score.get_width()//2, SCREEN_HEIGHT//2))
    screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 50))
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True  # Restart game
                if event.key == pygame.K_ESCAPE:
                    return False  # Quit game
    return False

# --- Main Game Loop ---
running = True
while running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and snake.direction != DOWN:
                snake.direction = UP
            elif event.key == pygame.K_DOWN and snake.direction != UP:
                snake.direction = DOWN
            elif event.key == pygame.K_LEFT and snake.direction != RIGHT:
                snake.direction = LEFT
            elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                snake.direction = RIGHT

    # --- Game Logic ---
    snake.move()

    # --- Special Food Spawning ---
    food_spawn_timer += 1
    # Spawn new food periodically (but limit to max 5 foods on screen)
    if food_spawn_timer >= FOOD_SPAWN_DELAY and len(special_foods) < 5:
        special_foods.append(SpecialFood(snake.body))
        food_spawn_timer = 0

    # --- Update Special Foods (check expiration) ---
    for food in special_foods[:]:
        if food.is_expired():
            special_foods.remove(food)  # Remove expired food

    # --- Check if snake eats any special food ---
    head_position = snake.body[0]
    for food in special_foods[:]:
        if head_position == food.position:
            # Add points based on food weight
            score += food.weight * 10  # Light=10, Normal=20, Heavy=30 points
            foods_eaten += 1
            snake.grow()
            special_foods.remove(food)
            
            # Level up logic: every N foods, increase level and speed
            if foods_eaten % foods_for_next_level == 0:
                level += 1
                print(f"Level up! Now at level {level}")

    # --- Check for collisions (Game Over) ---
    if snake.check_collision():
        # Show game over message and ask to restart or quit
        if show_game_over():
            # Restart the game
            snake = Snake()
            special_foods = []
            score = 0
            level = 1
            foods_eaten = 0
            food_spawn_timer = 0
            continue
        else:
            running = False

    # --- Drawing ---
    screen.fill(BLACK)  # Clear screen

    # Draw snake
    snake.draw(screen)

    # Draw all special foods
    for food in special_foods:
        food.draw(screen)

    # Draw UI (Score and Level)
    draw_text(f"Score: {score}", WHITE, 10, 10)
    draw_text(f"Level: {level}", WHITE, SCREEN_WIDTH - 100, 10)
    draw_text(f"Foods: {foods_eaten}", WHITE, SCREEN_WIDTH - 100, 40)
    
    # Draw instructions
    inst1 = small_font.render("Arrow keys to move", WHITE, True)
    inst2 = small_font.render("Food weights: 1(blue) 2(orange) 3(purple)", WHITE, True)
    inst3 = small_font.render("Heavier food = more points but disappears faster!", YELLOW, True)
    screen.blit(inst1, (10, SCREEN_HEIGHT - 50))
    screen.blit(inst2, (10, SCREEN_HEIGHT - 35))
    screen.blit(inst3, (10, SCREEN_HEIGHT - 20))

    # Update display
    pygame.display.update()

    # Control game speed (increase with level)
    base_fps = 10
    speed_increase_per_level = 2
    current_fps = min(base_fps + (level - 1) * speed_increase_per_level, 30)
    clock.tick(current_fps)

pygame.quit()