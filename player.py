import os
from paths import RESULTS_DIR, AUDIO_FILE, TIMESTAMPS_FILE
from utils import load_yaml
from pydub.playback import play
from pydub import AudioSegment


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
    play(audio)


if __name__ == '__main__':
    load_audio_and_effects("20231210203838")
