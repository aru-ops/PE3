# paint.py
# Главный файл приложения Paint (интерфейс, обработка событий)

import pygame
from tools import *

# ---------- Инициализация ----------
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Paint Pro - TSIS2")
clock = pygame.time.Clock()

canvas = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT))
canvas.fill(WHITE)

# ---------- Состояние приложения ----------
current_tool = PEN
current_color = BLACK
drawing = False
start_pos = None
end_pos = None
last_pos = None          # для рисования карандашом
brush_size_index = 1     # индекс размера (2,5,10)

# Текстовый ввод
text_input_active = False
text_input_pos = None
text_input_string = ""
text_font = pygame.font.SysFont("Arial", 24)

def get_brush_size():
    return BRUSH_SIZES[brush_size_index]

# ---------- Палитра цветов ----------
palette = [
    {"color": BLACK, "rect": pygame.Rect(620, 60, 30, 30)},
    {"color": RED, "rect": pygame.Rect(660, 60, 30, 30)},
    {"color": GREEN, "rect": pygame.Rect(700, 60, 30, 30)},
    {"color": BLUE, "rect": pygame.Rect(740, 60, 30, 30)},
    {"color": YELLOW, "rect": pygame.Rect(620, 100, 30, 30)},
    {"color": PURPLE, "rect": pygame.Rect(660, 100, 30, 30)},
    {"color": ORANGE, "rect": pygame.Rect(700, 100, 30, 30)},
    {"color": WHITE, "rect": pygame.Rect(740, 100, 30, 30)},
]

# ---------- Кнопки инструментов ----------
tool_buttons = [
    {"tool": PEN, "rect": pygame.Rect(620, 150, 60, 30), "text": "Pen"},
    {"tool": LINE, "rect": pygame.Rect(690, 150, 60, 30), "text": "Line"},
    {"tool": RECTANGLE, "rect": pygame.Rect(620, 190, 60, 30), "text": "Rect"},
    {"tool": CIRCLE, "rect": pygame.Rect(690, 190, 60, 30), "text": "Circle"},
    {"tool": SQUARE, "rect": pygame.Rect(620, 230, 80, 30), "text": "Square"},
    {"tool": RIGHT_TRIANGLE, "rect": pygame.Rect(710, 230, 80, 30), "text": "RightTri"},
    {"tool": EQUILATERAL, "rect": pygame.Rect(620, 270, 80, 30), "text": "EquiTri"},
    {"tool": RHOMBUS, "rect": pygame.Rect(710, 270, 80, 30), "text": "Rhombus"},
    {"tool": ERASER, "rect": pygame.Rect(620, 310, 60, 30), "text": "Eraser"},
    {"tool": FILL, "rect": pygame.Rect(690, 310, 60, 30), "text": "Fill"},
    {"tool": TEXT, "rect": pygame.Rect(620, 350, 60, 30), "text": "Text"},
]

# ---------- Кнопки размера кисти ----------
brush_buttons = [
    {"size": 2, "rect": pygame.Rect(690, 350, 30, 30), "text": "2"},
    {"size": 5, "rect": pygame.Rect(730, 350, 30, 30), "text": "5"},
    {"size": 10, "rect": pygame.Rect(770, 350, 30, 30), "text": "10"},
]

font = pygame.font.SysFont("Arial", 14)

def draw_ui():
    """Рисует всю панель инструментов."""
    # Фон правой панели
    pygame.draw.rect(screen, GRAY, (CANVAS_WIDTH, 0, SCREEN_WIDTH - CANVAS_WIDTH, SCREEN_HEIGHT))
    # Цвета
    for color_info in palette:
        pygame.draw.rect(screen, color_info["color"], color_info["rect"])
        pygame.draw.rect(screen, BLACK, color_info["rect"], 2)
    # Кнопки инструментов
    for btn in tool_buttons:
        color = (100, 100, 200) if btn["tool"] == current_tool else GRAY
        pygame.draw.rect(screen, color, btn["rect"])
        pygame.draw.rect(screen, BLACK, btn["rect"], 2)
        text_surf = font.render(btn["text"], True, BLACK)
        text_rect = text_surf.get_rect(center=btn["rect"].center)
        screen.blit(text_surf, text_rect)
    # Кнопки размера кисти
    for btn in brush_buttons:
        if btn["size"] == get_brush_size():
            pygame.draw.rect(screen, (100, 200, 100), btn["rect"])
        else:
            pygame.draw.rect(screen, LIGHT_GRAY, btn["rect"])
        pygame.draw.rect(screen, BLACK, btn["rect"], 2)
        text_surf = font.render(btn["text"], True, BLACK)
        text_rect = text_surf.get_rect(center=btn["rect"].center)
        screen.blit(text_surf, text_rect)
    # Текущий размер
    size_text = font.render(f"Brush: {get_brush_size()}px", True, BLACK)
    screen.blit(size_text, (620, 390))

# ---------- Обработка текста ----------
def start_text_input(pos):
    global text_input_active, text_input_pos, text_input_string
    text_input_active = True
    text_input_pos = pos
    text_input_string = ""

def update_text_input(event):
    global text_input_string, text_input_active
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RETURN:
            if text_input_string:
                text_surface = text_font.render(text_input_string, True, current_color)
                canvas.blit(text_surface, text_input_pos)
            text_input_active = False
        elif event.key == pygame.K_ESCAPE:
            text_input_active = False
        elif event.key == pygame.K_BACKSPACE:
            text_input_string = text_input_string[:-1]
        else:
            if event.unicode and event.unicode.isprintable():
                text_input_string += event.unicode

def draw_text_preview():
    if text_input_active and text_input_string:
        preview_surf = text_font.render(text_input_string + "_", True, current_color)
        screen.blit(preview_surf, text_input_pos)

# ---------- Основной цикл ----------
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Ctrl+S сохранение
        if event.type == pygame.KEYDOWN and event.mod & pygame.KMOD_CTRL and event.key == pygame.K_s:
            save_canvas(canvas)

        # Переключение размера клавишами 1,2,3
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                brush_size_index = 0
            elif event.key == pygame.K_2:
                brush_size_index = 1
            elif event.key == pygame.K_3:
                brush_size_index = 2

        # Обработка мыши
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            # Выбор цвета
            for color_info in palette:
                if color_info["rect"].collidepoint(x, y):
                    current_color = color_info["color"]
                    break
            # Выбор инструмента
            for btn in tool_buttons:
                if btn["rect"].collidepoint(x, y):
                    current_tool = btn["tool"]
                    break
            # Выбор размера кисти
            for btn in brush_buttons:
                if btn["rect"].collidepoint(x, y):
                    brush_size_index = BRUSH_SIZES.index(btn["size"])
                    break
            # Действия на холсте
            if x < CANVAS_WIDTH and y < CANVAS_HEIGHT:
                if current_tool == FILL:
                    target = canvas.get_at((x, y))
                    if target != current_color:
                        flood_fill(canvas, x, y, target, current_color)
                elif current_tool == TEXT:
                    start_text_input((x, y))
                else:
                    drawing = True
                    start_pos = (x, y)
                    last_pos = (x, y)

        # Движение мыши (рисование)
        if event.type == pygame.MOUSEMOTION and drawing:
            x, y = event.pos
            if x < CANVAS_WIDTH and y < CANVAS_HEIGHT:
                end_pos = (x, y)
                if current_tool == PEN:
                    draw_shape(canvas, PEN, current_color, last_pos, end_pos, get_brush_size())
                    last_pos = end_pos
                elif current_tool == ERASER:
                    draw_eraser(canvas, end_pos, get_brush_size())
                    last_pos = end_pos

        # Отпускание мыши (фиксация фигур)
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and drawing:
            drawing = False
            x, y = event.pos
            if x < CANVAS_WIDTH and y < CANVAS_HEIGHT:
                end_pos = (x, y)
                if current_tool in [RECTANGLE, CIRCLE, SQUARE, RIGHT_TRIANGLE, EQUILATERAL, RHOMBUS, LINE]:
                    draw_shape(canvas, current_tool, current_color, start_pos, end_pos, get_brush_size())

        # Текстовый ввод
        if text_input_active:
            update_text_input(event)

    # ---- Отрисовка ----
    screen.fill(WHITE)
    screen.blit(canvas, (0, 0))

    # Предпросмотр для фигур
    if drawing and current_tool in [RECTANGLE, CIRCLE, SQUARE, RIGHT_TRIANGLE, EQUILATERAL, RHOMBUS, LINE]:
        temp_surf = canvas.copy()
        draw_shape(temp_surf, current_tool, current_color, start_pos, end_pos, get_brush_size())
        screen.blit(temp_surf, (0, 0))

    draw_text_preview()
    draw_ui()

    pygame.display.update()
    clock.tick(60)

pygame.quit()