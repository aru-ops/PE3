# main.py - Main game loop for Racer (TSIS 3)
# Handles menus, game states, spawning, collisions, and UI

import pygame
import sys
import os
from persistence import load_settings, save_settings, load_leaderboard, save_score
from ui import Button, TextInput
from racer import Player, Enemy, Obstacle, PowerUp, Coin, SPEED_BASE

# Change working directory to the script's location to ensure assets are found
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Initialize Pygame and its mixer for sound
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 600, 600                       # game window size
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS 3: Racer")
clock = pygame.time.Clock()                    # for controlling frame rate
font = pygame.font.Font(None, 36)              # default font for UI

# Load saved settings (sound, car color, difficulty)
settings = load_settings()

# Helper to load a sound file (returns None if not found)
def load_sound(name):
    path = os.path.join('assets', 'sounds', name)
    try:
        return pygame.mixer.Sound(path)
    except (FileNotFoundError, pygame.error):
        return None

# Create sound objects for crashes, power-ups, and coins
snd_crash = load_sound('crash.wav')
snd_powerup = load_sound('powerup.wav')
snd_coin = load_sound('coin.wav')
# Try to load background music
music_loaded = False
try:
    pygame.mixer.music.load(os.path.join('assets', 'sounds', 'bg_music.mp3'))
    music_loaded = True
except:
    pass

# Game state variables
state = "MENU"                      # MENU, NAME_INPUT, PLAY, SETTINGS, LEADERBOARD, GAMEOVER
player_name = "Player"
score = 0
distance = 0
coins_collected = 0
enemy_speed_boost = 0               # extra speed for enemies based on coins collected

# Sprite groups for efficient collision detection and drawing
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
powerups = pygame.sprite.Group()
coins = pygame.sprite.Group()
player = None

def reset_game():
    """Reset all game variables and clear all sprites for a new game."""
    global player, score, distance, coins_collected, enemy_speed_boost
    global all_sprites, enemies, obstacles, powerups, coins
    all_sprites.empty()              # remove all existing sprites
    enemies.empty()
    obstacles.empty()
    powerups.empty()
    coins.empty()
    player = Player(settings["car_color"])   # create new player car
    all_sprites.add(player)                  # add player to main group
    score = 0
    distance = 0
    coins_collected = 0
    enemy_speed_boost = 0
    if music_loaded and settings["sound"]:
        pygame.mixer.music.play(-1)          # loop background music

def draw_hud():
    """Draw heads-up display: score, distance, coins, active power‑ups."""
    screen.blit(font.render(f"Score: {int(score)}", True, (255,255,255)), (10, 10))
    screen.blit(font.render(f"Dist: {int(distance)}m", True, (255,255,255)), (10, 40))
    screen.blit(font.render(f"Coins: {coins_collected}", True, (255,215,0)), (10, 70))
    if player and player.nitro_active:
        time_left = (player.powerup_timer - pygame.time.get_ticks()) // 1000
        screen.blit(font.render(f"NITRO: {max(0, time_left)}s", True, (0,255,255)), (10, 110))
    if player and player.shield_active:
        screen.blit(font.render("SHIELD ACTIVE", True, (255,215,0)), (10, 110))

# Create UI buttons (x, y, width, height, text)
btn_play = Button(200, 150, 200, 50, "Play")
btn_board = Button(200, 220, 200, 50, "Leaderboard")
btn_settings = Button(200, 290, 200, 50, "Settings")
btn_quit = Button(200, 360, 200, 50, "Quit")

# Settings screen buttons
btn_easy = Button(200, 150, 200, 50, "Easy")
btn_normal = Button(200, 220, 200, 50, "Normal")
btn_hard = Button(200, 290, 200, 50, "Hard")
btn_back = Button(200, 500, 200, 50, "Back")
btn_retry = Button(200, 350, 200, 50, "Retry")
btn_menu = Button(200, 420, 200, 50, "Main Menu")
name_input = TextInput(200, 250, 200, 40)      # text input for player name

# Custom events for timed spawns
SPAWN_ENEMY = pygame.USEREVENT + 1
SPAWN_OBSTACLE = pygame.USEREVENT + 2
SPAWN_POWERUP = pygame.USEREVENT + 3
SPAWN_COIN = pygame.USEREVENT + 4
# Set timers (in milliseconds)
pygame.time.set_timer(SPAWN_ENEMY, 1500)       # every 1.5 sec
pygame.time.set_timer(SPAWN_OBSTACLE, 2500)    # every 2.5 sec
pygame.time.set_timer(SPAWN_POWERUP, 6000)     # every 6 sec
pygame.time.set_timer(SPAWN_COIN, 800)         # every 0.8 sec

# ---- Main game loop ----
running = True
while running:
    # --- Draw static background (grass and road) ---
    screen.fill((50, 150, 50))                           # green grass
    pygame.draw.rect(screen, (40, 40, 40), (150, 0, 300, 600))   # asphalt road
    # Animated road lines (move with distance)
    for y in range(0, 600, 40):
        pygame.draw.rect(screen, (255, 255, 255), (245, (y + int(distance * 10)) % 600, 10, 20))
        pygame.draw.rect(screen, (255, 255, 255), (345, (y + int(distance * 10)) % 600, 10, 20))

    # --- Process events (keyboard, mouse, timers) ---
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

        # ----- Main Menu state -----
        if state == "MENU":
            if btn_play.is_clicked(event):
                state = "NAME_INPUT"
            if btn_board.is_clicked(event):
                state = "LEADERBOARD"
            if btn_settings.is_clicked(event):
                state = "SETTINGS"
            if btn_quit.is_clicked(event):
                running = False

        # ----- Settings state -----
        elif state == "SETTINGS":
            if btn_back.is_clicked(event):
                state = "MENU"
            if btn_easy.is_clicked(event):
                settings["difficulty"] = "easy"
                save_settings(settings)
            if btn_normal.is_clicked(event):
                settings["difficulty"] = "normal"
                save_settings(settings)
            if btn_hard.is_clicked(event):
                settings["difficulty"] = "hard"
                save_settings(settings)

        # ----- Name input state -----
        elif state == "NAME_INPUT":
            name_input.handle_event(event)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                player_name = name_input.text if name_input.text else "Player"
                reset_game()
                state = "PLAY"

        # ----- Playing state -----
        elif state == "PLAY":
            # Spawn enemies (traffic cars)
            if event.type == SPAWN_ENEMY:
                e = Enemy(settings["difficulty"], enemy_speed_boost)
                # Avoid spawning on top of existing enemies or obstacles
                if not pygame.sprite.spritecollideany(e, enemies) and not pygame.sprite.spritecollideany(e, obstacles):
                    all_sprites.add(e)
                    enemies.add(e)
            # Spawn obstacles (barriers, oil spills)
            if event.type == SPAWN_OBSTACLE:
                o = Obstacle()
                if not pygame.sprite.spritecollideany(o, enemies) and not pygame.sprite.spritecollideany(o, obstacles):
                    all_sprites.add(o)
                    obstacles.add(o)
            # Spawn power-ups (Nitro, Shield, Repair)
            if event.type == SPAWN_POWERUP:
                p = PowerUp()
                if not pygame.sprite.spritecollideany(p, enemies) and not pygame.sprite.spritecollideany(p, obstacles):
                    all_sprites.add(p)
                    powerups.add(p)
            # Spawn coins (weighted values)
            if event.type == SPAWN_COIN:
                c = Coin()
                if (not pygame.sprite.spritecollideany(c, enemies) and
                    not pygame.sprite.spritecollideany(c, obstacles) and
                    not pygame.sprite.spritecollideany(c, powerups)):
                    all_sprites.add(c)
                    coins.add(c)

        # ----- Leaderboard state -----
        elif state == "LEADERBOARD":
            if btn_back.is_clicked(event):
                state = "MENU"

        # ----- Game Over state -----
        elif state == "GAMEOVER":
            if btn_retry.is_clicked(event):
                reset_game()
                state = "PLAY"
            if btn_menu.is_clicked(event):
                state = "MENU"

    # ----- Update game logic based on current state -----
    if state == "MENU":
        btn_play.draw(screen)
        btn_board.draw(screen)
        btn_settings.draw(screen)
        btn_quit.draw(screen)

    elif state == "SETTINGS":
        screen.fill((40, 40, 40))
        title = font.render("Difficulty Settings", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        curr_diff = font.render(f"Current: {settings['difficulty'].upper()}", True, (0, 255, 0))
        screen.blit(curr_diff, (WIDTH//2 - curr_diff.get_width()//2, 380))
        btn_easy.draw(screen)
        btn_normal.draw(screen)
        btn_hard.draw(screen)
        btn_back.draw(screen)

    elif state == "NAME_INPUT":
        screen.blit(font.render("Enter Name & Press Enter:", True, (255,255,255)), (150, 200))
        name_input.draw(screen)

    elif state == "PLAY":
        # Update all moving sprites (cars move downwards)
        all_sprites.update()

        # Increase enemy speed based on collected coins (every 5 coins = +1 speed)
        new_boost = coins_collected // 5
        if new_boost != enemy_speed_boost:
            enemy_speed_boost = new_boost
            diff = settings["difficulty"]
            for e in enemies:
                if diff == "easy":
                    base = SPEED_BASE - 2
                elif diff == "normal":
                    base = SPEED_BASE
                else:   # hard
                    base = SPEED_BASE + 2
                base = max(2, base)
                e.speed = base + enemy_speed_boost

        # Progress distance and score over time
        distance += 0.1 + (enemy_speed_boost * 0.02)
        score += 0.2 if not player.nitro_active else 0.5   # score increases faster with nitro

        # Handle coin collection
        coin_hits = pygame.sprite.spritecollide(player, coins, True)   # remove collected coin
        for coin in coin_hits:
            if settings["sound"] and snd_coin:
                snd_coin.play()
            coins_collected += 1
            score += coin.weight * 10       # weighted coin value (10/20/50 points)

        # Collision with enemies or obstacles (only if shield is not active)
        if not player.shield_active:
            if pygame.sprite.spritecollideany(player, enemies) or pygame.sprite.spritecollideany(player, obstacles):
                if settings["sound"] and snd_crash:
                    snd_crash.play()
                if player.crashes_allowed > 0:
                    player.crashes_allowed -= 1
                    player.shield_active = True
                    player.powerup_timer = pygame.time.get_ticks() + 2000
                else:
                    pygame.mixer.music.stop()
                    save_score(player_name, int(score), int(distance))   # save to leaderboard
                    state = "GAMEOVER"

        # Power-up collection
        hits = pygame.sprite.spritecollide(player, powerups, True)   # remove collected power-up
        for hit in hits:
            if settings["sound"] and snd_powerup:
                snd_powerup.play()
            if hit.type == "Nitro":
                player.nitro_active, player.shield_active = True, False
                player.powerup_timer = pygame.time.get_ticks() + 4000
            elif hit.type == "Shield":
                player.shield_active, player.nitro_active = True, False
                player.powerup_timer = pygame.time.get_ticks() + 4000
            elif hit.type == "Repair":
                player.crashes_allowed = 1

        # Draw all sprites and HUD
        all_sprites.draw(screen)
        draw_hud()

    elif state == "LEADERBOARD":
        screen.fill((30, 30, 30))
        board = load_leaderboard()                      # get top 10 scores
        for i, entry in enumerate(board):
            txt = f"{i+1}. {entry['name']} - {entry['score']} pts"
            screen.blit(font.render(txt, True, (255,255,255)), (150, 50 + i*35))
        btn_back.draw(screen)

    elif state == "GAMEOVER":
        screen.fill((0, 0, 0))
        screen.blit(font.render(f"GAME OVER! Score: {int(score)}", True, (255, 0, 0)), (180, 200))
        btn_retry.draw(screen)
        btn_menu.draw(screen)

    # Update display and maintain 60 FPS
    pygame.display.flip()
    clock.tick(60)

# Quit game properly
pygame.quit()
sys.exit()