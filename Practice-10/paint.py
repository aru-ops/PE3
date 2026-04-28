import pygame

# Initialize Pygame
pygame.init()

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
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

# Tools
PEN = 0
RECTANGLE = 1
CIRCLE = 2
ERASER = 3

# --- Game Window Setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Paint Program")
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

# --- Tool Buttons ---
tool_buttons = [
    {"tool": PEN, "rect": pygame.Rect(620, 150, 60, 30), "text": "Pen"},
    {"tool": RECTANGLE, "rect": pygame.Rect(690, 150, 60, 30), "text": "Rect"},
    {"tool": CIRCLE, "rect": pygame.Rect(620, 190, 60, 30), "text": "Circle"},
    {"tool": ERASER, "rect": pygame.Rect(690, 190, 60, 30), "text": "Eraser"},
]

# Font for button labels
font = pygame.font.SysFont("Arial", 16)

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
        pygame.draw.rect(screen, GRAY, button["rect"])
        pygame.draw.rect(screen, BLACK, button["rect"], 2)
        text = font.render(button["text"], True, BLACK)
        text_rect = text.get_rect(center=button["rect"].center)
        screen.blit(text, text_rect)

def draw_shape(surface, tool, color, start, end):
    """Draw a shape on the given surface."""
    if tool == RECTANGLE:
        x = min(start[0], end[0])
        y = min(start[1], end[1])
        w = abs(start[0] - end[0])
        h = abs(start[1] - end[1])
        pygame.draw.rect(surface, color, (x, y, w, h), 2)  # Outline
    elif tool == CIRCLE:
        center = ((start[0] + end[0]) // 2, (start[1] + end[1]) // 2)
        radius = max(abs(start[0] - end[0]), abs(start[1] - end[1])) // 2
        pygame.draw.circle(surface, color, center, radius, 2)  # Outline
    elif tool == PEN:
        pygame.draw.line(surface, color, start, end, brush_size)
    elif tool == ERASER:
        pygame.draw.circle(surface, WHITE, end, eraser_size)

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
                if current_tool == PEN or current_tool == ERASER:
                    # Draw directly on canvas for pen and eraser
                    draw_shape(canvas, current_tool, current_color, start_pos, end_pos)
                    start_pos = end_pos

        # Mouse button up
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and drawing:
                drawing = False
                x, y = event.pos
                if x < CANVAS_WIDTH and y < CANVAS_HEIGHT:
                    end_pos = event.pos
                    # Draw final shape on canvas for rectangle and circle
                    if current_tool == RECTANGLE or current_tool == CIRCLE:
                        draw_shape(canvas, current_tool, current_color, start_pos, end_pos)

    # --- Drawing ---
    # Clear screen
    screen.fill(WHITE)

    # Draw canvas
    screen.blit(canvas, (0, 0))

    # Draw UI elements
    draw_ui()

    # Draw preview shape while drawing (for rectangle and circle)
    if drawing and (current_tool == RECTANGLE or current_tool == CIRCLE):
        preview_surface = screen.subsurface((0, 0, CANVAS_WIDTH, CANVAS_HEIGHT))
        # Make a copy of the canvas to draw preview
        temp_surface = canvas.copy()
        draw_shape(temp_surface, current_tool, current_color, start_pos, end_pos)
        screen.blit(temp_surface, (0, 0))

    # Update display
    pygame.display.update()
    clock.tick(60)

pygame.quit()