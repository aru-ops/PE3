import pygame
import sys
import datetime
from clock import draw_clock

pygame.init()

WIDTH, HEIGHT = 400, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mickey Clock")

clock = pygame.time.Clock()

# загрузка изображения руки
hand_img = pygame.image.load("images/mickeyclock.jpeg")
hand_img = pygame.transform.scale(hand_img, (100, 100))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((255, 255, 255))

    now = datetime.datetime.now()
    minutes = now.minute
    seconds = now.second

    draw_clock(screen, hand_img, minutes, seconds)

    pygame.display.flip()
    clock.tick(1)  # обновление раз в секунду