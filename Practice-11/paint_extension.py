import pygame
import math

# Initialize Pygame
pygame.init()

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT =600
CANVAS_WIDTH = 600
CANVAS_HEIGHT = 500
PALETTE_WIDTH = 150
TOOLBAR_HEIGHT = 50

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)

# Tools (Extended with new shapes)
PEN = 0
RECTANGLE = 1
CIRCLE = 2
ERASER = 3
SQUARE = 4          # New: Square shape
RIGHT_TRIANGLE = 5  # New: Right triangle
EQUILATERAL = 6     # New: Equilateral triangle
RHOMBUS = 7         # New: Rhombus (diamond)

# --- Game Window Setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Paint Program - Extended Shapes")
clock = pygame.time.Clock()

# --- Drawing Surface ---
canvas = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT))
canvas.fill(WHITE)  # Start with a white canvas

# --- Game Variables ---
current_tool = PEN
current_color = BLACK
drawing = False
start_pos = None
end_pos = None

# Brush size
brush_size = 5
eraser_size = 20

# --- Color Palette (Rectangles) ---
palette = [
    {"color": BLACK, "rect": pygame.Rect(620, 60, 30, 30)},
    {"color": RED, "rect": pygame.Rect(660, 60, 30, 30)},
    {"color": GREEN, "rect": pygame.Rect(700, 60, 30, 30)},
    {"color": BLUE, "rect": pygame.Rect(740, 60, 30, 30)},
    {"color": YELLOW, "rect": pygame.Rect(620, 100, 30, 30)},
    {"color": PURPLE, "rect": pygame.Rect(660, 100, 30, 30)},
    {"color": ORANGE, "rect": pygame.Rect(700, 100, 30, 30)},
    {"color": WHITE, "rect": pygame.Rect(740, 100, 30, 30)}  # White for eraser?
]

# --- Tool Buttons (Extended with new shape buttons) ---
tool_buttons = [
    {"tool": PEN, "rect": pygame.Rect(620, 150, 60, 30), "text": "Pen"},
    {"tool": RECTANGLE, "rect": pygame.Rect(690, 150, 60, 30), "text": "Rect"},
    {"tool": CIRCLE, "rect": pygame.Rect(620, 190, 60, 30), "text": "Circle"},
    {"tool": ERASER, "rect": pygame.Rect(690, 190, 60, 30), "text": "Eraser"},
    # New shape buttons
    {"tool": SQUARE, "rect": pygame.Rect(620, 230, 80, 30), "text": "Square"},
    {"tool": RIGHT_TRIANGLE, "rect": pygame.Rect(710, 230, 80, 30), "text": "Right Tri"},
    {"tool": EQUILATERAL, "rect": pygame.Rect(620, 270, 80, 30), "text": "Equilateral"},
    {"tool": RHOMBUS, "rect": pygame.Rect(710, 270, 80, 30), "text": "Rhombus"},
]

# Font for button labels
font = pygame.font.SysFont("Arial", 14)

def draw_ui():
    """Draw the user interface (color palette and tool buttons)."""
    # Draw palette background
    pygame.draw.rect(screen, GRAY, (CANVAS_WIDTH, 0, PALETTE_WIDTH, SCREEN_HEIGHT))

    # Draw color squares
    for color_info in palette:
        pygame.draw.rect(screen, color_info["color"], color_info["rect"])
        pygame.draw.rect(screen, BLACK, color_info["rect"], 2)  # Border

    # Draw tool buttons
    for button in tool_buttons:
        # Highlight active tool with different color
        if button["tool"] == current_tool:
            pygame.draw.rect(screen, (100, 100, 200), button["rect"])  # Highlight
        else:
            pygame.draw.rect(screen, GRAY, button["rect"])
        pygame.draw.rect(screen, BLACK, button["rect"], 2)
        text = font.render(button["text"], True, BLACK)
        text_rect = text.get_rect(center=button["rect"].center)
        screen.blit(text, text_rect)

def draw_square(surface, color, start, end):
    """
    Draw a square (all sides equal).
    Uses the smaller of width and height to maintain square proportions.
    """
    x1, y1 = start
    x2, y2 = end
    width = abs(x2 - x1)
    height = abs(y2 - y1)
    size = min(width, height)  # Make it a perfect square
    
    # Determine top-left corner
    x = min(x1, x2)
    y = min(y1, y2)
    
    # If mouse dragged left or up, adjust position
    if x2 < x1:
        x = x1 - size
    if y2 < y1:
        y = y1 - size
        
    pygame.draw.rect(surface, color, (x, y, size, size), 2)  # Outline only

def draw_right_triangle(surface, color, start, end):
    """
    Draw a right triangle (90-degree angle).
    The right angle is at the start position (top-left).
    """
    x1, y1 = start
    x2, y2 = end
    
    # Three points of the right triangle
    points = [
        (x1, y1),           # Top-left (right angle corner)
        (x2, y1),           # Top-right
        (x1, y2)            # Bottom-left
    ]
    pygame.draw.polygon(surface, color, points, 2)

def draw_equilateral_triangle(surface, color, start, end):
    """
    Draw an equilateral triangle (all sides equal).
    The triangle orientation depends on mouse movement direction.
    """
    x1, y1 = start
    x2, y2 = end
    
    side_length = abs(x2 - x1)
    height = side_length * math.sqrt(3) / 2  # Height of equilateral triangle
    
    # Determine triangle orientation based on mouse Y movement
    if y2 > y1:  # Mouse moved DOWN - triangle points down
        points = [
            (x1, y1),                                      # Top vertex
            (x1 - side_length//2, y1 + height),           # Bottom-left
            (x1 + side_length//2, y1 + height)            # Bottom-right
        ]
    else:  # Mouse moved UP - triangle points up
        points = [
            (x1, y1),                                      # Bottom vertex
            (x1 - side_length//2, y1 - height),           # Top-left
            (x1 + side_length//2, y1 - height)            # Top-right
        ]
    pygame.draw.polygon(surface, color, points, 2)

def draw_rhombus(surface, color, start, end):
    """
    Draw a rhombus (diamond shape).
    Uses start point as center, end point determines width and height.
    """
    center_x, center_y = start
    x2, y2 = end
    
    # Calculate width and height from center
    width = abs(x2 - center_x)
    height = abs(y2 - center_y)
    
    # Four vertices of the rhombus (diamond)
    points = [
        (center_x, center_y - height),   # Top
        (center_x + width, center_y),    # Right
        (center_x, center_y + height),   # Bottom
        (center_x - width, center_y)     # Left
    ]
    pygame.draw.polygon(surface, color, points, 2)

def draw_shape(surface, tool, color, start, end):
    """
    Draw a shape on the given surface.
    Extended to support all new shape types.
    """
    if tool == RECTANGLE:
        x = min(start[0], end[0])
        y = min(start[1], end[1])
        w = abs(start[0] - end[0])
        h = abs(start[1] - end[1])
        pygame.draw.rect(surface, color, (x, y, w, h), 2)
        
    elif tool == CIRCLE:
        center = ((start[0] + end[0]) // 2, (start[1] + end[1]) // 2)
        radius = max(abs(start[0] - end[0]), abs(start[1] - end[1])) // 2
        pygame.draw.circle(surface, color, center, radius, 2)
        
    elif tool == PEN:
        pygame.draw.line(surface, color, start, end, brush_size)
        
    elif tool == ERASER:
        pygame.draw.circle(surface, WHITE, end, eraser_size)
        
    # New shape drawing functions
    elif tool == SQUARE:
        draw_square(surface, color, start, end)
        
    elif tool == RIGHT_TRIANGLE:
        draw_right_triangle(surface, color, start, end)
        
    elif tool == EQUILATERAL:
        draw_equilateral_triangle(surface, color, start, end)
        
    elif tool == RHOMBUS:
        draw_rhombus(surface, color, start, end)

# --- Main Game Loop ---
running = True
while running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Mouse button down
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                x, y = event.pos
                # Check if click is on color palette
                for color_info in palette:
                    if color_info["rect"].collidepoint(x, y):
                        current_color = color_info["color"]
                        # If white is selected, it's effectively an eraser
                        if current_color == WHITE:
                            current_tool = ERASER
                        break
                        
                # Check if click is on tool buttons
                for button in tool_buttons:
                    if button["rect"].collidepoint(x, y):
                        current_tool = button["tool"]
                        break
                        
                # If click is on canvas, start drawing
                if x < CANVAS_WIDTH and y < CANVAS_HEIGHT:
                    drawing = True
                    start_pos = event.pos
                    end_pos = event.pos

        # Mouse motion
        elif event.type == pygame.MOUSEMOTION and drawing:
            x, y = event.pos
            if x < CANVAS_WIDTH and y < CANVAS_HEIGHT:
                end_pos = event.pos
                # Draw directly on canvas for pen and eraser (freehand)
                if current_tool == PEN or current_tool == ERASER:
                    draw_shape(canvas, current_tool, current_color, start_pos, end_pos)
                    start_pos = end_pos

        # Mouse button up
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and drawing:
                drawing = False
                x, y = event.pos
                if x < CANVAS_WIDTH and y < CANVAS_HEIGHT:
                    end_pos = event.pos
                    # Draw final shape on canvas for all shape tools
                    if current_tool in [RECTANGLE, CIRCLE, SQUARE, RIGHT_TRIANGLE, EQUILATERAL, RHOMBUS]:
                        draw_shape(canvas, current_tool, current_color, start_pos, end_pos)

    # --- Drawing ---
    # Clear screen
    screen.fill(WHITE)

    # Draw canvas
    screen.blit(canvas, (0, 0))

    # Draw UI elements
    draw_ui()

    # Draw preview shape while drawing (for shape tools)
    if drawing and current_tool in [RECTANGLE, CIRCLE, SQUARE, RIGHT_TRIANGLE, EQUILATERAL, RHOMBUS]:
        # Create a temporary surface for preview
        temp_surface = canvas.copy()
        draw_shape(temp_surface, current_tool, current_color, start_pos, end_pos)
        screen.blit(temp_surface, (0, 0))

    # Update display
    pygame.display.update()
    clock.tick(60)

pygame.quit()