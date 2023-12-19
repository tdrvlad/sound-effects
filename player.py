import os
import time
from paths import RESULTS_DIR, AUDIO_FILE, TIMESTAMPS_FILE, EFFECT_1_PIN, EFFECT_2_PIN, EFFECT_3_PIN, TIMESTAMPS_START, TIMESTAMPS_END
from utils import load_yaml, load_sample
from pydub.playback import play
import threading
from pydub import AudioSegment
from rpi import RpiPin


pin_mapping = {
    'ding': EFFECT_1_PIN,
    'doorbell': EFFECT_2_PIN
}


class AudioPlayer:
    def __init__(self, audio):
        self.audio = audio
        self.play_obj = None
        self.start_time = None

    def play(self):
        self.start_time = time.time()
        self.play_obj = play(self.audio)

    def current_playback_time(self):
        if self.start_time is None:
            return 0
        return time.time() - self.start_time


def create_sound_callable_dict(sound_timestamps_dict, pin: RpiPin):
    callable_dict = {}
    for start_time in sound_timestamps_dict[TIMESTAMPS_START]:
        callable_dict[start_time] = pin.turn_on
    for stop_time in sound_timestamps_dict[TIMESTAMPS_END]:
        callable_dict[stop_time] = pin.turn_off
    return dict(sorted(callable_dict.items()))


def create_sounds_callable_dict(sounds_timestamps_dict, pins):
    callable_dict = {}
    for sound, sound_timestamps_dict in sounds_timestamps_dict.items():
        pin = pins[sound]
        callable_dict.extend(create_sound_callable_dict(sound_timestamps_dict, pin))
    return dict(sorted(callable_dict.items()))


def control_leds(callable_dict, audio_player):
    while audio_player.current_playback_time() == 0:
        time.sleep(0.001)  # Wait for audio to start playing

    i = 0
    while i < len(callable_dict):
        curr_timestamp = list(callable_dict.keys())[i]
        curr_action = callable_dict[curr_timestamp]

        curr_time = audio_player.current_playback_time()
        if curr_timestamp <= curr_time:
            print(f"Action: {curr_time}")
            curr_action()
            i += 1
        else:
            time.sleep(0.01)


def load_audio_and_effects(sample_id):
    sample_dir = os.path.join(RESULTS_DIR, sample_id)
    if not os.path.exists(sample_dir):
        raise ValueError(f"Sample {sample_id} not found.")
    audio_file = os.path.join(sample_dir, f'{AUDIO_FILE}.mp3')
    if not os.path.exists(audio_file):
        raise ValueError(f"Audios {audio_file} not found.")
    timestamps_file = os.path.join(sample_dir, f'{TIMESTAMPS_FILE}.yaml')
    if not os.path.exists(timestamps_file):
        raise ValueError(f"Timestamps {timestamps_file} not found.")

    audio = AudioSegment.from_mp3(audio_file)
    timestamps = load_yaml(timestamps_file)

    sounds = list(timestamps.keys())
    print(f'Loaded timestamps for sounds: {", ".join(sounds)}')
    if len(sounds) > 3:
        raise ValueError("System configured for only 3 sound effects")

    pin_mapping = {sound: pin for sound, pin in zip(sounds, [EFFECT_1_PIN, EFFECT_2_PIN, EFFECT_3_PIN])}
    audio_length = len(audio) / 1000.0  # Audio length in seconds

    pins = {
        sound: RpiPin(pin) for sound, pin in pin_mapping.items()
    }

    actions = create_callable_dict(timestamps, pins)

    audio_player = AudioPlayer(audio)

    audio_thread = threading.Thread(target=audio_player.play)
    led_thread = threading.Thread(target=control_leds, args=(actions, audio_player))

    audio_thread.start()
    led_thread.start()

    audio_thread.join()
    led_thread.join()


def test_sample(sample_id):
    audio, sample_timestamps = load_sample(sample_id)

    pin = RpiPin(EFFECT_1_PIN)
    actions = create_sound_callable_dict(sample_timestamps, pin)

    audio_player = AudioPlayer(audio)
    audio_thread = threading.Thread(target=audio_player.play)
    led_thread = threading.Thread(target=control_leds, args=(actions, audio_player))

    audio_thread.start()
    led_thread.start()

    audio_thread.join()
    led_thread.join()


if __name__ == '__main__':
    # load_audio_and_effects("20231219192311")
    test_sample('ding')
