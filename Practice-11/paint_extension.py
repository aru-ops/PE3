# paint_extension.py
import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
TOOLBAR_WIDTH = 150
CANVAS_WIDTH = SCREEN_WIDTH - TOOLBAR_WIDTH
CANVAS_HEIGHT = SCREEN_HEIGHT

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (150, 150, 150)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)

class Shape:
    """Base class for all drawable shapes"""
    class Type:
        SQUARE = 0
        RIGHT_TRIANGLE = 1
        EQUILATERAL_TRIANGLE = 2
        RHOMBUS = 3
        
    def __init__(self, shape_type, start_pos, end_pos, color, size=100):
        self.type = shape_type
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.color = color
        self.size = size
        
    def draw(self, screen):
        """Draw shape based on its type"""
        if self.type == Shape.Type.SQUARE:
            self.draw_square(screen)
        elif self.type == Shape.Type.RIGHT_TRIANGLE:
            self.draw_right_triangle(screen)
        elif self.type == Shape.Type.EQUILATERAL_TRIANGLE:
            self.draw_equilateral_triangle(screen)
        elif self.type == Shape.Type.RHOMBUS:
            self.draw_rhombus(screen)
            
    def draw_square(self, screen):
        """Draw a square using the end position as the opposite corner"""
        x1, y1 = self.start_pos
        x2, y2 = self.end_pos
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        size = min(width, height)  # Make it square
        x = min(x1, x2)
        y = min(y1, y2)
        pygame.draw.rect(screen, self.color, (x, y, size, size), 3)
        
    def draw_right_triangle(self, screen):
        """Draw a right triangle (90-degree angle at top-left)"""
        x1, y1 = self.start_pos
        x2, y2 = self.end_pos
        width = x2 - x1
        height = y2 - y1
        
        # Triangle vertices: top-left, top-right, bottom-left
        points = [(x1, y1), (x2, y1), (x1, y2)]
        pygame.draw.polygon(screen, self.color, points, 3)
        
    def draw_equilateral_triangle(self, screen):
        """Draw an equilateral triangle (all sides equal)"""
        x1, y1 = self.start_pos
        x2, y2 = self.end_pos
        
        # Calculate side length and height
        side_length = abs(x2 - x1)
        height = side_length * math.sqrt(3) / 2
        
        # Determine orientation based on mouse movement
        if y2 > y1:  # Pointing down
            points = [
                (x1, y1),  # Top vertex
                (x1 - side_length//2, y1 + height),  # Bottom left
                (x1 + side_length//2, y1 + height)   # Bottom right
            ]
        else:  # Pointing up
            points = [
                (x1, y1),  # Bottom vertex
                (x1 - side_length//2, y1 - height),  # Top left
                (x1 + side_length//2, y1 - height)   # Top right
            ]
        pygame.draw.polygon(screen, self.color, points, 3)
        
    def draw_rhombus(self, screen):
        """Draw a rhombus (diamond shape)"""
        center_x, center_y = self.start_pos
        x2, y2 = self.end_pos
        
        # Calculate width and height from mouse position
        width = abs(x2 - center_x)
        height = abs(y2 - center_y)
        
        # Four vertices of rhombus
        points = [
            (center_x, center_y - height),  # Top
            (center_x + width, center_y),   # Right
            (center_x, center_y + height),  # Bottom
            (center_x - width, center_y)    # Left
        ]
        pygame.draw.polygon(screen, self.color, points, 3)

class PaintApp:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Paint - Shape Drawer")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        
        # Canvas surface
        self.canvas = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT))
        self.canvas.fill(WHITE)
        
        # Drawing state
        self.current_shape_type = Shape.Type.SQUARE
        self.current_color = BLACK
        self.drawing = False
        self.start_pos = None
        self.shapes = []
        self.preview_shape = None
        
        # Toolbar buttons
        self.buttons = {}
        self.create_toolbar()
        
    def create_toolbar(self):
        """Create toolbar with shape buttons"""
        y_offset = 50
        button_height = 40
        
        # Shape buttons
        shapes = [
            ("Square", Shape.Type.SQUARE),
            ("Right Triangle", Shape.Type.RIGHT_TRIANGLE),
            ("Equilateral", Shape.Type.EQUILATERAL_TRIANGLE),
            ("Rhombus", Shape.Type.RHOMBUS)
        ]
        
        for name, shape_type in shapes:
            rect = pygame.Rect(SCREEN_WIDTH - TOOLBAR_WIDTH + 10, y_offset, 
                              TOOLBAR_WIDTH - 20, button_height)
            self.buttons[shape_type] = {"rect": rect, "name": name}
            y_offset += button_height + 10
            
        # Color buttons
        colors = [
            (BLACK, "Black"),
            (RED, "Red"),
            (GREEN, "Green"),
            (BLUE, "Blue"),
            (YELLOW, "Yellow")
        ]
        
        y_offset += 20
        for color, name in colors:
            rect = pygame.Rect(SCREEN_WIDTH - TOOLBAR_WIDTH + 10, y_offset,
                              TOOLBAR_WIDTH - 20, 30)
            self.buttons[color] = {"rect": rect, "name": name, "color": color}
            y_offset += 40
            
        # Clear button
        clear_rect = pygame.Rect(SCREEN_WIDTH - TOOLBAR_WIDTH + 10, SCREEN_HEIGHT - 80,
                                TOOLBAR_WIDTH - 20, 40)
        self.buttons["clear"] = {"rect": clear_rect, "name": "Clear Canvas"}
        
    def draw_toolbar(self):
        """Draw the toolbar interface"""
        # Toolbar background
        pygame.draw.rect(self.screen, GRAY, 
                        (SCREEN_WIDTH - TOOLBAR_WIDTH, 0, TOOLBAR_WIDTH, SCREEN_HEIGHT))
        pygame.draw.line(self.screen, BLACK, 
                        (SCREEN_WIDTH - TOOLBAR_WIDTH, 0), 
                        (SCREEN_WIDTH - TOOLBAR_WIDTH, SCREEN_HEIGHT), 3)
        
        # Title
        title = self.font.render("SHAPES", True, BLACK)
        self.screen.blit(title, (SCREEN_WIDTH - TOOLBAR_WIDTH + 10, 10))
        
        # Draw all buttons
        for key, btn in self.buttons.items():
            # Highlight current selection
            if key == self.current_shape_type:
                pygame.draw.rect(self.screen, DARK_GRAY, btn["rect"])
            elif key == self.current_color:
                pygame.draw.rect(self.screen, DARK_GRAY, btn["rect"])
            else:
                pygame.draw.rect(self.screen, WHITE, btn["rect"])
                
            pygame.draw.rect(self.screen, BLACK, btn["rect"], 2)
            
            # Draw text or color swatch
            if "color" in btn:
                pygame.draw.rect(self.screen, btn["color"], 
                               (btn["rect"].x + 5, btn["rect"].y + 5, 20, 20))
                text = self.font.render(btn["name"], True, BLACK)
                self.screen.blit(text, (btn["rect"].x + 30, btn["rect"].y + 8))
            else:
                text = self.font.render(btn["name"], True, BLACK)
                text_rect = text.get_rect(center=btn["rect"].center)
                self.screen.blit(text, text_rect)
                
    def handle_click(self, pos):
        """Handle mouse clicks on toolbar"""
        x, y = pos
        
        # Check if click is on toolbar
        if x > SCREEN_WIDTH - TOOLBAR_WIDTH:
            for key, btn in self.buttons.items():
                if btn["rect"].collidepoint(x, y):
                    if key == "clear":
                        self.clear_canvas()
                    elif key in [Shape.Type.SQUARE, Shape.Type.RIGHT_TRIANGLE,
                                Shape.Type.EQUILATERAL_TRIANGLE, Shape.Type.RHOMBUS]:
                        self.current_shape_type = key
                    elif key in [BLACK, RED, GREEN, BLUE, YELLOW]:
                        self.current_color = key
                    return True
        return False
        
    def clear_canvas(self):
        """Clear all shapes from canvas"""
        self.canvas.fill(WHITE)
        self.shapes.clear()
        
    def start_drawing(self, pos):
        """Start drawing a new shape"""
        x, y = pos
        if x < CANVAS_WIDTH:  # Only draw on canvas area
            self.drawing = True
            self.start_pos = (x, y)
            
    def update_preview(self, current_pos):
        """Update shape preview while dragging"""
        if self.drawing and self.start_pos:
            self.preview_shape = Shape(
                self.current_shape_type,
                self.start_pos,
                current_pos,
                self.current_color
            )
            
    def finish_drawing(self, end_pos):
        """Finish drawing and add shape to canvas"""
        if self.drawing and self.start_pos:
            shape = Shape(
                self.current_shape_type,
                self.start_pos,
                end_pos,
                self.current_color
            )
            shape.draw(self.canvas)  # Draw permanently on canvas
            self.shapes.append(shape)
            self.drawing = False
            self.start_pos = None
            self.preview_shape = None
            
    def draw(self):
        """Draw everything to screen"""
        # Draw canvas
        self.screen.blit(self.canvas, (0, 0))
        
        # Draw preview shape (while dragging)
        if self.preview_shape:
            # Create temporary surface for preview
            temp_surface = self.canvas.copy()
            self.preview_shape.draw(temp_surface)
            self.screen.blit(temp_surface, (0, 0))
            
        # Draw toolbar on top
        self.draw_toolbar()
        
        # Draw instructions
        instructions = [
            "INSTRUCTIONS:",
            "Click shape button",
            "Click color button",
            "Drag on canvas to draw",
            "Clear to reset"
        ]
        y = SCREEN_HEIGHT - 150
        for instruction in instructions:
            text = self.font.render(instruction, True, BLACK)
            self.screen.blit(text, (10, y))
            y += 20
            
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        if not self.handle_click(event.pos):
                            self.start_drawing(event.pos)
                            
                elif event.type == pygame.MOUSEMOTION:
                    self.update_preview(event.pos)
                    
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.finish_drawing(event.pos)
                        
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = PaintApp()
    app.run()