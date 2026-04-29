# racer.py
import pygame
import random
import math
from persistence import load_settings, add_score

# Инициализация pygame (уже в main.py, но для автономности импортируем)
pygame.init()

# Константы экрана
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
LANE_COUNT = 3
LANE_WIDTH = SCREEN_WIDTH // LANE_COUNT
LANE_POSITIONS = [LANE_WIDTH//2, LANE_WIDTH + LANE_WIDTH//2, 2*LANE_WIDTH + LANE_WIDTH//2]

# Цвета
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
ORANGE = (255,165,0)
PURPLE = (128,0,128)
GRAY = (128,128,128)

# Типы препятствий
OBSTACLE_OIL = 0
OBSTACLE_BARRIER = 1
OBSTACLE_POTHOLE = 2

class Player:
    def __init__(self, color="green"):
        self.x = SCREEN_WIDTH//2
        self.y = SCREEN_HEIGHT - 80
        self.width = 40
        self.height = 70
        self.lane = 1  # 0,1,2
        self.color = color
        self.rect = pygame.Rect(self.x - self.width//2, self.y, self.width, self.height)
        self.speed = 5  # базовая скорость движения по полосам (пикселей за нажатие)
        self.shield_active = False
        self.nitro_active = False
        self.nitro_end_time = 0

    def set_lane(self, lane):
        if 0 <= lane < LANE_COUNT:
            self.lane = lane
            self.x = LANE_POSITIONS[lane]
            self.update_rect()

    def update_rect(self):
        self.rect.centerx = self.x
        self.rect.y = self.y

    def draw(self, screen):
        # Используем цвет из настроек
        car_color = GREEN if self.color == "green" else RED if self.color == "red" else BLUE
        pygame.draw.rect(screen, car_color, self.rect)
        if self.shield_active:
            pygame.draw.circle(screen, (0,255,255), self.rect.center, self.width//2+5, 2)

    def get_speed_multiplier(self, current_time):
        if self.nitro_active and current_time < self.nitro_end_time:
            return 1.5
        return 1.0

class Enemy:
    def __init__(self, lane, speed):
        self.lane = lane
        self.x = LANE_POSITIONS[lane]
        self.y = -80
        self.width = 40
        self.height = 70
        self.speed = speed
        self.rect = pygame.Rect(self.x - self.width//2, self.y, self.width, self.height)

    def update(self):
        self.y += self.speed
        self.rect.y = self.y

    def draw(self, screen):
        pygame.draw.rect(screen, RED, self.rect)

class Coin:
    def __init__(self, lane, weight):
        self.lane = lane
        self.x = LANE_POSITIONS[lane]
        self.y = -20
        self.weight = weight
        self.size = 20 + (weight-1)*5
        self.rect = pygame.Rect(self.x - self.size//2, self.y, self.size, self.size)

    def update(self):
        self.y += 4
        self.rect.y = self.y

    def draw(self, screen):
        color = YELLOW if self.weight == 1 else ORANGE if self.weight == 2 else PURPLE
        pygame.draw.circle(screen, color, (self.x, self.y + self.size//2), self.size//2)
        # отображаем вес
        font = pygame.font.SysFont("Arial", 12)
        text = font.render(str(self.weight), True, BLACK)
        screen.blit(text, (self.x-5, self.y+self.size//2-7))

class Obstacle:
    """Препятствие на дороге (например, масло, барьер, яма)."""
    def __init__(self, lane, obstacle_type, y=-50):
        self.lane = lane
        self.type = obstacle_type
        self.x = LANE_POSITIONS[lane]
        self.y = y
        self.width = 30
        self.height = 30
        self.rect = pygame.Rect(self.x - self.width//2, self.y, self.width, self.height)
        self.speed = 4

    def update(self):
        self.y += self.speed
        self.rect.y = self.y

    def draw(self, screen):
        if self.type == OBSTACLE_OIL:
            pygame.draw.circle(screen, (50,50,50), (self.x, self.y+15), 15)
            pygame.draw.circle(screen, (80,80,80), (self.x, self.y+15), 12)
        elif self.type == OBSTACLE_BARRIER:
            pygame.draw.rect(screen, (100,50,0), self.rect)
        elif self.type == OBSTACLE_POTHOLE:
            pygame.draw.circle(screen, (100,100,100), (self.x, self.y+15), 12)
            pygame.draw.circle(screen, (50,50,50), (self.x, self.y+15), 8)

class PowerUp:
    TYPES = ["nitro", "shield", "repair"]
    def __init__(self, lane, y=-40):
        self.lane = lane
        self.x = LANE_POSITIONS[lane]
        self.y = y
        self.type = random.choice(self.TYPES)
        self.size = 25
        self.rect = pygame.Rect(self.x - self.size//2, self.y, self.size, self.size)
        self.speed = 4
        self.lifetime = 180  # кадров до исчезновения

    def update(self):
        self.y += self.speed
        self.rect.y = self.y
        self.lifetime -= 1

    def draw(self, screen):
        if self.type == "nitro":
            color = (255, 100, 0)
            text = "N"
        elif self.type == "shield":
            color = (0, 200, 255)
            text = "S"
        else:
            color = (0, 255, 100)
            text = "R"
        pygame.draw.circle(screen, color, (self.x, self.y+self.size//2), self.size//2)
        font = pygame.font.SysFont("Arial", 14)
        label = font.render(text, True, BLACK)
        screen.blit(label, (self.x-7, self.y+self.size//2-7))

    def is_expired(self):
        return self.lifetime <= 0

class Game:
    def __init__(self, screen, player_name):
        self.screen = screen
        self.player_name = player_name
        self.clock = pygame.time.Clock()
        self.settings = load_settings()
        self.apply_difficulty()
        self.reset_game()

    def apply_difficulty(self):
        diff = self.settings["difficulty"]
        if diff == "easy":
            self.enemy_base_speed = 3
            self.obstacle_spawn_rate = 0.01
            self.powerup_spawn_rate = 0.005
        elif diff == "normal":
            self.enemy_base_speed = 5
            self.obstacle_spawn_rate = 0.02
            self.powerup_spawn_rate = 0.008
        else:  # hard
            self.enemy_base_speed = 7
            self.obstacle_spawn_rate = 0.03
            self.powerup_spawn_rate = 0.01

    def reset_game(self):
        self.player = Player(color=self.settings["car_color"])
        self.enemies = []
        self.coins = []
        self.obstacles = []
        self.powerups = []
        self.score = 0
        self.distance = 0  # метры (условные)
        self.coins_collected = 0
        self.frame = 0
        self.enemy_speed = self.enemy_base_speed
        self.game_over = False
        self.clock = pygame.time.Clock()
        self.active_powerup = None
        self.powerup_end_time = 0

    def spawn_enemy(self):
        lane = random.randint(0, LANE_COUNT-1)
        self.enemies.append(Enemy(lane, self.enemy_speed))

    def spawn_coin(self):
        lane = random.randint(0, LANE_COUNT-1)
        # вес с вероятностью
        r = random.random()
        if r < 0.5:
            weight = 1
        elif r < 0.8:
            weight = 2
        else:
            weight = 3
        self.coins.append(Coin(lane, weight))

    def spawn_obstacle(self):
        lane = random.randint(0, LANE_COUNT-1)
        obs_type = random.choice([OBSTACLE_OIL, OBSTACLE_BARRIER, OBSTACLE_POTHOLE])
        self.obstacles.append(Obstacle(lane, obs_type))

    def spawn_powerup(self):
        lane = random.randint(0, LANE_COUNT-1)
        self.powerups.append(PowerUp(lane))

    def update(self):
        if self.game_over:
            return

        self.frame += 1
        # Увеличение сложности со временем
        if self.frame % 600 == 0:  # каждые ~10 секунд при 60 fps
            self.enemy_speed = min(self.enemy_speed + 0.5, 12)

        # Спавн врагов, монет, препятствий, бонусов
        if random.random() < 0.02:
            self.spawn_enemy()
        if random.random() < 0.05:
            self.spawn_coin()
        if random.random() < self.obstacle_spawn_rate:
            self.spawn_obstacle()
        if random.random() < self.powerup_spawn_rate:
            self.spawn_powerup()

        # Обновление позиций
        for e in self.enemies[:]:
            e.update()
            if e.y > SCREEN_HEIGHT:
                self.enemies.remove(e)
        for c in self.coins[:]:
            c.update()
            if c.y > SCREEN_HEIGHT:
                self.coins.remove(c)
        for o in self.obstacles[:]:
            o.update()
            if o.y > SCREEN_HEIGHT:
                self.obstacles.remove(o)
        for p in self.powerups[:]:
            p.update()
            if p.is_expired() or p.y > SCREEN_HEIGHT:
                self.powerups.remove(p)

        # Проверка столкновений с врагами (если нет щита)
        for e in self.enemies:
            if self.player.rect.colliderect(e.rect):
                if self.player.shield_active:
                    self.player.shield_active = False
                    self.enemies.remove(e)
                else:
                    self.game_over = True
                    # Сохраняем результат
                    add_score(self.player_name, int(self.score), int(self.distance))
                    return

        # Проверка сбора монет
        for c in self.coins[:]:
            if self.player.rect.colliderect(c.rect):
                self.score += c.weight * 10
                self.coins_collected += 1
                self.coins.remove(c)

        # Проверка препятствий (снижают счёт или замедляют)
        for o in self.obstacles[:]:
            if self.player.rect.colliderect(o.rect):
                if o.type == OBSTACLE_OIL:
                    # замедление на секунду
                    self.enemy_speed = max(2, self.enemy_speed - 1)
                elif o.type == OBSTACLE_BARRIER:
                    self.score -= 50
                elif o.type == OBSTACLE_POTHOLE:
                    self.score -= 20
                self.obstacles.remove(o)

        # Проверка бонусов
        for p in self.powerups[:]:
            if self.player.rect.colliderect(p.rect):
                now = pygame.time.get_ticks() / 1000.0
                if p.type == "nitro":
                    self.player.nitro_active = True
                    self.player.nitro_end_time = now + 4.0
                elif p.type == "shield":
                    self.player.shield_active = True
                elif p.type == "repair":
                    # восстановление: убираем одно препятствие или даём бонус к очкам
                    if len(self.obstacles) > 0:
                        self.obstacles.pop()
                    else:
                        self.score += 100
                self.powerups.remove(p)

        # Обновление счёта за дистанцию (каждый кадр)
        self.distance += 0.1
        self.score += 0.5  # за проезд

        # Если активен нитро, увеличиваем скорость врагов? не обязательно, просто разгон игрока
        now = pygame.time.get_ticks() / 1000.0
        if self.player.nitro_active and now >= self.player.nitro_end_time:
            self.player.nitro_active = False

        # Активный бонус (для отображения)
        if self.player.shield_active:
            self.active_powerup = "SHIELD"
            self.powerup_end_time = 0
        elif self.player.nitro_active:
            self.active_powerup = "NITRO"
            self.powerup_end_time = self.player.nitro_end_time
        else:
            self.active_powerup = None

    def handle_input(self, keys):
        if not self.game_over and keys[pygame.K_LEFT]:
            self.player.set_lane(self.player.lane - 1)
        if not self.game_over and keys[pygame.K_RIGHT]:
            self.player.set_lane(self.player.lane + 1)

    def draw(self):
        self.screen.fill((30,30,30))
        # Рисуем полосы движения
        for i in range(1, LANE_COUNT):
            x = i * LANE_WIDTH
            pygame.draw.line(self.screen, WHITE, (x, 0), (x, SCREEN_HEIGHT), 2)

        # Игрок
        self.player.draw(self.screen)
        # Враги
        for e in self.enemies:
            e.draw(self.screen)
        # Монеты
        for c in self.coins:
            c.draw(self.screen)
        # Препятствия
        for o in self.obstacles:
            o.draw(self.screen)
        # Бонусы
        for p in self.powerups:
            p.draw(self.screen)

        # UI
        font = pygame.font.SysFont("Arial", 24)
        score_text = font.render(f"Score: {int(self.score)}", True, WHITE)
        dist_text = font.render(f"Distance: {int(self.distance)}m", True, WHITE)
        coin_text = font.render(f"Coins: {self.coins_collected}", True, YELLOW)
        self.screen.blit(score_text, (10,10))
        self.screen.blit(dist_text, (10,40))
        self.screen.blit(coin_text, (10,70))

        # Отображение активного бонуса
        if self.active_powerup:
            if self.active_powerup == "SHIELD":
                text = "SHIELD ACTIVE"
            else:
                remaining = max(0, self.powerup_end_time - (pygame.time.get_ticks()/1000.0))
                text = f"NITRO {remaining:.1f}s"
            power_text = font.render(text, True, (0,255,255))
            self.screen.blit(power_text, (SCREEN_WIDTH - 150, 10))

        # Сообщение при game over
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0,0))
            go_font = pygame.font.SysFont("Arial", 48)
            text = go_font.render("GAME OVER", True, RED)
            self.screen.blit(text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 50))

    def run(self):
        """Основной игровой цикл (вызывается один раз за игру)."""
        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            keys = pygame.key.get_pressed()
            self.handle_input(keys)
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
        # Игра закончена – возвращаем результат
        return self.score, self.distance, self.coins_collected