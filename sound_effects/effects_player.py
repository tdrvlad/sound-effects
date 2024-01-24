import time
from params import EFFECTS_MAP, PANEL_LED_PIN, BUTTON_PIN_1, BUTTON_PIN_2, BUTTON_PIN_3, BUTTONS_MAP
from utils import load_effect, get_audio_player
from effects_control import create_sounds_callable_dict, control_leds, get_effects_pins
import threading
from rpi import RpiPin, RpiInput
import RPi.GPIO as GPIO


def main(effect_id, buttons_map):
    print("Initializing effects.")
    led_pin = RpiPin(PANEL_LED_PIN, reverse=False)

    effects_pins = get_effects_pins(EFFECTS_MAP)

    audio_player, timestamps = load_effect(effect_id)
    actions = create_sounds_callable_dict(timestamps, effects_pins)

    # Load audio players for each intro and outro
    audio_players = {}
    for button, paths in buttons_map.items():
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
    main(effect_id="battle_v2_20240124124859", buttons_map=BUTTONS_MAP)