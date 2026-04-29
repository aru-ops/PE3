# tools.py
# Библиотека инструментов для Paint (фигуры, заливка, сохранение)

import pygame
import math
from datetime import datetime

# ---------- Константы ----------
# Размеры окна и холста
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CANVAS_WIDTH = 600
CANVAS_HEIGHT = 500

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)

# Инструменты
PEN = 0
RECTANGLE = 1
CIRCLE = 2
ERASER = 3
SQUARE = 4
RIGHT_TRIANGLE = 5
EQUILATERAL = 6
RHOMBUS = 7
LINE = 8
FILL = 9
TEXT = 10

# Размеры кисти
BRUSH_SIZES = [2, 5, 10]

# ---------- Функции рисования фигур (с поддержкой толщины) ----------
def draw_rectangle(surface, color, start, end, thickness):
    x = min(start[0], end[0])
    y = min(start[1], end[1])
    w = abs(start[0] - end[0])
    h = abs(start[1] - end[1])
    pygame.draw.rect(surface, color, (x, y, w, h), thickness)

def draw_circle(surface, color, start, end, thickness):
    center = ((start[0] + end[0]) // 2, (start[1] + end[1]) // 2)
    radius = max(abs(start[0] - end[0]), abs(start[1] - end[1])) // 2
    pygame.draw.circle(surface, color, center, radius, thickness)

def draw_square(surface, color, start, end, thickness):
    x1, y1 = start
    x2, y2 = end
    w = abs(x2 - x1)
    h = abs(y2 - y1)
    size = min(w, h)
    x = min(x1, x2)
    y = min(y1, y2)
    if x2 < x1:
        x = x1 - size
    if y2 < y1:
        y = y1 - size
    pygame.draw.rect(surface, color, (x, y, size, size), thickness)

def draw_right_triangle(surface, color, start, end, thickness):
    x1, y1 = start
    x2, y2 = end
    points = [(x1, y1), (x2, y1), (x1, y2)]
    pygame.draw.polygon(surface, color, points, thickness)

def draw_equilateral_triangle(surface, color, start, end, thickness):
    x1, y1 = start
    x2, y2 = end
    side = abs(x2 - x1)
    height = side * math.sqrt(3) / 2
    if y2 > y1:  # pointing down
        points = [(x1, y1), (x1 - side // 2, y1 + height), (x1 + side // 2, y1 + height)]
    else:
        points = [(x1, y1), (x1 - side // 2, y1 - height), (x1 + side // 2, y1 - height)]
    pygame.draw.polygon(surface, color, points, thickness)

def draw_rhombus(surface, color, start, end, thickness):
    cx, cy = start
    x2, y2 = end
    w = abs(x2 - cx)
    h = abs(y2 - cy)
    points = [(cx, cy - h), (cx + w, cy), (cx, cy + h), (cx - w, cy)]
    pygame.draw.polygon(surface, color, points, thickness)

def draw_line(surface, color, start, end, thickness):
    pygame.draw.line(surface, color, start, end, thickness)

def draw_pen(surface, color, start, end, thickness):
    pygame.draw.line(surface, color, start, end, thickness)

def draw_eraser(surface, pos, thickness):
    pygame.draw.circle(surface, WHITE, pos, thickness // 2)

def draw_shape(surface, tool, color, start, end, thickness):
    """Обёртка для вызова нужной функции рисования по инструменту."""
    if tool == RECTANGLE:
        draw_rectangle(surface, color, start, end, thickness)
    elif tool == CIRCLE:
        draw_circle(surface, color, start, end, thickness)
    elif tool == SQUARE:
        draw_square(surface, color, start, end, thickness)
    elif tool == RIGHT_TRIANGLE:
        draw_right_triangle(surface, color, start, end, thickness)
    elif tool == EQUILATERAL:
        draw_equilateral_triangle(surface, color, start, end, thickness)
    elif tool == RHOMBUS:
        draw_rhombus(surface, color, start, end, thickness)
    elif tool == LINE:
        draw_line(surface, color, start, end, thickness)
    elif tool == PEN:
        draw_pen(surface, color, start, end, thickness)
    elif tool == ERASER:
        draw_eraser(surface, end, thickness)

# ---------- Flood Fill (заливка) ----------
def flood_fill(surface, x, y, target_color, fill_color):
    """Заливка замкнутой области (BFS)."""
    if target_color == fill_color:
        return
    w, h = surface.get_size()
    stack = [(x, y)]
    visited = set()
    while stack:
        cx, cy = stack.pop()
        if (cx, cy) in visited:
            continue
        if cx < 0 or cx >= w or cy < 0 or cy >= h:
            continue
        if surface.get_at((cx, cy)) != target_color:
            continue
        surface.set_at((cx, cy), fill_color)
        visited.add((cx, cy))
        # 4 соседа
        stack.extend([(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)])

# ---------- Сохранение холста ----------
def save_canvas(canvas):
    """Сохраняет холст в файл с меткой времени."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"canvas_{timestamp}.png"
    pygame.image.save(canvas, filename)
    print(f"Canvas saved as {filename}")
    return filename