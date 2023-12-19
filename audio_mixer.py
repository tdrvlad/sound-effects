from paths import AUDIO_SAMPLES_DIR, AUDIO_SAMPLES_TIMESTAMPS_DIR, RESULTS_DIR, RECIPES_DIR
import os
import yaml
from pydub import AudioSegment
from datetime import datetime
from collections import defaultdict
import random

RECIPE_LENGTH = 'length'
RECIPE_SAMPLES = 'samples'
RECIPE_SAMPLE_NAME = 'name'
RECIPE_SAMPLE_FREQUENCY = 'frequency_range'
RECIPE_SAMPLE_FREQUENCY_MIN = 'min'
RECIPE_SAMPLE_FREQUENCY_MAX = 'max'
TIMESTAMPS_START = 'start'
TIMESTAMPS_END = 'stop'


def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def write_yaml(file_path, content):
    with open(file_path, 'w') as file:
        yaml.dump(content, file)


def mix_audio(recipe_name):
    recipe_file = os.path.join(RECIPES_DIR, f'{recipe_name}.yaml')
    if not os.path.exists(recipe_file):
        raise ValueError(f"Recipe {recipe_name} does not exist in {RECIPES_DIR}.")

    output_dir = os.path.join(RESULTS_DIR, datetime.now().strftime('%Y%m%d%H%M%S'))
    os.makedirs(output_dir, exist_ok=True)

    output_audio_file = os.path.join(output_dir, 'output.mp3')
    output_timestamps_file = os.path.join(output_dir, 'timestamps.yaml')

    recipe = load_yaml(recipe_file)
    mixed_audio = AudioSegment.silent(duration=recipe[RECIPE_LENGTH] * 1000)
    timestamps = {}
    samples_names = set([])

    for sample in recipe[RECIPE_SAMPLES]:
        audio_file = os.path.join(AUDIO_SAMPLES_DIR, f'{sample[RECIPE_SAMPLE_NAME]}.mp3')
        timestamps_file = os.path.join(AUDIO_SAMPLES_TIMESTAMPS_DIR, f'{sample[RECIPE_SAMPLE_NAME]}.yaml')

        if not os.path.exists(audio_file):
            raise ValueError(f"Audio {sample[RECIPE_SAMPLE_NAME]}.mp3 does not exist in {AUDIO_SAMPLES_DIR}.")
        if not os.path.exists(timestamps_file):
            raise ValueError(f"Audio Timestamps {sample[RECIPE_SAMPLE_NAME]}.yaml does not exist in {AUDIO_SAMPLES_TIMESTAMPS_DIR}.")

        audio = AudioSegment.from_mp3(audio_file)
        sample_timestamps = load_yaml(timestamps_file)

        sample_timestamps_start = sample_timestamps[TIMESTAMPS_START]
        sample_timestamps_end = sample_timestamps[TIMESTAMPS_END]

        frequency_min = sample[RECIPE_SAMPLE_FREQUENCY][RECIPE_SAMPLE_FREQUENCY_MIN]
        frequency_max = sample[RECIPE_SAMPLE_FREQUENCY][RECIPE_SAMPLE_FREQUENCY_MAX]

        last_timestamp = 0
        timestamps[sample[RECIPE_SAMPLE_NAME]] = defaultdict(list)

        while last_timestamp < recipe[RECIPE_LENGTH]:
            start = random.uniform(last_timestamp + frequency_min, last_timestamp + frequency_max)
            mixed_audio = mixed_audio.overlay(audio, position=start * 1000)
            last_timestamp += start
            timestamps[sample[RECIPE_SAMPLE_NAME]][TIMESTAMPS_START].extend([start + ts for ts in sample_timestamps_start])
            timestamps[sample[RECIPE_SAMPLE_NAME]][TIMESTAMPS_END].extend([start + ts for ts in sample_timestamps_end])

        timestamps[sample[RECIPE_SAMPLE_NAME]] = dict(timestamps[sample[RECIPE_SAMPLE_NAME]])
        samples_names.add(RECIPE_SAMPLE_NAME)

    mixed_audio.export(output_audio_file, format='mp3')
    write_yaml(output_timestamps_file, timestamps)

    return mixed_audio, timestamps


if __name__ == '__main__':
    audio, timestamps = mix_audio('demo_bells')