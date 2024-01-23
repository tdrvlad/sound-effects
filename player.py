import os
import time
from paths import EFFECTS_DIR, AUDIO_FILE, TIMESTAMPS_FILE, EFFECT_1_PIN, EFFECT_2_PIN, EFFECT_3_PIN, TIMESTAMPS_START, TIMESTAMPS_END, PANEL_LED_PIN, BUTTON_PIN_1
from utils import load_yaml, load_sample, load_effect
from pydub.playback import play
import threading
from pydub import AudioSegment
from rpi import RpiPin, RpiInput
import RPi.GPIO as GPIO


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
        callable_dict.update(create_sound_callable_dict(sound_timestamps_dict, pin))
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
            print(f"\nAction: {curr_time}")
            curr_action()
            print('\n')
            i += 1
        else:
            time.sleep(0.01)


def main(sample_id, intro_audio_path=None, outro_audio_path=None):
    GPIO.cleanup()

    led_pin = RpiPin(PANEL_LED_PIN)
    background_pin = RpiPin(EFFECT_1_PIN)
    background_pin.turn_on()

    # for pin_id in [EFFECT_1_PIN, EFFECT_2_PIN, EFFECT_3_PIN]:
    #     pin = RpiPin(pin_id)
    #     pin.turn_off()

    def action():
        led_pin.turn_off()
        background_pin.turn_off()
        play_effect(
            sample_id,
            intro_audio_path=intro_audio_path,
            outro_audio_path=outro_audio_path,
            background_pin=background_pin
        )
        led_pin.turn_on()
        background_pin.turn_on()

    button = RpiInput(BUTTON_PIN_1, action=action)

    try:
        led_pin.turn_on()
        background_pin.turn_on()
        while True:
            time.sleep(0.1)
            button.check_pressed()

    except Exception as e:
        raise e

    finally:
        led_pin.turn_off()
        background_pin.turn_on()
        GPIO.cleanup()


def play_effect(effect_id, intro_audio_path=None, outro_audio_path=None, background_pin=None):

    audio, timestamps = load_effect(effect_id)
    sounds = list(timestamps.keys())
    print(f'Loaded timestamps for sounds: {", ".join(sounds)}')
    if len(sounds) > 3:
        raise ValueError("System configured for only 3 sound effects")

    pin_mapping = {sound: pin for sound, pin in zip(sounds, [EFFECT_1_PIN, EFFECT_2_PIN, EFFECT_3_PIN])}
    audio_length = len(audio) / 1000.0  # Audio length in seconds

    pins = {
        sound: RpiPin(pin) for sound, pin in pin_mapping.items()
    }

    actions = create_sounds_callable_dict(timestamps, pins)

    if intro_audio_path:
        intro_audio = AudioSegment.from_mp3(intro_audio_path)
        intro_audio_player = AudioPlayer(intro_audio)
        intro_audio_player.play()

    audio_player = AudioPlayer(audio)

    audio_thread = threading.Thread(target=audio_player.play)
    led_thread = threading.Thread(target=control_leds, args=(actions, audio_player))

    audio_thread.start()
    led_thread.start()

    audio_thread.join()
    led_thread.join()

    if outro_audio_path:
        if background_pin is not None:
            background_pin.turn_on()

        outro_audio = AudioSegment.from_mp3(outro_audio_path)
        outro_audio_player = AudioPlayer(outro_audio)
        outro_audio_player.play()


def test_sample(sample_id):
    print("Test")
    audio, sample_timestamps = load_sample(sample_id)

    pin = RpiPin(EFFECT_1_PIN)
    actions = create_sound_callable_dict(sample_timestamps, pin)
    print(actions)

    audio_player = AudioPlayer(audio)
    audio_thread = threading.Thread(target=audio_player.play)
    led_thread = threading.Thread(target=control_leds, args=(actions, audio_player))

    audio_thread.start()
    led_thread.start()

    audio_thread.join()
    led_thread.join()


if __name__ == '__main__':
    test_sample('maxim_machine_gun')
    # test_sample('explosion')
    # main("battle_short")
    # main("battle_long_outro", intro_audio_path='./audio_samples/intro_mateias_doina_discurs.mp3')
    # main("battle_long", outro_audio_path='./audio_samples/outro_battle.mp3')
