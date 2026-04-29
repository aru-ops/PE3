# game.py
import pygame
import random
import time
from settings_manager import load_settings

# Константы (можно взять из вашего snake.py)
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
CELL_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // CELL_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // CELL_SIZE

WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
DARK_GREEN = (0,150,0)
BLUE = (0,0,255)
PURPLE = (128,0,128)
ORANGE = (255,165,0)
YELLOW = (255,255,0)
DARK_RED = (139,0,0)
CYAN = (0,255,255)

# Типы еды
class FoodType:
    NORMAL = 1
    POISON = 2

class PowerUpType:
    SPEED = "speed"
    SLOW = "slow"
    SHIELD = "shield"

class Snake:
    def __init__(self):
        self.body = [(GRID_WIDTH//2, GRID_HEIGHT//2)]
        self.direction = (1,0)
        self.grow_flag = False
        self.color = load_settings().get("snake_color", DARK_GREEN)

    def move(self):
        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        self.body.insert(0, new_head)
        if not self.grow_flag:
            self.body.pop()
        else:
            self.grow_flag = False

    def grow(self):
        self.grow_flag = True

    def check_collision(self, walls=None):
        head = self.body[0]
        # стены
        if head[0] < 0 or head[0] >= GRID_WIDTH or head[1] < 0 or head[1] >= GRID_HEIGHT:
            return True
        # самостолкновение
        if head in self.body[1:]:
            return True
        # препятствия (стены-блоки)
        if walls and head in walls:
            return True
        return False

    def draw(self, screen, grid):
        for i, seg in enumerate(self.body):
            color = self.color if i != 0 else (min(255, self.color[0]+50), min(255, self.color[1]+50), min(255, self.color[2]+50))
            rect = pygame.Rect(seg[0]*CELL_SIZE, seg[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, color, rect)
            if grid:
                pygame.draw.rect(screen, BLACK, rect, 1)

class Food:
    def __init__(self, snake_body, walls, food_type=FoodType.NORMAL):
        self.type = food_type
        self.position = self.generate_position(snake_body, walls)
        self.spawn_time = time.time()
        self.lifetime = 5.0 if food_type == FoodType.NORMAL else 4.0  # poison исчезает быстрее

    def generate_position(self, snake_body, walls):
        while True:
            x = random.randint(0, GRID_WIDTH-1)
            y = random.randint(0, GRID_HEIGHT-1)
            if (x,y) not in snake_body and (x,y) not in walls:
                return (x,y)

    def is_expired(self):
        return time.time() - self.spawn_time > self.lifetime

    def draw(self, screen, grid):
        color = YELLOW if self.type == FoodType.NORMAL else DARK_RED
        rect = pygame.Rect(self.position[0]*CELL_SIZE, self.position[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, color, rect)
        if grid:
            pygame.draw.rect(screen, BLACK, rect, 1)

class PowerUp:
    def __init__(self, snake_body, walls):
        self.type = random.choice([PowerUpType.SPEED, PowerUpType.SLOW, PowerUpType.SHIELD])
        self.position = self.generate_position(snake_body, walls)
        self.spawn_time = time.time()
        self.lifetime = 8.0  # секунд на поле

    def generate_position(self, snake_body, walls):
        while True:
            x = random.randint(0, GRID_WIDTH-1)
            y = random.randint(0, GRID_HEIGHT-1)
            if (x,y) not in snake_body and (x,y) not in walls:
                return (x,y)

    def is_expired(self):
        return time.time() - self.spawn_time > self.lifetime

    def draw(self, screen, grid):
        if self.type == PowerUpType.SPEED:
            color = CYAN
        elif self.type == PowerUpType.SLOW:
            color = PURPLE
        else:  # shield
            color = ORANGE
        rect = pygame.Rect(self.position[0]*CELL_SIZE, self.position[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, color, rect)
        if grid:
            pygame.draw.rect(screen, BLACK, rect, 1)

class Obstacle:
    def __init__(self, pos):
        self.position = pos

    def draw(self, screen, grid):
        rect = pygame.Rect(self.position[0]*CELL_SIZE, self.position[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, (100,100,100), rect)
        if grid:
            pygame.draw.rect(screen, BLACK, rect, 1)

class SnakeGame:
    def __init__(self, screen, username, settings):
        self.screen = screen
        self.username = username
        self.settings = settings
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.snake = Snake()
        self.score = 0
        self.level = 1
        self.foods_eaten = 0
        self.foods_per_level = 3
        self.base_speed = 8
        self.current_speed = self.base_speed
        self.walls = []   # препятствия (позиции)
        self.powerup = None
        self.active_powerup = None
        self.powerup_end_time = 0
        self.shield_active = False
        self.last_move_time = 0
        self.move_delay = 1000 // self.current_speed
        self.game_over = False
        self.personal_best = self.get_personal_best()

        # Создаём еду (обычную и ядовитую)
        self.foods = []
        self.spawn_normal_food()
        self.spawn_poison_food()

        # Уровень: если >=3, генерируем препятствия
        if self.level >= 3:
            self.generate_obstacles(3)  # 3 блока

    def get_personal_best(self):
        from db import get_personal_best
        return get_personal_best(self.username)

    def spawn_normal_food(self):
        self.foods.append(Food(self.snake.body, self.walls, FoodType.NORMAL))

    def spawn_poison_food(self):
        # Вероятность появления яда: 30%
        if random.random() < 0.3 and not any(f.type == FoodType.POISON for f in self.foods):
            self.foods.append(Food(self.snake.body, self.walls, FoodType.POISON))

    def spawn_powerup(self):
        if self.powerup is None and random.random() < 0.02:  # 2% шанс каждый кадр
            self.powerup = PowerUp(self.snake.body, self.walls)

    def generate_obstacles(self, count):
        """Случайно ставит блоки, не блокируя змейку."""
        self.walls = []
        for _ in range(count):
            while True:
                x = random.randint(0, GRID_WIDTH-1)
                y = random.randint(0, GRID_HEIGHT-1)
                if (x,y) not in self.snake.body and (x,y) not in [f.position for f in self.foods] and (x,y) not in self.walls:
                    # Проверка, что змейка может двигаться (хотя бы одна соседняя свободна)
                    self.walls.append((x,y))
                    break

    def handle_collision(self):
        # Проверка столкновения с препятствиями или стенами/собой
        if self.snake.check_collision(self.walls):
            if self.shield_active:
                self.shield_active = False
                # откатить последний ход? проще: убираем щит и не засчитываем смерть
                # но телепортация? реализуем как "игнорирование одного удара"
                # для простоты: при столкновении со стеной или препятствием щит спасает один раз,
                # но змейка не двигается дальше? улучшим: при shield_active не вызываем game_over
                return False
            else:
                self.game_over = True
                return True
        return False

    def update(self):
        if self.game_over:
            return

        now = pygame.time.get_ticks()
        # Управление скоростью (таймер)
        if now - self.last_move_time < self.move_delay:
            return
        self.last_move_time = now

        # Движение змейки
        self.snake.move()

        # Проверка столкновений после движения
        if self.handle_collision():
            return

        # Сбор еды
        head = self.snake.body[0]
        for food in self.foods[:]:
            if head == food.position:
                if food.type == FoodType.NORMAL:
                    self.score += 10
                    self.foods_eaten += 1
                    self.snake.grow()
                elif food.type == FoodType.POISON:
                    # Укорачиваем змейку на 2 сегмента
                    for _ in range(2):
                        if len(self.snake.body) > 1:
                            self.snake.body.pop()
                    if len(self.snake.body) <= 1:
                        self.game_over = True
                        return
                    self.score -= 5  # штраф
                self.foods.remove(food)
                # Спавн новой обычной еды
                self.spawn_normal_food()
                # Спавн яда с вероятностью
                self.spawn_poison_food()

                # Повышение уровня
                if self.foods_eaten % self.foods_per_level == 0:
                    self.level_up()
                break

        # Сбор power-up
        if self.powerup and head == self.powerup.position:
            now_sec = pygame.time.get_ticks() / 1000.0
            if self.powerup.type == PowerUpType.SPEED:
                self.active_powerup = PowerUpType.SPEED
                self.powerup_end_time = now_sec + 5.0
            elif self.powerup.type == PowerUpType.SLOW:
                self.active_powerup = PowerUpType.SLOW
                self.powerup_end_time = now_sec + 5.0
            elif self.powerup.type == PowerUpType.SHIELD:
                self.shield_active = True
                self.active_powerup = None
            self.powerup = None

        # Обновление активных баффов/дебаффов
        self.update_powerups()

        # Удаление просроченной еды
        for food in self.foods[:]:
            if food.is_expired():
                self.foods.remove(food)
                self.spawn_normal_food()  # замена

        # Удаление просроченного power-up
        if self.powerup and self.powerup.is_expired():
            self.powerup = None

        # Спавн нового power-up
        self.spawn_powerup()

        # Обновление скорости игры (влияние power-up)
        self.update_speed()

    def update_powerups(self):
        now = pygame.time.get_ticks() / 1000.0
        if self.active_powerup and now >= self.powerup_end_time:
            self.active_powerup = None

    def update_speed(self):
        base = self.base_speed + (self.level - 1)
        if self.active_powerup == PowerUpType.SPEED:
            self.current_speed = base * 1.5
        elif self.active_powerup == PowerUpType.SLOW:
            self.current_speed = base * 0.7
        else:
            self.current_speed = base
        self.move_delay = int(1000 // self.current_speed)

    def level_up(self):
        self.level += 1
        # При уровне 3+ добавляем препятствия (если их нет)
        if self.level == 3:
            self.generate_obstacles(3)
        elif self.level > 3 and len(self.walls) < 6:
            # Добавляем ещё одно препятствие
            self.generate_obstacles(1)

    def handle_input(self, keys):
        if keys[pygame.K_UP] and self.snake.direction != (0,1):
            self.snake.direction = (0,-1)
        elif keys[pygame.K_DOWN] and self.snake.direction != (0,-1):
            self.snake.direction = (0,1)
        elif keys[pygame.K_LEFT] and self.snake.direction != (1,0):
            self.snake.direction = (-1,0)
        elif keys[pygame.K_RIGHT] and self.snake.direction != (-1,0):
            self.snake.direction = (1,0)

    def draw_grid(self):
        if self.settings["grid"]:
            for x in range(0, SCREEN_WIDTH, CELL_SIZE):
                pygame.draw.line(self.screen, (50,50,50), (x,0), (x,SCREEN_HEIGHT))
            for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
                pygame.draw.line(self.screen, (50,50,50), (0,y), (SCREEN_WIDTH,y))

    def draw(self):
        self.screen.fill(BLACK)
        # Препятствия
        for wall in self.walls:
            rect = pygame.Rect(wall[0]*CELL_SIZE, wall[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, (80,80,80), rect)
        # Еда
        for food in self.foods:
            food.draw(self.screen, self.settings["grid"])
        # Power-up
        if self.powerup:
            self.powerup.draw(self.screen, self.settings["grid"])
        # Змейка
        self.snake.draw(self.screen, self.settings["grid"])
        # Сетка
        self.draw_grid()

        # UI
        font = pygame.font.SysFont("Arial", 24)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        level_text = font.render(f"Level: {self.level}", True, WHITE)
        best_text = font.render(f"Best: {self.personal_best}", True, WHITE)
        self.screen.blit(score_text, (10,10))
        self.screen.blit(level_text, (10,40))
        self.screen.blit(best_text, (10,70))
        if self.active_powerup:
            txt = "SPEED" if self.active_powerup == PowerUpType.SPEED else "SLOW"
            timer = max(0, self.powerup_end_time - (pygame.time.get_ticks()/1000.0))
            power_text = font.render(f"{txt}: {timer:.1f}s", True, CYAN)
            self.screen.blit(power_text, (SCREEN_WIDTH-120, 10))
        if self.shield_active:
            shield_text = font.render("SHIELD", True, ORANGE)
            self.screen.blit(shield_text, (SCREEN_WIDTH-120, 40))

    def run(self):
        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
            keys = pygame.key.get_pressed()
            self.handle_input(keys)
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
        # Сохраняем результат в БД
        from db import save_game_result
        save_game_result(self.username, self.score, self.level)
        return self.score, self.level, self.personal_best