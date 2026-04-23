import pygame
import random

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

# --- Food Class ---
class Food:
    def __init__(self, snake_body):
        self.position = self.generate_random_position(snake_body)

    def generate_random_position(self, snake_body):
        """Generate a random position that is not occupied by the snake."""
        while True:
            x = random.randint(0, (SCREEN_WIDTH // CELL_SIZE) - 1) * CELL_SIZE
            y = random.randint(0, (SCREEN_HEIGHT // CELL_SIZE) - 1) * CELL_SIZE
            if (x, y) not in snake_body:
                return (x, y)

    def draw(self, screen):
        """Draw the food on the screen."""
        pygame.draw.rect(screen, RED,
                       (self.position[0], self.position[1], CELL_SIZE, CELL_SIZE))

# --- Game Setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()

# --- Game Variables ---
snake = Snake()
food = Food(snake.body)
score = 0
level = 1
foods_for_next_level = 3  # Foods needed to advance to the next level
foods_eaten = 0

# Font for UI
font = pygame.font.SysFont("Arial", 24)

def draw_text(text, color, x, y):
    """Helper function to draw text on the screen."""
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def show_game_over():
    """Display a game over message and wait for user input."""
    game_over_text = font.render("Game Over! Press R to restart or Q to quit", True, WHITE)
    screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2))
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True  # Restart game
                if event.key == pygame.K_q:
                    return False # Quit game
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

    # Check if snake eats food
    if snake.body[0] == food.position:
        snake.grow()
        score += 10
        foods_eaten += 1
        food = Food(snake.body)  # Generate new food

        # Level up logic: every 3 foods, increase level and speed
        if foods_eaten % foods_for_next_level == 0:
            level += 1
            # Increase game speed (FPS) by 2 each level, up to a maximum of 30
            current_fps = clock.get_fps()
            new_fps = min(10 + (level - 1) * 2, 30)
            # Actually, we control speed via clock.tick(), so we'll adjust FPS
            # We'll store base_fps and update it
            # For simplicity, we directly set FPS variable
            # Let's store FPS in a variable
            pass # We'll handle FPS outside the loop

    # Check for collisions (Game Over)
    if snake.check_collision():
        # Show game over message and ask to restart or quit
        if show_game_over():
            # Restart the game
            snake = Snake()
            food = Food(snake.body)
            score = 0
            level = 1
            foods_eaten = 0
            continue
        else:
            running = False

    # --- Drawing ---
    screen.fill(BLACK)  # Clear screen

    # Draw snake
    snake.draw(screen)

    # Draw food
    food.draw(screen)

    # Draw UI (Score and Level)
    draw_text(f"Score: {score}", WHITE, 10, 10)
    draw_text(f"Level: {level}", WHITE, SCREEN_WIDTH - 100, 10)

    # Update display
    pygame.display.update()

    # Control game speed (increase with level)
    base_fps = 10
    speed_increase_per_level = 2
    current_fps = min(base_fps + (level - 1) * speed_increase_per_level, 30)
    clock.tick(current_fps)

pygame.quit()