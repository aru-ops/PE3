import pygame
import sys
from player import MusicPlayer

pygame.init()

screen = pygame.display.set_mode((500, 200))
pygame.display.set_caption("Music Player")

font = pygame.font.SysFont(None, 36)

player = MusicPlayer([
    "music/track1.wav",
    "music/track2.wav"
])

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                player.play()
            elif event.key == pygame.K_s:
                player.stop()
            elif event.key == pygame.K_n:
                player.next()
            elif event.key == pygame.K_b:
                player.prev()
            elif event.key == pygame.K_q:
                pygame.quit()
                sys.exit()

    screen.fill((0, 0, 0))

    text = font.render(f"Track: {player.get_current_track()}", True, (255, 255, 255))
    screen.blit(text, (20, 80))

    pygame.display.flip()