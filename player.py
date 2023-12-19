import os
import time
from paths import RESULTS_DIR, AUDIO_FILE, TIMESTAMPS_FILE, EFFECT_1_PIN, EFFECT_2_PIN, EFFECT_3_PIN
from utils import load_yaml
from pydub.playback import play
import threading
from pydub import AudioSegment
from rpi import RpiPin


pin_mapping = {
    'ding': EFFECT_1_PIN,
    'doorbell': EFFECT_2_PIN
}


def control_leds(timestamps, audio_length, pins):
    start_time = time.time()
    while time.time() - start_time < audio_length:
        current_time = time.time() - start_time
        for sound, times in timestamps.items():
            if sound not in pins:
                raise ValueError(f"Sound {sound} has no pin associated.")
            pin = pins[sound]
            for start, stop in zip(times['start'], times['stop']):
                if start <= current_time < stop:
                    pin.turn_on()
                elif current_time >= stop:
                    pin.turn_off()


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
    print(pin_mapping)
    audio_length = len(audio) / 1000.0  # Audio length in seconds

    pins = {
        sound: RpiPin(pin) for sound, pin in pin_mapping.items()
    }
    print(pins)

    # Create and start threads
    # audio_thread = threading.Thread(target=play, args=(audio,))
    # led_thread = threading.Thread(target=control_leds, args=(timestamps, audio_length, pins))
    #
    # audio_thread.start()
    # led_thread.start()
    #
    # audio_thread.join()
    # led_thread.join()


if __name__ == '__main__':
    load_audio_and_effects("20231210203838")
