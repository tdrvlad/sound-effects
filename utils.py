import yaml
import os
from paths import AUDIO_SAMPLES_DIR, AUDIO_SAMPLES_TIMESTAMPS_DIR, EFFECTS_DIR, AUDIO_FILE, TIMESTAMPS_FILE
from pydub import AudioSegment
from audio_player import AudioPlayer


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
        raise ValueError(f"Audio {sample_id}.mp3 does not exist in {AUDIO_SAMPLES_DIR}.")
    if not os.path.exists(timestamps_file):
        raise ValueError(
            f"Audio Timestamps {sample_id}.yaml does not exist in {AUDIO_SAMPLES_TIMESTAMPS_DIR}.")

    audio = load_audio(audio_file)
    sample_timestamps = load_yaml(timestamps_file)
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