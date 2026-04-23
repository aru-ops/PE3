# racer_extension.py
import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
LANE_WIDTH = SCREEN_WIDTH // 3
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 80
ENEMY_WIDTH = 50
ENEMY_HEIGHT = 80
COIN_SIZE = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)
ORANGE = (255, 165, 0)

class Coin:
    """Coin with different weights (Light, Normal, Heavy)"""
    class Weight:
        LIGHT = 1    # Worth 1 point, small size
        NORMAL = 2   # Worth 2 points, medium size
        HEAVY = 3    # Worth 3 points, large size
    
    def __init__(self, x, y, weight):
        self.x = x
        self.y = y
        self.weight = weight
        self.size = 20 + (weight - 1) * 5  # Different size based on weight
        self.rect = pygame.Rect(x, y, self.size, self.size)
        
    def draw(self, screen):
        # Different colors based on weight
        if self.weight == self.Weight.LIGHT:
            color = YELLOW
        elif self.weight == self.Weight.NORMAL:
            color = GOLD
        else:
            color = ORANGE
        pygame.draw.circle(screen, color, (self.x + self.size//2, self.y + self.size//2), self.size//2)
        # Draw weight number on coin
        font = pygame.font.Font(None, 20)
        text = font.render(str(self.weight), True, BLACK)
        screen.blit(text, (self.x + self.size//3, self.y + self.size//3))

class Enemy:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.rect = pygame.Rect(x, y, ENEMY_WIDTH, ENEMY_HEIGHT)
        
    def update(self):
        self.y += self.speed
        self.rect.y = self.y
        
    def draw(self, screen):
        pygame.draw.rect(screen, RED, self.rect)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.lane = 1  # 0=left, 1=middle, 2=right
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        
    def move_left(self):
        if self.lane > 0:
            self.lane -= 1
            self.x -= LANE_WIDTH
            
    def move_right(self):
        if self.lane < 2:
            self.lane += 1
            self.x += LANE_WIDTH
            
    def update(self):
        self.rect.x = self.x
        self.rect.y = self.y
        
    def draw(self, screen):
        pygame.draw.rect(screen, BLACK, self.rect)

class RacerGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Racer - Coin Collector")
        self.clock = pygame.time.Clock()
        
        # Game objects
        self.player = Player(SCREEN_WIDTH//2 - PLAYER_WIDTH//2, SCREEN_HEIGHT - 100)
        self.coins = []
        self.enemies = []
        
        # Game stats
        self.score = 0
        self.coins_collected = 0
        self.enemy_speed = 5
        self.enemy_spawn_timer = 0
        self.coin_spawn_timer = 0
        
        # Fonts
        self.font = pygame.font.Font(None, 36)
        
    def spawn_coin(self):
        """Randomly generate coins with different weights"""
        # Random lane (0, 1, 2)
        lane = random.randint(0, 2)
        x = lane * LANE_WIDTH + (LANE_WIDTH//2 - COIN_SIZE//2)
        y = -COIN_SIZE
        
        # Random weight (1, 2, or 3)
        weight = random.choice([Coin.Weight.LIGHT, Coin.Weight.NORMAL, Coin.Weight.HEAVY])
        
        self.coins.append(Coin(x, y, weight))
        
    def spawn_enemy(self):
        """Spawn enemy in random lane"""
        lane = random.randint(0, 2)
        x = lane * LANE_WIDTH + (LANE_WIDTH//2 - ENEMY_WIDTH//2)
        y = -ENEMY_HEIGHT
        self.enemies.append(Enemy(x, y, self.enemy_speed))
        
    def update_coins(self):
        """Update coin positions and check collection"""
        for coin in self.coins[:]:
            coin.y += 3  # Fall speed
            coin.rect.y = coin.y
            
            # Check collision with player
            if self.player.rect.colliderect(coin.rect):
                self.score += coin.weight  # Add weight value to score
                self.coins_collected += 1
                self.coins.remove(coin)
                
                # Increase enemy speed when player earns N coins (every 5 coins)
                if self.coins_collected % 5 == 0:
                    self.enemy_speed += 1
                    print(f"Enemy speed increased to {self.enemy_speed}!")
                    
            # Remove coins that go off screen
            elif coin.y > SCREEN_HEIGHT:
                self.coins.remove(coin)
                
    def update_enemies(self):
        """Update enemy positions and check collisions"""
        for enemy in self.enemies[:]:
            enemy.update()
            
            # Check collision with player
            if self.player.rect.colliderect(enemy.rect):
                return False  # Game over
                
            # Remove enemies off screen
            if enemy.y > SCREEN_HEIGHT:
                self.enemies.remove(enemy)
                
        return True  # Game continues
        
    def run(self):
        running = True
        game_over = False
        frame_count = 0
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                if not game_over:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            self.player.move_left()
                        elif event.key == pygame.K_RIGHT:
                            self.player.move_right()
                            
            if not game_over:
                # Spawn enemies every 60 frames (about 1 second at 60 FPS)
                frame_count += 1
                if frame_count % 60 == 0:
                    self.spawn_enemy()
                    
                # Spawn coins every 30 frames
                if frame_count % 30 == 0:
                    self.spawn_coin()
                    
                # Update game objects
                self.player.update()
                game_over = not self.update_enemies()
                self.update_coins()
                
                # Drawing
                self.screen.fill(WHITE)
                
                # Draw lane lines
                for i in range(1, 3):
                    pygame.draw.line(self.screen, BLACK, (i * LANE_WIDTH, 0), (i * LANE_WIDTH, SCREEN_HEIGHT), 3)
                    
                self.player.draw(self.screen)
                for enemy in self.enemies:
                    enemy.draw(self.screen)
                for coin in self.coins:
                    coin.draw(self.screen)
                    
                # Draw UI
                score_text = self.font.render(f"Score: {self.score}", True, BLACK)
                coins_text = self.font.render(f"Coins: {self.coins_collected}", True, BLACK)
                speed_text = self.font.render(f"Enemy Speed: {self.enemy_speed}", True, BLACK)
                self.screen.blit(score_text, (10, 10))
                self.screen.blit(coins_text, (10, 50))
                self.screen.blit(speed_text, (10, 90))
                
            else:
                # Game over screen
                game_over_text = self.font.render("GAME OVER! Press ESC to quit", True, RED)
                final_score = self.font.render(f"Final Score: {self.score}", True, BLACK)
                self.screen.blit(game_over_text, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 50))
                self.screen.blit(final_score, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2))
                
                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE]:
                    running = False
                    
            pygame.display.flip()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = RacerGame()
    game.run()