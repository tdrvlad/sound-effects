import time

import yaml
import os
from params import AUDIO_SAMPLES_DIR, AUDIO_SAMPLES_TIMESTAMPS_DIR, EFFECTS_DIR, AUDIO_FILE, TIMESTAMPS_FILE, \
    TIMESTAMPS_START, TIMESTAMPS_END, EFFECTS_MAP
from pydub import AudioSegment
from audio_player import AudioPlayer
from rpi import RpiPin


def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def load_audio(audio_path):
    audio = AudioSegment.from_mp3(audio_path)
    return audio


def write_yaml(file_path, content):
    with open(file_path, 'w') as file:
        yaml.dump(content, file)


def load_sample(sample_id):
    audio_file = os.path.join(AUDIO_SAMPLES_DIR, f'{sample_id}.mp3')
    timestamps_file = os.path.join(AUDIO_SAMPLES_TIMESTAMPS_DIR, f'{sample_id}.yaml')

    if not os.path.exists(audio_file):
        raise ValueError(f"Audio {sample_id} does not exist in {AUDIO_SAMPLES_DIR}.")
    if os.path.exists(timestamps_file):
        sample_timestamps = load_yaml(timestamps_file)
    else:
        sample_timestamps = {TIMESTAMPS_START: [], TIMESTAMPS_END: []}
        print(f"No audio Timestamps found for {sample_id} in {AUDIO_SAMPLES_TIMESTAMPS_DIR}.")

    audio = load_audio(audio_file)
    return audio, sample_timestamps


def load_effect(effect_id, return_audio=False):
    effect_dir = os.path.join(EFFECTS_DIR, effect_id)
    if not os.path.exists(effect_dir):
        raise ValueError(f"Effect {effect_id} not found.")
    audio_file = os.path.join(effect_dir, f'{AUDIO_FILE}.mp3')
    if not os.path.exists(audio_file):
        raise ValueError(f"Audios {audio_file} not found.")
    timestamps_file = os.path.join(effect_dir, f'{TIMESTAMPS_FILE}.yaml')
    if not os.path.exists(timestamps_file):
        raise ValueError(f"Timestamps {timestamps_file} not found.")

    audio_player = get_audio_player(audio_file)
    timestamps = load_yaml(timestamps_file)

    return audio_player, timestamps


def add_delay_to_timestamps(timestamps_dict, delta):
    for key, time_data in timestamps_dict.items():
        for time_type in ["start", "stop"]:
            time_data[time_type] = [timestamp + delta for timestamp in time_data[time_type]]


def get_audio_player(audio_path):
    if audio_path:
        print(f"Loading audio {audio_path}.")
        audio = AudioSegment.from_mp3(audio_path)
        audio_player = AudioPlayer(audio)
        return audio_player
    return None


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
        if sound not in pins:
            print(f"No GPIO pin associated to sound {sound}")
            pin = None
        else:
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


def get_effects_pins(effects_map=EFFECTS_MAP):
    pin_instances = {}
    effects_pins = {}

    for effect, pin_id in effects_map.items():
        if pin_id not in pin_instances:
            pin_instances[pin_id] = RpiPin(pin_id)

        effects_pins[effect] = pin_instances[pin_id]
    return effects_pins