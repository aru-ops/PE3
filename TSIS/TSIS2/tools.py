import pygame

def flood_fill(surface, x, y, new_color):
    try:
        original_color = surface.get_at((x, y))[:3]
    except IndexError:
        return
    if original_color == new_color:
        return
    stack = [(x, y)]
    w, h = surface.get_size()
    while stack:
        cx, cy = stack.pop()
        if cx < 0 or cx >= w or cy < 0 or cy >= h:
            continue
        if surface.get_at((cx, cy))[:3] != original_color:
            continue
        surface.set_at((cx, cy), new_color + (255,))
        stack.extend([(cx+1,cy), (cx-1,cy), (cx,cy+1), (cx,cy-1)])

def get_right_triangle_points(start, end):
    x1,y1 = start
    x2,y2 = end
    return [(x1,y1), (x1,y2), (x2,y2)]

def get_equilateral_triangle(start, end):
    x1,y1 = start
    x2,y2 = end
    dx = x2 - x1
    dy = y2 - y1
    length = (dx*dx + dy*dy)**0.5
    if length == 0:
        return None
    mx = (x1 + x2)/2
    my = (y1 + y2)/2
    height = (3**0.5)/2 * length
    perp_x = -dy/length
    perp_y = dx/length
    third_x = mx + perp_x * height
    third_y = my + perp_y * height
    return [(x1,y1), (x2,y2), (third_x, third_y)]

def get_rhombus_points(start, end):
    x1,y1 = start
    x2,y2 = end
    cx = (x1 + x2)/2
    cy = (y1 + y2)/2
    dx = abs(x2 - x1)/2
    dy = abs(y2 - y1)/2
    return [(cx, cy-dy), (cx+dx, cy), (cx, cy+dy), (cx-dx, cy)]