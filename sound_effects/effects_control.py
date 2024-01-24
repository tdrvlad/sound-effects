import time

from params import EFFECTS_MAP, TIMESTAMPS_START, TIMESTAMPS_END
from rpi import RpiPin


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


def create_sound_callable_dict(sound_timestamps_dict, pin: RpiPin):
    callable_dict = {}
    for start_time in sound_timestamps_dict[TIMESTAMPS_START]:
        callable_dict[start_time] = pin.turn_on
    for stop_time in sound_timestamps_dict[TIMESTAMPS_END]:
        callable_dict[stop_time] = pin.turn_off
    return dict(sorted(callable_dict.items()))