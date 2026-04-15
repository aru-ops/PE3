import pygame
import math

def draw_hand(screen, image, angle, position):
    rotated = pygame.transform.rotate(image, angle)
    rect = rotated.get_rect(center=position)
    screen.blit(rotated, rect)

def draw_clock(screen, hand_img, minutes, seconds):
    center = (200, 200)

    # угол для минут
    min_angle = -(minutes * 6)  # 360 / 60 = 6
    sec_angle = -(seconds * 6)

    # рисуем руки
    draw_hand(screen, hand_img, min_angle, center)
    draw_hand(screen, hand_img, sec_angle, center)