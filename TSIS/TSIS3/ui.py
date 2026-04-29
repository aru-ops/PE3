# ui.py - User interface elements for Racer game (TSIS 3)
# Contains Button and TextInput classes for interactive menus
import pygame

class Button:
    """A clickable button that changes color when hovered over."""
    def __init__(self, x, y, w, h, text, color=(200, 200, 200), hover_color=(150, 150, 150)):
        """
        Initialize button with position, size, text, and colors.
        - x, y: top-left corner coordinates
        - w, h: width and height
        - text: button label
        - color: normal background color (light gray)
        - hover_color: color when mouse is over (darker gray)
        """
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.font = pygame.font.Font(None, 36)          # default system font, size 36

    def draw(self, surface):
        """Draw the button on the given surface. Changes color if mouse hovers."""
        mouse_pos = pygame.mouse.get_pos()              # get current mouse position
        # Choose hover color if mouse is inside button rectangle, else normal color
        current_color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(surface, current_color, self.rect)   # filled rectangle
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)    # black outline, 2px thick
        # Render and center the button text
        text_surf = self.font.render(self.text, True, (0, 0, 0))   # black text
        text_rect = text_surf.get_rect(center=self.rect.center)    # center text in button
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        """
        Check if the button was clicked.
        Returns True if the mouse button was pressed and cursor is inside button rect.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:   # left mouse button
            if self.rect.collidepoint(event.pos):
                return True
        return False

class TextInput:
    """A simple text input box where the user can type a name or other data."""
    def __init__(self, x, y, w, h):
        """
        Initialize text input box at position (x, y) with given width and height.
        """
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""                          # currently typed text
        self.font = pygame.font.Font(None, 36)  # same font as buttons

    def handle_event(self, event):
        """
        Process keyboard events to update the text.
        Supports backspace and printable characters (max length 15).
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]      # remove last character
            elif event.unicode.isprintable() and len(self.text) < 15:
                self.text += event.unicode      # add typed character

    def draw(self, surface):
        """
        Draw the input box with white background, black border, and current text.
        """
        pygame.draw.rect(surface, (255, 255, 255), self.rect)   # white background
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)      # black border
        text_surf = self.font.render(self.text, True, (0, 0, 0)) # render text
        surface.blit(text_surf, (self.rect.x + 10, self.rect.y + 10))  # draw with left padding