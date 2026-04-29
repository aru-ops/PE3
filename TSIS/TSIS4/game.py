# game.py - Core game logic for Snake Game (TSIS 4)
# Handles snake movement, food, power-ups, obstacles, collisions, and level progression

import pygame
import random
from config import (
    WIDTH, HEIGHT, BLOCK_SIZE, BASE_SPEED,
    C_BG, C_GRID, C_FOOD_NORMAL, C_FOOD_WEIGHTED, C_POISON,
    C_OBSTACLE, C_PW_SPEED, C_PW_SLOW, C_PW_SHIELD
)

def run_game(screen, settings, personal_best):
    """
    Main game loop for one playing session.
    Returns (final_score, final_level) when the game ends.
    """
    clock = pygame.time.Clock()                 # for controlling frame rate
    font = pygame.font.SysFont(None, 36)        # default font for UI text

    # --- Initial snake setup (three segments horizontal) ---
    snake = [
        [WIDTH//2, HEIGHT//2],                 # head at center
        [WIDTH//2 - BLOCK_SIZE, HEIGHT//2],    # body segment left of head
        [WIDTH//2 - 2*BLOCK_SIZE, HEIGHT//2]   # body segment two left
    ]
    dx, dy = BLOCK_SIZE, 0                     # initial direction: right
    snake_color = tuple(settings["snake_color"]) # color from settings

    # Game progression variables
    score = 0
    level = 1
    food_eaten_this_level = 0
    current_speed = BASE_SPEED

    # --- Obstacles (appear from level 3) ---
    obstacles = []

    def generate_obstacles():
        """
        Generate a list of obstacle positions for the current level.
        Obstacles appear starting from level 3, number = level*2.
        They are placed randomly but avoid the snake's starting area.
        """
        obs = []
        if level >= 3:                          # obstacles only from level 3
            num_obs = level * 2                 # more obstacles as level increases
            for _ in range(num_obs):
                while True:
                    ox = random.randrange(0, WIDTH, BLOCK_SIZE)
                    oy = random.randrange(0, HEIGHT, BLOCK_SIZE)
                    # Avoid spawning too close to the snake's head (central area)
                    if not (WIDTH//2 - 100 <= ox <= WIDTH//2 + 100 and HEIGHT//2 - 100 <= oy <= HEIGHT//2 + 100):
                        obs.append([ox, oy])
                        break
        return obs

    obstacles = generate_obstacles()            # initial obstacles for level 1 (none)

    def get_random_pos(avoid=[]):
        """
        Return a random grid position (x,y) that is not occupied by:
        - the snake's body
        - any obstacle
        - any additional positions in the 'avoid' list (e.g., existing food/power-up)
        """
        while True:
            x = random.randrange(0, WIDTH, BLOCK_SIZE)
            y = random.randrange(0, HEIGHT, BLOCK_SIZE)
            pos = [x, y]
            if pos not in snake and pos not in obstacles and pos not in avoid:
                return pos

    # --- Normal food ---
    food = get_random_pos()
    food_type = "normal"           # can be "normal" or "weighted"
    food_timer = 0                 # time when weighted food expires (milliseconds)

    # --- Poison food (dark red) ---
    poison = get_random_pos() if random.random() < 0.3 else None

    # --- Power-ups ---
    powerup = None                 # position of the power-up (or None)
    powerup_type = None            # "speed", "slow", or "shield"
    powerup_spawn_time = 0         # time when it was created (ms)
    active_effect = None           # currently active power-up effect name
    effect_end_time = 0            # time when active effect ends (ms)
    shield_active = False          # flag for shield protection

    running = True
    while running:
        current_time = pygame.time.get_ticks()   # current millisecond count

        # --- Event handling (keyboard, quit) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, None               # user closed the window
            if event.type == pygame.KEYDOWN:
                # Change direction, preventing 180-degree turns
                if event.key == pygame.K_UP and dy == 0:
                    dx, dy = 0, -BLOCK_SIZE
                elif event.key == pygame.K_DOWN and dy == 0:
                    dx, dy = 0, BLOCK_SIZE
                elif event.key == pygame.K_LEFT and dx == 0:
                    dx, dy = -BLOCK_SIZE, 0
                elif event.key == pygame.K_RIGHT and dx == 0:
                    dx, dy = BLOCK_SIZE, 0

        # Calculate new head position after movement
        new_head = [snake[0][0] + dx, snake[0][1] + dy]

        # --- Collision detection ---
        collision = False
        # Wall collision
        if (new_head[0] < 0 or new_head[0] >= WIDTH or
            new_head[1] < 0 or new_head[1] >= HEIGHT):
            collision = True
        # Self collision or obstacle collision
        if new_head in snake or new_head in obstacles:
            collision = True

        if collision:
            if shield_active:                     # shield can save from one collision
                shield_active = False
                active_effect = None
                # Teleport through walls (wrap around) if shield is active
                if new_head[0] < 0:
                    new_head[0] = WIDTH - BLOCK_SIZE
                elif new_head[0] >= WIDTH:
                    new_head[0] = 0
                elif new_head[1] < 0:
                    new_head[1] = HEIGHT - BLOCK_SIZE
                elif new_head[1] >= HEIGHT:
                    new_head[1] = 0
                else:
                    # Collision with self or obstacle does not teleport; skip movement
                    continue
            else:
                running = False                   # game over
                continue

        # Insert new head into snake
        snake.insert(0, new_head)

        # --- Food consumption ---
        if new_head == food:
            if settings["sound"]:
                pass   # optional sound effect (uncomment if you add sound)
            # Add score based on food type
            if food_type == "normal":
                score += 10
            elif food_type == "weighted":
                score += 30

            food_eaten_this_level += 1
            # Level up after eating 3 foods per level
            if food_eaten_this_level >= 3:
                level += 1
                food_eaten_this_level = 0
                obstacles = generate_obstacles()   # regenerate obstacles for new level

            # Spawn new food (sometimes weighted with 5-second timer)
            food = get_random_pos()
            if random.random() < 0.2:
                food_type = "weighted"
                food_timer = current_time + 5000   # disappears after 5 sec
            else:
                food_type = "normal"

            # Sometimes spawn poison food when eating regular food
            if random.random() < 0.3 and poison is None:
                poison = get_random_pos()
        else:
            # Remove tail (snake didn't eat, so move forward without growing)
            snake.pop()

        # --- Poison consumption (shortens snake) ---
        if poison and new_head == poison:
            if settings["sound"]:
                pass
            # Remove two segments from the tail (if possible)
            if len(snake) > 0:
                snake.pop()
            if len(snake) > 0:
                snake.pop()
            poison = None
            # If snake becomes too short (length <= 1), game over
            if len(snake) <= 1:
                running = False
                continue

        # --- Power-up spawning ---
        if powerup is None and random.random() < 0.01:   # 1% chance per frame
            powerup = get_random_pos()
            powerup_type = random.choice(["speed", "slow", "shield"])
            powerup_spawn_time = current_time

        # Remove power-up if not collected after 8 seconds
        if powerup and current_time - powerup_spawn_time > 8000:
            powerup = None

        # Power-up collection
        if powerup and new_head == powerup:
            if settings["sound"]:
                pass
            active_effect = powerup_type
            effect_end_time = current_time + 5000       # effect lasts 5 seconds
            if powerup_type == "shield":
                shield_active = True
            powerup = None

        # Deactivate non-shield effects after their duration ends
        if active_effect and active_effect != "shield" and current_time > effect_end_time:
            active_effect = None

        # Remove weighted food if it expired
        if food_type == "weighted" and current_time > food_timer:
            food = get_random_pos()
            food_type = "normal"

        # --- Game speed calculation ---
        # Base speed increases with level, plus power-up modifiers
        fps = BASE_SPEED + level          # level adds directly to FPS
        if active_effect == "speed":
            fps += 8
        elif active_effect == "slow":
            fps = max(4, fps - 5)

        # --- Drawing everything ---
        screen.fill(C_BG)                 # black background

        # Draw grid overlay if enabled in settings
        if settings["grid_overlay"]:
            for x in range(0, WIDTH, BLOCK_SIZE):
                pygame.draw.line(screen, C_GRID, (x, 0), (x, HEIGHT))
            for y in range(0, HEIGHT, BLOCK_SIZE):
                pygame.draw.line(screen, C_GRID, (0, y), (WIDTH, y))

        # Draw obstacles
        for obs in obstacles:
            pygame.draw.rect(screen, C_OBSTACLE, (obs[0], obs[1], BLOCK_SIZE, BLOCK_SIZE))

        # Draw food (normal or weighted)
        food_color = C_FOOD_WEIGHTED if food_type == "weighted" else C_FOOD_NORMAL
        pygame.draw.rect(screen, food_color, (food[0], food[1], BLOCK_SIZE, BLOCK_SIZE))

        # Draw poison (if present)
        if poison:
            pygame.draw.rect(screen, C_POISON, (poison[0], poison[1], BLOCK_SIZE, BLOCK_SIZE))

        # Draw power-up (if any)
        if powerup:
            if powerup_type == "speed":
                c = C_PW_SPEED
            elif powerup_type == "slow":
                c = C_PW_SLOW
            else:   # shield
                c = C_PW_SHIELD
            pygame.draw.rect(screen, c, (powerup[0], powerup[1], BLOCK_SIZE, BLOCK_SIZE))

        # Draw the snake (head may be highlighted if shield active)
        for i, segment in enumerate(snake):
            c = snake_color
            if shield_active and i == 0:   # head has different color when shielded
                c = C_PW_SHIELD
            pygame.draw.rect(screen, c, (segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE))

        # Draw HUD (score, level, personal best)
        hud_text = font.render(f"Score: {score}  Level: {level}  Best: {personal_best}", True, (255,255,255))
        screen.blit(hud_text, (10, 10))

        # Display active power-up effect
        if active_effect:
            eff_text = font.render(f"Active: {active_effect.upper()}", True, (255,255,0))
            screen.blit(eff_text, (WIDTH - 200, 10))

        pygame.display.flip()               # update the screen
        clock.tick(fps)                     # maintain game speed

    return score, level                     # return final results after game over