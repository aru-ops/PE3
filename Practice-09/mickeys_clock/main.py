import pygame
from clock import MickeyClock

pygame.init()

screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption("Mickey Clock")

clock = pygame.time.Clock()
mickey = MickeyClock(screen)

running = True
while running:
    screen.fill((255, 255, 255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    mickey.draw()

    pygame.display.flip()
    clock.tick(1)  # обновление каждую секунду

pygame.quit()