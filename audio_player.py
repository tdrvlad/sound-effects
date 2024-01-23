import time

from pydub.playback import play


class AudioPlayer:
    def __init__(self, audio, delay=-0.6, volume_change=0):
        self.audio = audio

        if volume_change:
            self.audio = self.audio + volume_change

        self.play_obj = None
        self.start_time = None
        self.delay = delay

    def play(self):
        self.start_time = time.time()
        self.play_obj = play(self.audio)

    def current_playback_time(self):
        if self.start_time is None:
            return 0
        current_playback_time = time.time() - self.start_time + self.delay
        return current_playback_time