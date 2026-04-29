# main.py - Main menu and game flow for Snake Game (TSIS 4)
# Handles all screens: main menu, leaderboard, settings, game over, and game execution

import pygame
import db
import config
import game
from config import WIDTH, HEIGHT

# Initialize Pygame and set up main window
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Snake - PostgreSQL & JSON")
# Different font sizes for headings and regular text
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 36)

def draw_button(text, rect, color, hover_color, mouse_pos):
    """
    Draw a button with hover effect.
    Changes color when mouse is over it.
    Returns True if the mouse is hovering (used for click detection elsewhere).
    """
    is_hover = rect.collidepoint(mouse_pos)                    # check if mouse inside button
    pygame.draw.rect(screen, hover_color if is_hover else color, rect)
    text_surf = font.render(text, True, (255, 255, 255))       # white text
    # Center text inside button
    screen.blit(text_surf, (rect.x + (rect.width - text_surf.get_width()) // 2, rect.y + 10))
    return is_hover

def main():
    # Initialize database tables if they don't exist
    db.setup_database()
    # Load user settings (snake color, grid, sound) from settings.json
    settings = config.load_settings()

    # Global state variables
    state = "MENU"                     # can be MENU, PLAYING, LEADERBOARD, SETTINGS, GAME_OVER
    username = ""                      # typed by player on the main menu
    player_id = None                   # database ID of the current player
    last_score, last_level = 0, 0      # results from the last game
    personal_best = 0                  # player's highest score (from DB)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        click = False                  # becomes True if left mouse button is pressed this frame

        # ---- Event handling ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click = True
            # Handle keyboard input only on the main menu
            if state == "MENU" and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    username = username[:-1]                # delete last character
                elif event.key == pygame.K_RETURN and username != "":
                    # Pressing Enter starts the game
                    player_id = db.get_or_create_player(username)
                    personal_best = db.get_personal_best(player_id)
                    state = "PLAYING"
                elif event.key != pygame.K_RETURN and len(username) < 15:
                    username += event.unicode                # add typed character

        # Clear screen with dark gray background
        screen.fill((20, 20, 20))

        # ----- MAIN MENU -----
        if state == "MENU":
            title = font.render("SNAKE GAME", True, (0, 255, 0))   # green title
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
            # Prompt with blinking cursor
            prompt = small_font.render("Type Username: " + username + ("_" if pygame.time.get_ticks() % 1000 < 500 else ""), True, (200, 200, 200))
            screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, 150))

            # Define button rectangles
            btn_play = pygame.Rect(WIDTH//2 - 100, 250, 200, 50)
            btn_lead = pygame.Rect(WIDTH//2 - 125, 320, 250, 50)
            btn_sett = pygame.Rect(WIDTH//2 - 100, 390, 200, 50)
            btn_quit = pygame.Rect(WIDTH//2 - 100, 460, 200, 50)

            # Draw buttons and check clicks
            if draw_button("Play", btn_play, (50, 150, 50), (80, 200, 80), mouse_pos) and click and username != "":
                player_id = db.get_or_create_player(username)
                personal_best = db.get_personal_best(player_id)
                state = "PLAYING"
            if draw_button("Leaderboard", btn_lead, (50, 50, 150), (80, 80, 200), mouse_pos) and click:
                state = "LEADERBOARD"
            if draw_button("Settings", btn_sett, (150, 150, 50), (200, 200, 80), mouse_pos) and click:
                state = "SETTINGS"
            if draw_button("Quit", btn_quit, (150, 50, 50), (200, 80, 80), mouse_pos) and click:
                running = False

        # ----- PLAYING -----
        elif state == "PLAYING":
            # Run the actual game loop (inside game.py)
            last_score, last_level = game.run_game(screen, settings, personal_best)
            if last_score is None:                       # window closed during game
                running = False
            else:
                # Game finished – save result to database
                db.save_score(player_id, last_score, last_level)
                state = "GAME_OVER"

        # ----- GAME OVER SCREEN -----
        elif state == "GAME_OVER":
            go_text = font.render("GAME OVER", True, (255, 0, 0))
            screen.blit(go_text, (WIDTH//2 - go_text.get_width()//2, 100))
            s_text = small_font.render(f"Score: {last_score} | Level: {last_level}", True, (255, 255, 255))
            screen.blit(s_text, (WIDTH//2 - s_text.get_width()//2, 200))

            btn_retry = pygame.Rect(WIDTH//2 - 100, 300, 200, 50)
            btn_menu = pygame.Rect(WIDTH//2 - 100, 370, 200, 50)

            if draw_button("Retry", btn_retry, (50, 150, 50), (80, 200, 80), mouse_pos) and click:
                # Restart with the same player
                personal_best = db.get_personal_best(player_id)
                state = "PLAYING"
            if draw_button("Menu", btn_menu, (100, 100, 100), (150, 150, 150), mouse_pos) and click:
                state = "MENU"

        # ----- LEADERBOARD SCREEN (top 10 scores) -----
        elif state == "LEADERBOARD":
            title = font.render("TOP 10 SCORES", True, (255, 215, 0))   # gold color
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))
            y_offset = 100
            # Fetch top 10 from database and display each
            for rank, row in enumerate(db.get_top_10(), 1):
                # row contains: username, score, level, date
                txt = small_font.render(f"{rank}. {row[0]} - Score: {row[1]} - Lvl: {row[2]}", True, (200, 200, 200))
                screen.blit(txt, (WIDTH//2 - txt.get_width()//2, y_offset))
                y_offset += 35
            btn_back = pygame.Rect(WIDTH//2 - 100, 500, 200, 50)
            if draw_button("Back", btn_back, (100, 100, 100), (150, 150, 150), mouse_pos) and click:
                state = "MENU"

        # ----- SETTINGS SCREEN -----
        elif state == "SETTINGS":
            title = font.render("SETTINGS", True, (255, 255, 255))
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))

            # Labels that change based on current settings
            grid_lbl = "Grid: ON" if settings["grid_overlay"] else "Grid: OFF"
            sound_lbl = "Sound: ON" if settings["sound"] else "Sound: OFF"

            btn_grid = pygame.Rect(WIDTH//2 - 150, 150, 300, 50)
            btn_sound = pygame.Rect(WIDTH//2 - 150, 220, 300, 50)
            btn_color = pygame.Rect(WIDTH//2 - 150, 290, 300, 50)
            btn_back = pygame.Rect(WIDTH//2 - 100, 450, 200, 50)

            # Toggle grid overlay
            if draw_button(grid_lbl, btn_grid, (70, 70, 70), (100, 100, 100), mouse_pos) and click:
                settings["grid_overlay"] = not settings["grid_overlay"]
                config.save_settings(settings)             # save change to file
            # Toggle sound
            if draw_button(sound_lbl, btn_sound, (70, 70, 70), (100, 100, 100), mouse_pos) and click:
                settings["sound"] = not settings["sound"]
                config.save_settings(settings)
            # Cycle snake color: Green → Blue → Yellow → Green ...
            if draw_button("Cycle Snake Color", btn_color, tuple(settings["snake_color"]), (150, 150, 150), mouse_pos) and click:
                c = settings["snake_color"]
                if c == [0, 255, 0]:
                    settings["snake_color"] = [0, 100, 255]   # blue
                elif c == [0, 100, 255]:
                    settings["snake_color"] = [255, 255, 0]   # yellow
                else:
                    settings["snake_color"] = [0, 255, 0]     # green
                config.save_settings(settings)
            # Return to main menu
            if draw_button("Back", btn_back, (100, 100, 100), (150, 150, 150), mouse_pos) and click:
                state = "MENU"

        pygame.display.flip()           # update the entire screen

    pygame.quit()                       # clean exit

if __name__ == "__main__":
    main()