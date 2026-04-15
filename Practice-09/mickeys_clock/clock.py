import pygame
import datetime

class MickeyClock:
    def __init__(self, screen):
        self.screen = screen

        self.bg = pygame.image.load("images/background.png")
        self.mickey = pygame.image.load("images/micky.png")

        self.left_hand = pygame.image.load("images/left_hand.png")
        self.right_hand = pygame.image.load("images/right_hand.png")

        self.center = (self.bg.get_width() // 2, self.bg.get_height() // 2)

    def draw(self):
        now = datetime.datetime.now()
        minutes = now.minute
        seconds = now.second

        # углы (важно: минус чтобы шло по часовой)
        minute_angle = -minutes * 6
        second_angle = -seconds * 6

        # вращаем
        rotated_min = pygame.transform.rotate(self.right_hand, minute_angle)
        rotated_sec = pygame.transform.rotate(self.left_hand, second_angle)

        # центрируем
        min_rect = rotated_min.get_rect(center=self.center)
        sec_rect = rotated_sec.get_rect(center=self.center)

        # --- РИСУЕМ В ПРАВИЛЬНОМ ПОРЯДКЕ ---
        self.screen.blit(self.bg, (0, 0))

        # Микки поверх фона
        mickey_rect = self.mickey.get_rect(center=self.center)
        self.screen.blit(self.mickey, mickey_rect)

        # руки поверх Микки
        self.screen.blit(rotated_min, min_rect)
        self.screen.blit(rotated_sec, sec_rect)