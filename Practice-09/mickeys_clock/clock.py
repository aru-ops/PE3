import pygame
import datetime
import os

class MickeyClock:
    def __init__(self, screen):
        self.screen = screen

        base = os.path.dirname(__file__)
        img_path = os.path.join(base, "images")

        self.bg = pygame.image.load(os.path.join(img_path, "clock.png"))
        self.mickey = pygame.image.load(os.path.join(img_path, "mikkey.png"))

        self.left_hand = pygame.image.load(os.path.join(img_path, "hand_left_centered.png"))
        self.right_hand = pygame.image.load(os.path.join(img_path, "hand_right_centered.png"))

        self.center = (self.bg.get_width() // 2, self.bg.get_height() // 2)

    def draw(self):
        now = datetime.datetime.now()
        minutes = now.minute
        seconds = now.second

        minute_angle = -minutes * 6
        second_angle = -seconds * 6

        rotated_min = pygame.transform.rotate(self.right_hand, minute_angle)
        rotated_sec = pygame.transform.rotate(self.left_hand, second_angle)

        min_rect = rotated_min.get_rect(center=self.center)
        sec_rect = rotated_sec.get_rect(center=self.center)

        self.screen.blit(self.bg, (0, 0))

        mickey_rect = self.mickey.get_rect(center=self.center)
        self.screen.blit(self.mickey, mickey_rect)

        self.screen.blit(rotated_min, min_rect)
        self.screen.blit(rotated_sec, sec_rect)