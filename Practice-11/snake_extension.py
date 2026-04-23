# snake_extension.py
import pygame
import random
import sys
import time

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
CELL_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // CELL_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // CELL_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)

class SpecialFood:
    """Food with different weights and timer functionality"""
    class Type:
        LIGHT = 1    # Worth 1 point, stays 5 seconds
        NORMAL = 2   # Worth 2 points, stays 3 seconds
        HEAVY = 3    # Worth 3 points, stays 2 seconds
    
    def __init__(self, x, y, food_type):
        self.x = x
        self.y = y
        self.type = food_type
        self.spawn_time = time.time()
        self.lifetime = {1: 5, 2: 3, 3: 2}[food_type]  # Lifetime in seconds
        
    def is_expired(self):
        """Check if food has disappeared"""
        return time.time() - self.spawn_time > self.lifetime
        
    def draw(self, screen):
        # Different colors for different weights
        if self.type == self.Type.LIGHT:
            color = BLUE
        elif self.type == self.Type.NORMAL:
            color = ORANGE
        else:
            color = PURPLE
            
        # Draw food
        pygame.draw.rect(screen, color, (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        
        # Draw timer indicator (shrinking circle)
        remaining = max(0, self.lifetime - (time.time() - self.spawn_time))
        percentage = remaining / self.lifetime
        radius = int(CELL_SIZE // 2 * percentage)
        pygame.draw.circle(screen, WHITE, 
                          (self.x * CELL_SIZE + CELL_SIZE//2, self.y * CELL_SIZE + CELL_SIZE//2), 
                          radius, 2)

class Snake:
    def __init__(self):
        # Start in the middle of the screen
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        self.body = [(start_x, start_y)]
        self.direction = (1, 0)  # Moving right
        self.grow_flag = False
        
    def move(self):
        """Move snake in current direction"""
        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        self.body.insert(0, new_head)
        
        if not self.grow_flag:
            self.body.pop()
        else:
            self.grow_flag = False
            
    def grow(self):
        """Mark snake to grow on next move"""
        self.grow_flag = True
        
    def check_collision(self):
        """Check if snake collides with walls or itself"""
        head = self.body[0]
        
        # Wall collision
        if head[0] < 0 or head[0] >= GRID_WIDTH or head[1] < 0 or head[1] >= GRID_HEIGHT:
            return True
            
        # Self collision
        if head in self.body[1:]:
            return True
            
        return False
        
    def draw(self, screen):
        for segment in self.body:
            pygame.draw.rect(screen, GREEN, 
                           (segment[0] * CELL_SIZE, segment[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake - Special Food Edition")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.reset_game()
        
    def reset_game(self):
        """Reset game state"""
        self.snake = Snake()
        self.special_foods = []
        self.score = 0
        self.food_spawn_timer = 0
        
    def spawn_special_food(self):
        """Randomly generate food with different weights"""
        # Find empty positions
        occupied = set(self.snake.body)
        occupied.update([(food.x, food.y) for food in self.special_foods])
        
        available_positions = []
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                if (x, y) not in occupied:
                    available_positions.append((x, y))
                    
        if available_positions:
            x, y = random.choice(available_positions)
            # Random weight: 1 (light), 2 (normal), or 3 (heavy)
            weight = random.choice([1, 2, 3])
            self.special_foods.append(SpecialFood(x, y, weight))
            
    def update_foods(self):
        """Update food timers and check expiration"""
        # Remove expired foods
        for food in self.special_foods[:]:
            if food.is_expired():
                self.special_foods.remove(food)
                
        # Check if snake eats any food
        head = self.snake.body[0]
        for food in self.special_foods[:]:
            if (head[0], head[1]) == (food.x, food.y):
                # Add points based on food weight
                self.score += food.type
                self.special_foods.remove(food)
                self.snake.grow()
                
    def run(self):
        running = True
        game_over = False
        frame_count = 0
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                if not game_over and event.type == pygame.KEYDOWN:
                    # Change direction with arrow keys (prevent 180-degree turns)
                    if event.key == pygame.K_UP and self.snake.direction != (0, 1):
                        self.snake.direction = (0, -1)
                    elif event.key == pygame.K_DOWN and self.snake.direction != (0, -1):
                        self.snake.direction = (0, 1)
                    elif event.key == pygame.K_LEFT and self.snake.direction != (1, 0):
                        self.snake.direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and self.snake.direction != (-1, 0):
                        self.snake.direction = (1, 0)
                        
            if not game_over:
                # Spawn food every 60 frames (about 1 second)
                frame_count += 1
                if frame_count % 60 == 0 and len(self.special_foods) < 5:
                    self.spawn_special_food()
                    
                # Update game
                self.snake.move()
                game_over = self.snake.check_collision()
                self.update_foods()
                
                # Drawing
                self.screen.fill(BLACK)
                
                # Draw grid lines
                for x in range(0, SCREEN_WIDTH, CELL_SIZE):
                    pygame.draw.line(self.screen, GRAY, (x, 0), (x, SCREEN_HEIGHT), 1)
                for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
                    pygame.draw.line(self.screen, GRAY, (0, y), (SCREEN_WIDTH, y), 1)
                    
                self.snake.draw(self.screen)
                for food in self.special_foods:
                    food.draw(self.screen)
                    
                # Draw UI
                score_text = self.font.render(f"Score: {self.score}", True, WHITE)
                self.screen.blit(score_text, (10, 10))
                
                # Draw instructions
                inst_text = self.small_font.render("Arrow keys to move", True, WHITE)
                self.screen.blit(inst_text, (10, SCREEN_HEIGHT - 30))
                
            else:
                # Game over screen
                game_over_text = self.font.render("GAME OVER! Press R to restart or ESC to quit", True, RED)
                final_score = self.font.render(f"Final Score: {self.score}", True, WHITE)
                self.screen.blit(game_over_text, (SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT//2 - 50))
                self.screen.blit(final_score, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2))
                
                keys = pygame.key.get_pressed()
                if keys[pygame.K_r]:
                    self.reset_game()
                    game_over = False
                    frame_count = 0
                elif keys[pygame.K_ESCAPE]:
                    running = False
                    
            pygame.display.flip()
            self.clock.tick(10)  # Snake speed (10 FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = SnakeGame()
    game.run()