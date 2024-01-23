import time
from audio_player import AudioPlayer
from paths import EFFECTS_MAP, EFFECT_1_PIN, TIMESTAMPS_START, TIMESTAMPS_END, PANEL_LED_PIN, BUTTON_PIN_1, BUTTON_PIN_2, BUTTON_PIN_3
from utils import load_sample, load_effect, get_audio_player
import threading
from rpi import RpiPin, RpiInput
import RPi.GPIO as GPIO


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


# def main(effect_id, intro_audio_path=None, outro_audio_path=None):
#     print("Initializing effects.")
#     led_pin = RpiPin(PANEL_LED_PIN, reverse=False)
#
#     effects_pins = get_effects_pins(EFFECTS_MAP)
#
#     audio_player, timestamps = load_effect(effect_id)
#     actions = create_sounds_callable_dict(timestamps, effects_pins)
#
#     intro_audio_player = get_audio_player(intro_audio_path)
#     outro_audio_player = get_audio_player(outro_audio_path)
#
#     if not 'background' in effects_pins:
#         raise ValueError('No GPIO pin defined for background')
#
#     background_pin = effects_pins['background']
#     background_pin.turn_on()
#
#     print(f"Loaded effects: {', '.join(effects_pins.keys())}")
#
#     def action():
#         led_pin.turn_off()
#         play_effect(
#             actions=actions,
#             effects_audio_player=audio_player,
#             intro_audio_player=intro_audio_player,
#             outro_audio_player=outro_audio_player,
#             background_pin=background_pin
#         )
#         led_pin.turn_on()
#
#     button = RpiInput(BUTTON_PIN_1, action=action)
#
#     try:
#         led_pin.turn_on()
#         print('Ready.')
#         while True:
#             time.sleep(0.1)
#             button.check_pressed()
#
#     except Exception as e:
#         raise e
#
#     finally:
#         led_pin.turn_off()
#         background_pin.turn_on()
#         GPIO.cleanup()


def main(effect_id, audio_paths):
    print("Initializing effects.")
    led_pin = RpiPin(PANEL_LED_PIN, reverse=False)

    effects_pins = get_effects_pins(EFFECTS_MAP)

    audio_player, timestamps = load_effect(effect_id)
    actions = create_sounds_callable_dict(timestamps, effects_pins)

    # Load audio players for each intro and outro
    audio_players = {}
    for button, paths in audio_paths.items():
        intro_path, outro_path = paths
        audio_players[button] = (
            get_audio_player(intro_path),
            get_audio_player(outro_path)
        )

    if not 'background' in effects_pins:
        raise ValueError('No GPIO pin defined for background')

    background_pin = effects_pins['background']
    background_pin.turn_on()

    print(f"Loaded effects: {', '.join(effects_pins.keys())}")

    def action(button):
        led_pin.turn_off()
        intro_audio_player, outro_audio_player = audio_players[button]
        play_effect(
            actions=actions,
            effects_audio_player=audio_player,
            intro_audio_player=intro_audio_player,
            outro_audio_player=outro_audio_player,
            background_pin=background_pin
        )
        led_pin.turn_on()

    buttons_actions = {
        BUTTON_PIN_1: lambda: action(BUTTON_PIN_1),
        BUTTON_PIN_2: lambda: action(BUTTON_PIN_2),
        BUTTON_PIN_3: lambda: action(BUTTON_PIN_3)
    }

    buttons = []
    for pin, button_action in buttons_actions.items():
        buttons .append(RpiInput(pin, action=button_action))

    try:
        led_pin.turn_on()
        print('Ready.')
        while True:
            time.sleep(0.1)
            for button in buttons :
                button.check_pressed()

    except Exception as e:
        raise e

    finally:
        led_pin.turn_off()
        background_pin.turn_on()
        GPIO.cleanup()



def play_effect(actions, effects_audio_player, intro_audio_player=None, outro_audio_player=None, background_pin=None, background_while_intro=False, background_while_outro=True):

    print("Playing effect.")
    if intro_audio_player:
        print("Playing intro.")
        if not background_while_intro:
            background_pin.turn_off()
        intro_audio_player.play()
    background_pin.turn_off()

    audio_thread = threading.Thread(target=effects_audio_player.play)
    led_thread = threading.Thread(target=control_leds, args=(actions, effects_audio_player))

    audio_thread.start()
    led_thread.start()

    audio_thread.join()
    led_thread.join()

    if outro_audio_player:
        print("Playing outro.")
        if background_while_outro:
            background_pin.turn_on()
        outro_audio_player.play()
    background_pin.turn_on()




if __name__ == '__main__':
    # test_sample('maxim_machine_gun')
    # test_sample('explosion')
    # main("battle_short")

    audio_paths = {
        BUTTON_PIN_1: ("./audio_samples/intro_ro.mp3", "./audio_samples/outro_battle.mp3"),
        BUTTON_PIN_2: ("./audio_samples/intro_en.mp3", "./audio_samples/outro_battle.mp3"),
        BUTTON_PIN_3: ("./audio_samples/intro_doina.mp3", "./audio_samples/outro_battle.mp3"),
    }
    main(effect_id="battle_v2", audio_paths=audio_paths)



    # main("battle_v2",  intro_audio_path='./audio_samples/doina_short.mp3', outro_audio_path='./audio_samples/outro_battle.mp3')
    # main("battle_long", outro_audio_path='./audio_samples/outro_battle.mp3')
