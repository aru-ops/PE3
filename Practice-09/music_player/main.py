import pygame
from player import MusicPlayer

pygame.init()

screen = pygame.display.set_mode((400, 200))
pygame.display.set_caption("Music Player")

player = MusicPlayer()

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                player.play()
            elif event.key == pygame.K_s:
                player.stop()
            elif event.key == pygame.K_n:
                player.next()
            elif event.key == pygame.K_b:
                player.prev()

    screen.fill((30, 30, 30))
    pygame.display.flip()

pygame.quit()