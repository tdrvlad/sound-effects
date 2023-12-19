import yaml
import os
from paths import AUDIO_SAMPLES_DIR, AUDIO_SAMPLES_TIMESTAMPS_DIR
from pydub import AudioSegment


def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


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

    audio = AudioSegment.from_mp3(audio_file)
    sample_timestamps = load_yaml(timestamps_file)
    return audio, sample_timestamps
