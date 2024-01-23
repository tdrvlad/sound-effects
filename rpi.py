import time
from paths import PANEL_LED_PIN, EFFECT_1_PIN, EFFECT_2_PIN, EFFECT_3_PIN, EFFECT_4_PIN, BUTTON_PULL_DOWN, BUTTON_PIN_1, BUTTON_PIN_2, BUTTON_PI_3
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


class RpiInput:
    def __init__(self, pin_id, pull_down=BUTTON_PULL_DOWN, action=None, press_time=0.7):
        self.pin_id = pin_id
        self.action = action
        self.pull_down = pull_down
        self.press_time = press_time
        if pull_down:
            pull = GPIO.PUD_DOWN
            self.pressed_state = GPIO.LOW
        else:
            pull = GPIO.PUD_UP
            self.pressed_state = GPIO.HIGH

        GPIO.setup(self.pin_id, GPIO.IN, pull_up_down=pull)

    def check_pressed(self):
        start_time = time.time()
        while GPIO.input(self.pin_id) == self.pressed_state:
            time.sleep(0.01)
            if time.time() - start_time > self.press_time:
                if self.action is not None:
                    self.action()

class RpiPin:
    def __init__(self, pin_id, reverse=True):
        self.pin_id = pin_id

        # Turning on Relays means their input should be low
        self.on = GPIO.HIGH
        self.off = GPIO.LOW

        if reverse:
            self.on = GPIO.LOW
            self.off = GPIO.HIGH

        GPIO.setup(self.pin_id, GPIO.OUT, initial=self.off)
        self.turn_off()

    def turn_on(self, time_interval=None):
        print(f"Turn on {self.pin_id}.")
        GPIO.output(self.pin_id, self.on)
        if time_interval is not None:
            time.sleep(time_interval)
            GPIO.output(self.pin_id, self.off)

    def turn_off(self, time_interval=None):
        print(f"Turn off {self.pin_id}.")
        GPIO.output(self.pin_id, self.off)
        if time_interval is not None:
            time.sleep(time_interval)
            GPIO.output(self.pin_id, self.on)


def test_output(pin_id):
    print(f"Testing output on GPIO pin {pin_id}.")

    pin = RpiPin(pin_id)
    for _ in range(100):
        pin.turn_on()
        time.sleep(1)
        pin.turn_off()
        time.sleep(1)


def test_button(pin_id):
    print(f"Testing input from GPIO pin {pin_id}")

    def print_pressed():
        print("Pressed")

    button = RpiInput(pin_id, action=print_pressed)
    while True:
        button.check_pressed()
        time.sleep(0.1)


if __name__ == "__main__":
    test_output(EFFECT_4_PIN)

    # test_button(BUTTON_PIN_1)
    # pin = RpiPin(PANEL_LED_PIN)
    # pin.turn_on()


    # test_pin(PANEL_LED_PIN)
    # time.sleep(2.5)
    # test_pin(EFFECT_1_PIN)
    # time.sleep(2.5)
    # test_pin(EFFECT_2_PIN)
    # time.sleep(2.5)
    # test_pin(EFFECT_3_PIN)
