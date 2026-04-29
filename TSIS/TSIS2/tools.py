# tools.py - Helper functions for Paint application (TSIS 2)
# Contains flood fill algorithm and geometry functions for triangles and rhombus
import pygame

def flood_fill(surface, x, y, new_color):
    """
    Perform iterative flood fill on a pygame Surface.
    Replaces all connected pixels of the original color with new_color.
    """
    # Try to get the color of the starting pixel, ignoring alpha channel
    try:
        original_color = surface.get_at((x, y))[:3]   # get RGB only
    except IndexError:
        return                                         # if coordinates are out of bounds, exit
    # If the new color is the same as original, nothing to do
    if original_color == new_color:
        return
    # Use a stack (list) for iterative flood fill (non-recursive to avoid recursion depth)
    stack = [(x, y)]
    w, h = surface.get_size()                          # boundaries of the surface
    while stack:
        cx, cy = stack.pop()                           # get the next pixel to process
        # Skip if pixel is outside the surface boundaries
        if cx < 0 or cx >= w or cy < 0 or cy >= h:
            continue
        # If the pixel's color (ignoring alpha) is not the original color, skip
        if surface.get_at((cx, cy))[:3] != original_color:
            continue
        # Change the pixel color (set full alpha = 255)
        surface.set_at((cx, cy), new_color + (255,))
        # Push the four orthogonal neighbors onto the stack
        stack.extend([(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)])

def get_right_triangle_points(start, end):
    """
    Return three points for a right triangle with legs parallel to the axes.
    The triangle is defined by the rectangle between start and end points.
    Points: (x1,y1) - top-left, (x1,y2) - bottom-left, (x2,y2) - bottom-right.
    """
    x1, y1 = start
    x2, y2 = end
    return [(x1, y1), (x1, y2), (x2, y2)]

def get_equilateral_triangle(start, end):
    """
    Return vertices of an equilateral triangle where start and end are two vertices.
    The third vertex is placed perpendicular to the base, calculated using vector math.
    """
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
    length = (dx*dx + dy*dy) ** 0.5                     # distance between start and end
    if length == 0:                                     # if points are identical, cannot form triangle
        return None
    mx = (x1 + x2) / 2                                  # midpoint of the base
    my = (y1 + y2) / 2
    height = (3 ** 0.5) / 2 * length                    # height of equilateral triangle
    # Perpendicular vector (rotate base direction by 90 degrees)
    perp_x = -dy / length
    perp_y = dx / length
    # Third vertex = midpoint + perpendicular vector * height
    third_x = mx + perp_x * height
    third_y = my + perp_y * height
    return [(x1, y1), (x2, y2), (third_x, third_y)]

def get_rhombus_points(start, end):
    """
    Return four points of a rhombus (diamond shape) inscribed in the rectangle
    defined by start (top-left) and end (bottom-right) corners.
    The rhombus's vertices lie at midpoints of the rectangle's edges.
    """
    x1, y1 = start
    x2, y2 = end
    cx = (x1 + x2) / 2                                 # center x
    cy = (y1 + y2) / 2                                 # center y
    dx = abs(x2 - x1) / 2                              # half width
    dy = abs(y2 - y1) / 2                              # half height
    # Return points: top, right, bottom, left
    return [(cx, cy - dy), (cx + dx, cy), (cx, cy + dy), (cx - dx, cy)]