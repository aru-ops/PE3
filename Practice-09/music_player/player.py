import pygame

class MusicPlayer:
    def __init__(self, tracks):
        self.tracks = tracks
        self.index = 0
        pygame.mixer.init()

    def play(self):
        pygame.mixer.music.load(self.tracks[self.index])
        pygame.mixer.music.play()

    def stop(self):
        pygame.mixer.music.stop()

    def next(self):
        self.index = (self.index + 1) % len(self.tracks)
        self.play()

    def prev(self):
        self.index = (self.index - 1) % len(self.tracks)
        self.play()

    def get_current_track(self):
        return self.tracks[self.index]