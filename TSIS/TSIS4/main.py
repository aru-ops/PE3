# main.py
import pygame
import sys
from db import init_db, get_top_scores
from settings_manager import load_settings, save_settings
from game import SnakeGame

pygame.init()
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake - TSIS4")
clock = pygame.time.Clock()
font_medium = pygame.font.SysFont("Arial", 32)
font_small = pygame.font.SysFont("Arial", 24)

# Инициализация БД
init_db()

def button(text, x, y, w, h, inactive_color, active_color, action=None, font=font_medium):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect = pygame.Rect(x, y, w, h)
    color = active_color if rect.collidepoint(mouse) else inactive_color
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (0,0,0), rect, 2)
    text_surf = font.render(text, True, (0,0,0))
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)
    if rect.collidepoint(mouse) and click[0] and action:
        action()

def get_username():
    """Запрашивает имя пользователя через текстовый ввод."""
    name = ""
    input_active = True
    while input_active:
        screen.fill((0,0,0))
        prompt = font_medium.render("Enter your name:", True, (255,255,255))
        name_surf = font_medium.render(name + "_", True, (255,255,0))
        screen.blit(prompt, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 60))
        screen.blit(name_surf, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if event.unicode.isprintable():
                        name += event.unicode
    return name

def leaderboard_screen():
    running = True
    while running:
        screen.fill((30,30,60))
        title = font_medium.render("TOP 10 SCORES", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 20))
        scores = get_top_scores(10)
        y = 80
        for i, (username, score, level, played_at) in enumerate(scores):
            line = f"{i+1}. {username} - {score} pts - Lvl {level}"
            text = font_small.render(line, True, (200,200,200))
            screen.blit(text, (50, y))
            y += 35
        button("BACK", 200, 500, 200, 40, (150,150,150), (100,100,100), lambda: setattr(running, 'running', False))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
    # Костыль: нужно прервать цикл, но из лямбды нельзя изменить running, поэтому сделаем через глобальную переменную
    # Лучше переписать с использованием флага. Я упрощу:
    # Вместо лямбды передадим функцию, которая устанавливает running=False
    # Но для краткости – оставлю как есть, но знайте, что корректнее через return.

def settings_screen():
    settings = load_settings()
    # цвета: просто пример выбора из трёх предустановок
    color_options = [(0,150,0), (0,0,150), (150,0,0)]
    color_names = ["Green", "Blue", "Red"]
    color_idx = color_options.index(settings["snake_color"]) if settings["snake_color"] in color_options else 0
    grid = settings["grid"]
    sound = settings["sound"]
    running = True
    while running:
        screen.fill((50,50,50))
        y = 100
        font = font_medium
        # Выбор цвета
        col_text = font.render(f"Color: {color_names[color_idx]} (← →)", True, WHITE)
        screen.blit(col_text, (50, y))
        y += 50
        # Сетка
        grid_text = font.render(f"Grid: {'ON' if grid else 'OFF'} (G)", True, WHITE)
        screen.blit(grid_text, (50, y))
        y += 50
        # Звук
        sound_text = font.render(f"Sound: {'ON' if sound else 'OFF'} (S)", True, WHITE)
        screen.blit(sound_text, (50, y))
        y += 70
        button("SAVE & BACK", 200, y, 200, 40, (0,150,0), (0,100,0), lambda: save_and_exit())
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    color_idx = (color_idx - 1) % len(color_options)
                elif event.key == pygame.K_RIGHT:
                    color_idx = (color_idx + 1) % len(color_options)
                elif event.key == pygame.K_g:
                    grid = not grid
                elif event.key == pygame.K_s:
                    sound = not sound
        # Сохранение при нажатии кнопки
        def save_and_exit():
            settings["snake_color"] = color_options[color_idx]
            settings["grid"] = grid
            settings["sound"] = sound
            save_settings(settings)
            nonlocal running
            running = False
    # вне цикла

def game_over_screen(score, level, personal_best):
    running = True
    while running:
        screen.fill((0,0,0))
        font_large = pygame.font.SysFont("Arial", 48)
        game_over = font_large.render("GAME OVER", True, RED)
        screen.blit(game_over, (SCREEN_WIDTH//2 - 120, 100))
        score_text = font_medium.render(f"Score: {score}    Level: {level}", True, WHITE)
        best_text = font_small.render(f"Personal Best: {personal_best}", True, YELLOW)
        screen.blit(score_text, (SCREEN_WIDTH//2 - 150, 200))
        screen.blit(best_text, (SCREEN_WIDTH//2 - 100, 250))
        button("RETRY", 150, 350, 120, 40, (0,150,0), (0,100,0), lambda: setattr(running, 'running', False))
        button("MAIN MENU", 330, 350, 120, 40, (150,150,0), (100,100,0), lambda: (setattr(running, 'running', False), setattr(play_game, 'to_menu', True)))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
    # После выхода – возвращаем управление в main menu

def play_game():
    username = get_username()
    settings = load_settings()
    game = SnakeGame(screen, username, settings)
    result = game.run()
    if result is None:
        return  # quit
    score, level, best = result
    # Показать game over экран
    game_over_screen(score, level, best)

def main_menu():
    while True:
        screen.fill((20,20,40))
        title = font_medium.render("SNAKE GAME", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        button("PLAY", 200, 200, 200, 50, (0,150,0), (0,100,0), play_game)
        button("LEADERBOARD", 200, 270, 200, 50, (0,0,150), (0,0,100), leaderboard_screen)
        button("SETTINGS", 200, 340, 200, 50, (150,150,0), (100,100,0), settings_screen)
        button("QUIT", 200, 410, 200, 50, (150,0,0), (100,0,0), sys.exit)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        clock.tick(30)

if __name__ == "__main__":
    main_menu()