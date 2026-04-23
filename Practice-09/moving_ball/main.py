import pygame
import sys
from ball import Ball

pygame.init()

WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moving Ball")

clock = pygame.time.Clock()

ball = Ball(300, 200)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        ball.move(-20, 0, WIDTH, HEIGHT)
    if keys[pygame.K_RIGHT]:
        ball.move(20, 0, WIDTH, HEIGHT)
    if keys[pygame.K_UP]:
        ball.move(0, -20, WIDTH, HEIGHT)
    if keys[pygame.K_DOWN]:
        ball.move(0, 20, WIDTH, HEIGHT)

    screen.fill((255, 255, 255))
    ball.draw(screen)

    pygame.display.flip()
    clock.tick(10)