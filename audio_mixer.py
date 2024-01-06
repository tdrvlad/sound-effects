from paths import EFFECTS_DIR, RECIPES_DIR, RECIPE_LENGTH, RECIPE_SAMPLES, RECIPE_SAMPLE_NAME, RECIPE_SAMPLE_FREQUENCY, \
    RECIPE_SAMPLE_FREQUENCY_MIN, RECIPE_SAMPLE_FREQUENCY_MAX, TIMESTAMPS_START, TIMESTAMPS_END
import os
from pydub import AudioSegment
from datetime import datetime
from collections import defaultdict
import random
from typing import Literal

from utils import load_yaml, write_yaml, load_sample, load_audio, load_effect, add_delay_to_timestamps


def mix_audio(recipe_name):
    recipe_file = os.path.join(RECIPES_DIR, f'{recipe_name}.yaml')
    if not os.path.exists(recipe_file):
        raise ValueError(f"Recipe {recipe_name} does not exist in {RECIPES_DIR}.")

    output_dir = os.path.join(EFFECTS_DIR, f'{recipe_name}_{datetime.now().strftime("%Y%m%d%H%M%S")}')
    os.makedirs(output_dir, exist_ok=True)

    output_audio_file = os.path.join(output_dir, 'output.mp3')
    output_timestamps_file = os.path.join(output_dir, 'timestamps.yaml')

    recipe = load_yaml(recipe_file)
    mixed_audio = AudioSegment.silent(duration=recipe[RECIPE_LENGTH] * 1000)
    timestamps = {}
    samples_names = set([])

    for sample in recipe[RECIPE_SAMPLES]:
        sample_id = sample[RECIPE_SAMPLE_NAME]
        audio, sample_timestamps = load_sample(sample_id)

        sample_timestamps_start = sample_timestamps[TIMESTAMPS_START]
        sample_timestamps_end = sample_timestamps[TIMESTAMPS_END]

        frequency_min = sample[RECIPE_SAMPLE_FREQUENCY][RECIPE_SAMPLE_FREQUENCY_MIN]
        frequency_max = sample[RECIPE_SAMPLE_FREQUENCY][RECIPE_SAMPLE_FREQUENCY_MAX]

        last_timestamp = 0
        timestamps[sample[RECIPE_SAMPLE_NAME]] = defaultdict(list)

        while last_timestamp < recipe[RECIPE_LENGTH]:
            start = random.uniform(last_timestamp + frequency_min, last_timestamp + frequency_max)
            mixed_audio = mixed_audio.overlay(audio, position=start * 1000)
            last_timestamp = start
            timestamps_start = [start + ts for ts in sample_timestamps_start if start + ts < recipe[RECIPE_LENGTH]]
            timestamps_end = [start + ts for ts in sample_timestamps_end if start + ts < recipe[RECIPE_LENGTH]]

            timestamps[sample[RECIPE_SAMPLE_NAME]][TIMESTAMPS_START].extend(timestamps_start)
            timestamps[sample[RECIPE_SAMPLE_NAME]][TIMESTAMPS_END].extend(timestamps_end)

        timestamps[sample[RECIPE_SAMPLE_NAME]] = dict(timestamps[sample[RECIPE_SAMPLE_NAME]])
        samples_names.add(RECIPE_SAMPLE_NAME)

    mixed_audio.export(output_audio_file, format='mp3')
    write_yaml(output_timestamps_file, timestamps)

    return mixed_audio, timestamps


def add_audio_to_effect(audio_path, effect_id, position: Literal["before", "after", "overlay"]="before"):
    output_dir = os.path.join(EFFECTS_DIR, f'{os.path.basename(audio_path)}_{effect_id}')
    os.makedirs(output_dir, exist_ok=True)

    output_audio_file = os.path.join(output_dir, 'output.mp3')
    output_timestamps_file = os.path.join(output_dir, 'timestamps.yaml')

    effect_audio, effect_timestamps = load_effect(effect_id)
    audio = load_audio(audio_path)

    if position == "before":
        result_audio = audio + effect_audio
        add_delay_to_timestamps(effect_timestamps, delta=len(audio) / 1000.0)
    elif position == "after":
        result_audio = effect_audio + audio
    elif position == "overlay":
        result_audio = effect_audio.overlay(audio, position=0)
    else:
        raise ValueError("Specify position for adding audio.")

    result_audio.export(output_audio_file, format='mp3')
    write_yaml(output_timestamps_file, effect_timestamps)


if __name__ == '__main__':
    # audio, timestamps = mix_audio('battle1')
    add_audio_to_effect("./audio_samples/ww1_charge_1.mp3", "ww1_charge_2.mp3_battle1_20231219231714", position="before")