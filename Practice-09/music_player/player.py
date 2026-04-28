import pygame

class MusicPlayer:
    def __init__(self):
        pygame.mixer.init()

        self.playlist = [
    "music/sample_tracks/track1.wav",
    "music/sample_tracks/track2.wav",
    "music/sample_tracks/track3.wav"
]
        self.index = 0

    def play(self):
        pygame.mixer.music.load(self.playlist[self.index])
        pygame.mixer.music.play()

    def stop(self):
        pygame.mixer.music.stop()

    def next(self):
        self.index = (self.index + 1) % len(self.playlist)
        self.play()

    def prev(self):
        self.index = (self.index - 1) % len(self.playlist)
        self.play()