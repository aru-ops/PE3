import pygame

def flood_fill(surface, x, y, new_color):
    """
    Iterative flood fill using a stack.
    Replaces all pixels connected to (x,y) that have the same color as the original.
    """
    try:
        original_color = surface.get_at((x, y))[:3]
    except IndexError:
        return
    if original_color == new_color:
        return

    stack = [(x, y)]
    width, height = surface.get_size()

    while stack:
        cx, cy = stack.pop()
        if cx < 0 or cx >= width or cy < 0 or cy >= height:
            continue
        if surface.get_at((cx, cy))[:3] != original_color:
            continue

        surface.set_at((cx, cy), new_color + (255,))

        stack.append((cx + 1, cy))
        stack.append((cx - 1, cy))
        stack.append((cx, cy + 1))
        stack.append((cx, cy - 1))

def get_right_triangle_points(start, end):
    """Return points for a right triangle with legs parallel to axes."""
    x1, y1 = start
    x2, y2 = end
    return [(x1, y1), (x1, y2), (x2, y2)]

def get_equilateral_triangle(start, end):
    """
    Return vertices of an equilateral triangle using start and end as two vertices.
    Third vertex is placed perpendicularly above/below the base's midpoint.
    """
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
    length = (dx**2 + dy**2) ** 0.5
    if length == 0:
        return None
    mx = (x1 + x2) / 2
    my = (y1 + y2) / 2
    height = (3**0.5) / 2 * length
    perp_x = -dy / length
    perp_y = dx / length
    third_x = mx + perp_x * height
    third_y = my + perp_y * height
    return [(x1, y1), (x2, y2), (third_x, third_y)]

def get_rhombus_points(start, end):
    """
    Return four points of a rhombus (diamond) inscribed in the rectangle defined by start and end.
    """
    x1, y1 = start
    x2, y2 = end
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    dx = abs(x2 - x1) / 2
    dy = abs(y2 - y1) / 2
    return [
        (cx, cy - dy),
        (cx + dx, cy),
        (cx, cy + dy),
        (cx - dx, cy)
    ]