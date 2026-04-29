# ui.py
import pygame

pygame.init()
font_small = pygame.font.SysFont("Arial", 24)
font_medium = pygame.font.SysFont("Arial", 32)
font_large = pygame.font.SysFont("Arial", 48)

def draw_text(surface, text, font, color, x, y, center=False):
    img = font.render(text, True, color)
    if center:
        rect = img.get_rect(center=(x, y))
        surface.blit(img, rect)
    else:
        surface.blit(img, (x, y))

def button(surface, text, x, y, w, h, active_color, inactive_color, action=None):
    """Простая кнопка. Возвращает True, если нажата."""
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect = pygame.Rect(x, y, w, h)
    color = active_color if rect.collidepoint(mouse) else inactive_color
    pygame.draw.rect(surface, color, rect)
    pygame.draw.rect(surface, (0,0,0), rect, 2)
    draw_text(surface, text, font_medium, (0,0,0), x + w//2, y + h//2, center=True)
    if rect.collidepoint(mouse) and click[0] and action:
        if callable(action):
            action()
        return True
    return False

def main_menu(screen, on_play, on_leaderboard, on_settings, on_quit):
    """Рисует главное меню и обрабатывает нажатия кнопок."""
    running = True
    while running:
        screen.fill((30,30,30))
        draw_text(screen, "RACER GAME", font_large, (255,255,0), 400, 100, center=True)
        # Кнопки
        if button(screen, "PLAY", 300, 200, 200, 50, (0,150,0), (0,100,0), on_play):
            running = False
        if button(screen, "LEADERBOARD", 300, 270, 200, 50, (0,0,150), (0,0,100), on_leaderboard):
            # on_leaderboard откроет экран лидерборда, но меню должно ждать
            pass
        if button(screen, "SETTINGS", 300, 340, 200, 50, (150,150,0), (100,100,0), on_settings):
            pass
        if button(screen, "QUIT", 300, 410, 200, 50, (150,0,0), (100,0,0), on_quit):
            running = False
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
    # После выхода из меню вызывается on_play или другие действия

def leaderboard_screen(screen, back_callback):
    """Показывает топ-10 результатов."""
    from persistence import load_leaderboard
    entries = load_leaderboard()
    running = True
    while running:
        screen.fill((40,40,60))
        draw_text(screen, "TOP 10 SCORES", font_large, (255,255,255), 400, 50, center=True)
        y = 120
        for i, entry in enumerate(entries[:10]):
            line = f"{i+1}. {entry['name']} - Score: {entry['score']} - Dist: {entry['distance']}m"
            draw_text(screen, line, font_medium, (200,200,200), 50, y)
            y += 35
        if button(screen, "BACK", 300, 500, 200, 40, (100,100,100), (50,50,50), back_callback):
            running = False
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

def settings_screen(screen, settings, on_save):
    """Экран настроек. Изменяет переданный словарь settings и сохраняет."""
    from persistence import save_settings
    options = ["sound", "car_color", "difficulty"]
    color_options = ["green", "red", "blue"]
    diff_options = ["easy", "normal", "hard"]
    selected_option = 0
    running = True
    while running:
        screen.fill((50,50,50))
        draw_text(screen, "SETTINGS", font_large, (255,255,0), 400, 50, center=True)
        # Звук
        txt = f"Sound: {'ON' if settings['sound'] else 'OFF'}"
        draw_text(screen, txt, font_medium, (255,255,255), 100, 150)
        # Цвет машины
        color_txt = f"Car color: {settings['car_color']}"
        draw_text(screen, color_txt, font_medium, (255,255,255), 100, 220)
        # Сложность
        diff_txt = f"Difficulty: {settings['difficulty']}"
        draw_text(screen, diff_txt, font_medium, (255,255,255), 100, 290)
        # Управление: стрелки вверх/вниз, Enter для изменения
        draw_text(screen, "Use UP/DOWN arrows, ENTER to change", font_small, (200,200,200), 400, 400, center=True)
        if button(screen, "SAVE & BACK", 300, 500, 200, 40, (0,150,0), (0,100,0), lambda: None):
            save_settings(settings)
            if on_save:
                on_save()  # обновить глобальные настройки в игре
            running = False
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    # Изменить выбранную опцию
                    opt = options[selected_option]
                    if opt == "sound":
                        settings["sound"] = not settings["sound"]
                    elif opt == "car_color":
                        idx = color_options.index(settings["car_color"])
                        idx = (idx + 1) % len(color_options)
                        settings["car_color"] = color_options[idx]
                    elif opt == "difficulty":
                        idx = diff_options.index(settings["difficulty"])
                        idx = (idx + 1) % len(diff_options)
                        settings["difficulty"] = diff_options[idx]
    return settings

def game_over_screen(screen, score, distance, coins, on_retry, on_menu):
    """Экран окончания игры."""
    running = True
    while running:
        screen.fill((0,0,0))
        draw_text(screen, "GAME OVER", font_large, (255,0,0), 400, 80, center=True)
        draw_text(screen, f"Score: {score}", font_medium, (255,255,255), 400, 160, center=True)
        draw_text(screen, f"Distance: {distance} m", font_medium, (255,255,255), 400, 210, center=True)
        draw_text(screen, f"Coins: {coins}", font_medium, (255,255,255), 400, 260, center=True)
        if button(screen, "RETRY", 250, 350, 120, 40, (0,150,0), (0,100,0), on_retry):
            running = False
        if button(screen, "MAIN MENU", 430, 350, 120, 40, (150,150,0), (100,100,0), on_menu):
            running = False
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()