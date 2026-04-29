# main.py
import pygame
import sys
from ui import main_menu, leaderboard_screen, settings_screen, game_over_screen
from persistence import load_settings, save_settings, add_score
from racer import Game

pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer - TSIS3")

def get_player_name():
    """Запрашивает имя перед игрой."""
    name = ""
    input_active = True
    font = pygame.font.SysFont("Arial", 32)
    while input_active:
        screen.fill((0,0,0))
        prompt = font.render("Enter your name:", True, (255,255,255))
        name_surface = font.render(name + "_", True, (255,255,0))
        screen.blit(prompt, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 60))
        screen.blit(name_surface, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2))
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

def play_game():
    player_name = get_player_name()
    game = Game(screen, player_name)
    score, distance, coins = game.run()
    # Показываем экран Game Over
    def retry():
        nonlocal game
        game = Game(screen, player_name)
        game.run()
    def back_to_menu():
        return
    game_over_screen(screen, int(score), int(distance), coins, lambda: play_game(), lambda: None)
    # После game_over_screen возвращаемся в главное меню

def show_leaderboard():
    leaderboard_screen(screen, lambda: None)

def show_settings():
    settings = load_settings()
    settings_screen(screen, settings, lambda: None)

def quit_game():
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    while True:
        main_menu(screen, play_game, show_leaderboard, show_settings, quit_game)