# paint.py - Extended Paint Application (TSIS 2)
# Import required modules: pygame for graphics, sys for exit, datetime for timestamp,
# and custom tools for flood fill and shape geometry
import pygame
import sys
import datetime
from tools import flood_fill, get_equilateral_triangle, get_right_triangle_points, get_rhombus_points

# Initialize Pygame (must be called before any other pygame functions)
pygame.init()

# Window dimensions and toolbar width
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
TOOLBAR_WIDTH = 150
# Rectangle defining the canvas area (right side of the window)
CANVAS_RECT = pygame.Rect(TOOLBAR_WIDTH, 0, WINDOW_WIDTH - TOOLBAR_WIDTH, WINDOW_HEIGHT)

# Color definitions for background and UI buttons
BACKGROUND_COLOR = (255, 255, 255)          # white canvas background
BUTTON_COLOR = (220, 220, 220)               # light gray for normal buttons
BUTTON_HOVER_COLOR = (180, 180, 240)         # light blue when mouse hovers
ACTIVE_BUTTON_COLOR = (100, 200, 100)        # green for active tool button

# Keyboard shortcuts for brush size: keys 1,2,3 map to 2,5,10 pixels
BRUSH_SIZES = {pygame.K_1: 2, pygame.K_2: 5, pygame.K_3: 10}
# Position and size of brush size buttons in toolbar (relative coordinates)
BRUSH_SIZE_BUTTONS = [(2, (10, 0)), (5, (10, 35)), (10, (10, 70))]

# List of all available tools (order determines button grid)
TOOLS = ['pencil', 'line', 'rect', 'circle', 'square', 'right_triangle',
         'equilateral_triangle', 'rhombus', 'eraser', 'fill', 'text', 'color_picker']
DEFAULT_TOOL = 'pencil'

# Predefined color palette (RGB tuples)
PREDEFINED_COLORS = [
    (0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255),
    (255, 255, 0), (255, 165, 0), (255, 192, 203), (128, 0, 128)
]

class PaintApp:
    def __init__(self):
        """Initialize game window, surfaces, and state variables."""
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Extended Paint")
        self.clock = pygame.time.Clock()                     # for controlling frame rate
        self.font = pygame.font.SysFont("Arial", 16)         # regular font
        self.small_font = pygame.font.SysFont("Arial", 12)   # small font for buttons

        # Canvas surface where drawing actually happens (separate from screen)
        self.canvas = pygame.Surface((CANVAS_RECT.width, CANVAS_RECT.height))
        self.canvas.fill(BACKGROUND_COLOR)

        # Current drawing state
        self.current_color = (0, 0, 0)                       # start with black
        self.brush_size = 2                                  # default small size
        self.tool = DEFAULT_TOOL
        self.shape_filled = False                            # False = outline, True = filled

        # Drawing flags
        self.drawing = False                                 # mouse button held on canvas
        self.start_pos = None                                # start point for lines/shapes
        self.last_pos = None                                 # last position for continuous drawing
        self.preview_shape = None                            # temporary shape while dragging

        # Text tool state
        self.text_mode = False
        self.text_pos = None
        self.text_string = ""
        self.text_input_active = False

        # UI element references (to detect clicks)
        self.tool_buttons = {}
        self.preset_color_rects = []
        self.brush_buttons = []
        self.fill_toggle_rect = None

    def draw_toolbar(self):
        """Draw the left toolbar with all buttons, color swatches, and current color."""
        self.screen.fill((240, 240, 240), (0, 0, TOOLBAR_WIDTH, WINDOW_HEIGHT))
        pygame.draw.line(self.screen, (0, 0, 0), (TOOLBAR_WIDTH, 0), (TOOLBAR_WIDTH, WINDOW_HEIGHT), 2)

        y = 10   # current vertical position
        title = self.font.render("TOOLS", True, (0, 0, 0))
        self.screen.blit(title, (TOOLBAR_WIDTH//2 - title.get_width()//2, y))
        y += 25

        # Draw tool buttons in a 2‑column grid
        col_width = TOOLBAR_WIDTH // 2
        for i, tool in enumerate(TOOLS):
            row = i // 2
            col = i % 2
            x = 5 + col * col_width
            y_btn = y + row * 35
            rect = pygame.Rect(x, y_btn, col_width - 5, 30)
            # Highlight active tool, else normal button color
            color = ACTIVE_BUTTON_COLOR if self.tool == tool else BUTTON_COLOR
            if rect.collidepoint(pygame.mouse.get_pos()):
                color = BUTTON_HOVER_COLOR
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)
            text = self.small_font.render(tool.replace('_', ' ').title(), True, (0, 0, 0))
            self.screen.blit(text, (rect.x + 5, rect.y + 7))
            self.tool_buttons[tool] = rect      # store rect for click detection

        y += ((len(TOOLS) + 1) // 2) * 35 + 10

        # Brush size selection buttons
        size_title = self.font.render("Brush Size", True, (0, 0, 0))
        self.screen.blit(size_title, (TOOLBAR_WIDTH//2 - size_title.get_width()//2, y))
        y += 20
        for size, (x_offset, y_offset) in BRUSH_SIZE_BUTTONS:
            rect = pygame.Rect(x_offset, y + y_offset, 30, 30)
            color = ACTIVE_BUTTON_COLOR if self.brush_size == size else BUTTON_COLOR
            if rect.collidepoint(pygame.mouse.get_pos()):
                color = BUTTON_HOVER_COLOR
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)
            text = self.small_font.render(str(size), True, (0, 0, 0))
            self.screen.blit(text, (rect.x + 10, rect.y + 7))
            self.brush_buttons.append((rect, size))
        y += 100

        # Fill / Outline toggle button
        fill_text = "Filled" if self.shape_filled else "Outline"
        fill_rect = pygame.Rect(10, y, TOOLBAR_WIDTH - 20, 30)
        if self.shape_filled:
            color = (100, 200, 100)           # green when filled mode active
        else:
            color = BUTTON_COLOR
        if fill_rect.collidepoint(pygame.mouse.get_pos()):
            color = BUTTON_HOVER_COLOR
        pygame.draw.rect(self.screen, color, fill_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), fill_rect, 1)
        text = self.small_font.render(fill_text, True, (0, 0, 0))
        self.screen.blit(text, (fill_rect.x + 10, fill_rect.y + 7))
        self.fill_toggle_rect = fill_rect
        y += 40

        # Color palette (swatches)
        color_title = self.font.render("Colors", True, (0, 0, 0))
        self.screen.blit(color_title, (TOOLBAR_WIDTH//2 - color_title.get_width()//2, y))
        y += 20
        swatch_size = 25
        cols = 2
        for idx, col in enumerate(PREDEFINED_COLORS):
            row = idx // cols
            col_idx = idx % cols
            x = 10 + col_idx * (swatch_size + 10)
            y_swatch = y + row * (swatch_size + 5)
            rect = pygame.Rect(x, y_swatch, swatch_size, swatch_size)
            pygame.draw.rect(self.screen, col, rect)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)
            self.preset_color_rects.append((rect, col))

        y += ((len(PREDEFINED_COLORS) + cols - 1) // cols) * (swatch_size + 5) + 10

        # Display current color
        current_text = self.font.render("Current:", True, (0, 0, 0))
        self.screen.blit(current_text, (10, y))
        color_rect = pygame.Rect(80, y, 50, 25)
        pygame.draw.rect(self.screen, self.current_color, color_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), color_rect, 1)

    def handle_events(self):
        """Process all input events (keyboard, mouse, quit). Returns False if should quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # Keyboard presses
            if event.type == pygame.KEYDOWN:
                # Ctrl+S saves the canvas
                if event.mod & pygame.KMOD_CTRL and event.key == pygame.K_s:
                    self.save_canvas()
                # Number keys 1,2,3 change brush size
                if event.key in BRUSH_SIZES:
                    self.brush_size = BRUSH_SIZES[event.key]
                # F toggles fill/outline mode
                if event.key == pygame.K_f:
                    self.shape_filled = not self.shape_filled
                # Tool shortcuts
                if event.key == pygame.K_p:
                    self.tool = 'pencil'
                elif event.key == pygame.K_l:
                    self.tool = 'line'
                elif event.key == pygame.K_r:
                    self.tool = 'rect'
                elif event.key == pygame.K_c:
                    self.tool = 'circle'
                elif event.key == pygame.K_e:
                    self.tool = 'eraser'
                elif event.key == pygame.K_t:
                    self.tool = 'text'
                elif event.key == pygame.K_v:
                    self.tool = 'fill'
                elif event.key == pygame.K_k:
                    self.tool = 'color_picker'

                # Handle text input when text tool is active
                if self.text_input_active:
                    if event.key == pygame.K_RETURN:
                        self.commit_text()                # place text on canvas
                        self.text_input_active = False
                        self.text_mode = False
                    elif event.key == pygame.K_ESCAPE:
                        self.text_input_active = False    # cancel text
                        self.text_mode = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.text_string = self.text_string[:-1]
                    else:
                        if event.unicode and event.unicode.isprintable():
                            self.text_string += event.unicode
                    continue   # skip drawing updates while typing text

            # Mouse button down
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                # Check tool buttons clicks
                for tool, rect in self.tool_buttons.items():
                    if rect.collidepoint(mouse_pos):
                        self.tool = tool
                        if tool == 'text':
                            self.text_mode = True
                        else:
                            self.text_mode = False
                            self.text_input_active = False
                        break
                # Check brush size buttons
                for rect, size in self.brush_buttons:
                    if rect.collidepoint(mouse_pos):
                        self.brush_size = size
                # Check fill/outline toggle
                if self.fill_toggle_rect and self.fill_toggle_rect.collidepoint(mouse_pos):
                    self.shape_filled = not self.shape_filled
                # Check color swatches
                for rect, col in self.preset_color_rects:
                    if rect.collidepoint(mouse_pos):
                        self.current_color = col

                # If click is inside canvas area
                if CANVAS_RECT.collidepoint(mouse_pos):
                    canvas_x = mouse_pos[0] - CANVAS_RECT.x
                    canvas_y = mouse_pos[1] - CANVAS_RECT.y
                    if self.tool == 'fill':
                        flood_fill(self.canvas, canvas_x, canvas_y, self.current_color)
                    elif self.tool == 'color_picker':
                        try:
                            self.current_color = self.canvas.get_at((canvas_x, canvas_y))[:3]
                        except:
                            pass
                    elif self.tool == 'text':
                        if not self.text_input_active:
                            self.text_pos = (canvas_x, canvas_y)
                            self.text_string = ""
                            self.text_input_active = True
                    else:
                        # Start drawing for pencil, line, shapes, eraser
                        self.drawing = True
                        self.start_pos = (canvas_x, canvas_y)
                        self.last_pos = (canvas_x, canvas_y)
                        if self.tool in ['line','rect','circle','square','right_triangle',
                                         'equilateral_triangle','rhombus']:
                            self.preview_shape = (self.tool, self.start_pos, self.start_pos)

            # Mouse motion while drawing
            if event.type == pygame.MOUSEMOTION and self.drawing:
                if CANVAS_RECT.collidepoint(pygame.mouse.get_pos()):
                    cx = pygame.mouse.get_pos()[0] - CANVAS_RECT.x
                    cy = pygame.mouse.get_pos()[1] - CANVAS_RECT.y
                    cur = (cx, cy)
                    if self.tool == 'pencil':
                        if self.last_pos:
                            pygame.draw.line(self.canvas, self.current_color, self.last_pos, cur, self.brush_size)
                        self.last_pos = cur
                    elif self.tool == 'eraser':
                        if self.last_pos:
                            pygame.draw.line(self.canvas, BACKGROUND_COLOR, self.last_pos, cur, self.brush_size)
                        self.last_pos = cur
                    elif self.tool in ['line','rect','circle','square','right_triangle',
                                       'equilateral_triangle','rhombus']:
                        # Update preview as user drags
                        self.preview_shape = (self.tool, self.start_pos, cur)

            # Mouse button up: finalize drawing
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.drawing and CANVAS_RECT.collidepoint(pygame.mouse.get_pos()):
                    cx = pygame.mouse.get_pos()[0] - CANVAS_RECT.x
                    cy = pygame.mouse.get_pos()[1] - CANVAS_RECT.y
                    end = (cx, cy)
                    if self.tool in ['line','rect','circle','square','right_triangle',
                                     'equilateral_triangle','rhombus'] and self.start_pos:
                        self.draw_shape(self.tool, self.start_pos, end)
                self.drawing = False
                self.start_pos = None
                self.last_pos = None
                self.preview_shape = None

        return True

    def draw_shape(self, shape_type, start, end):
        """Draw a shape (line, rectangle, circle, square, triangle, rhombus) on the canvas."""
        x1, y1 = start
        x2, y2 = end
        rect = pygame.Rect(min(x1,x2), min(y1,y2), abs(x2-x1), abs(y2-y1))
        color = self.current_color
        width = 0 if self.shape_filled else self.brush_size   # 0 = filled shape

        if shape_type == 'line':
            pygame.draw.line(self.canvas, color, start, end, self.brush_size)
        elif shape_type == 'rect':
            pygame.draw.rect(self.canvas, color, rect, width)
        elif shape_type == 'circle':
            center = (rect.centerx, rect.centery)
            radius = max(rect.width, rect.height)//2
            pygame.draw.circle(self.canvas, color, center, radius, width)
        elif shape_type == 'square':
            side = min(rect.width, rect.height)
            pygame.draw.rect(self.canvas, color, (rect.x, rect.y, side, side), width)
        elif shape_type == 'right_triangle':
            pts = get_right_triangle_points(start, end)
            if pts:
                pygame.draw.polygon(self.canvas, color, pts, width)
        elif shape_type == 'equilateral_triangle':
            pts = get_equilateral_triangle(start, end)
            if pts:
                pygame.draw.polygon(self.canvas, color, pts, width)
        elif shape_type == 'rhombus':
            pts = get_rhombus_points(start, end)
            if pts:
                pygame.draw.polygon(self.canvas, color, pts, width)

    def commit_text(self):
        """Render typed text onto canvas at the stored text position."""
        if not self.text_pos or not self.text_string:
            return
        font = pygame.font.SysFont("Arial", 24)
        surf = font.render(self.text_string, True, self.current_color)
        x, y = self.text_pos
        # Center text vertically around click point
        self.canvas.blit(surf, (x, y - surf.get_height()//2))

    def draw_preview(self):
        """Draw temporary preview (line or shape) while mouse is being dragged."""
        if self.preview_shape:
            shape, start, end = self.preview_shape
            surf = self.canvas.copy()   # create a copy so we don't modify actual canvas
            x1,y1 = start
            x2,y2 = end
            rect = pygame.Rect(min(x1,x2), min(y1,y2), abs(x2-x1), abs(y2-y1))
            color = self.current_color
            width = 0 if self.shape_filled else self.brush_size

            # Draw shape on temporary surface
            if shape == 'line':
                pygame.draw.line(surf, color, start, end, self.brush_size)
            elif shape == 'rect':
                pygame.draw.rect(surf, color, rect, width)
            elif shape == 'circle':
                center = (rect.centerx, rect.centery)
                radius = max(rect.width, rect.height)//2
                pygame.draw.circle(surf, color, center, radius, width)
            elif shape == 'square':
                side = min(rect.width, rect.height)
                pygame.draw.rect(surf, color, (rect.x, rect.y, side, side), width)
            elif shape == 'right_triangle':
                pts = get_right_triangle_points(start, end)
                if pts:
                    pygame.draw.polygon(surf, color, pts, width)
            elif shape == 'equilateral_triangle':
                pts = get_equilateral_triangle(start, end)
                if pts:
                    pygame.draw.polygon(surf, color, pts, width)
            elif shape == 'rhombus':
                pts = get_rhombus_points(start, end)
                if pts:
                    pygame.draw.polygon(surf, color, pts, width)

            # Blit preview surface to screen
            self.screen.blit(surf, CANVAS_RECT)
        else:
            # No preview, just show canvas
            self.screen.blit(self.canvas, CANVAS_RECT)

    def save_canvas(self):
        """Save current canvas as PNG with timestamp in the same directory."""
        import os
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"canvas_{timestamp}.png"
        # Get directory where this script is located
        dir_path = os.path.dirname(os.path.abspath(__file__))
        fullpath = os.path.join(dir_path, filename)

        # Convert canvas to RGB surface (remove alpha channel for compatibility)
        rgb_surface = pygame.Surface((self.canvas.get_width(), self.canvas.get_height()))
        rgb_surface.blit(self.canvas, (0, 0))
        pygame.image.save(rgb_surface, fullpath)
        print(f"Saved: {fullpath}")

    def draw_text_input_cursor(self):
        """Draw a blinking cursor while text tool is active."""
        if self.text_input_active and self.text_pos:
            if pygame.time.get_ticks() % 1000 < 500:   # blink every 500 ms
                font = pygame.font.SysFont("Arial", 24)
                text_surface = font.render(self.text_string, True, (0,0,0))
                cursor_x = self.text_pos[0] + text_surface.get_width()
                cursor_y = self.text_pos[1] - text_surface.get_height()//2
                pygame.draw.line(self.screen, self.current_color,
                                 (cursor_x + CANVAS_RECT.x, cursor_y + CANVAS_RECT.y),
                                 (cursor_x + CANVAS_RECT.x, cursor_y + CANVAS_RECT.y + 20), 2)

    def run(self):
        """Main game loop."""
        running = True
        while running:
            running = self.handle_events()       # process input, returns False on quit
            self.screen.fill((255,255,255))     # clear screen
            self.draw_toolbar()                  # draw UI buttons
            self.draw_preview()                  # draw canvas + preview
            self.draw_text_input_cursor()        # draw blinking cursor if needed

            # Draw currently typed text while text input is active
            if self.text_input_active and self.text_pos:
                font = pygame.font.SysFont("Arial", 24)
                ts = font.render(self.text_string, True, self.current_color)
                self.screen.blit(ts, (self.text_pos[0] + CANVAS_RECT.x,
                                      self.text_pos[1] + CANVAS_RECT.y - ts.get_height()//2))

            pygame.display.flip()                # update the screen
            self.clock.tick(60)                  # limit to 60 frames per second

        pygame.quit()
        sys.exit()

# Start the application if this file is executed directly
if __name__ == "__main__":
    PaintApp().run()