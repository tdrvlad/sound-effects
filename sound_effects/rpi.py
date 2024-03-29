import time
from params import PANEL_LED_PIN, EFFECT_1_PIN, EFFECT_2_PIN, EFFECT_3_PIN, BUTTON_PULL_DOWN, BUTTON_PIN_1, BUTTON_PIN_2, BUTTON_PIN_3, EFFECT_4_PIN
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


class RpiInput:
    def __init__(self, pin_id, pull_down=BUTTON_PULL_DOWN, action=None, press_time=0.5):
        self.pin_id = pin_id
        self.action = action
        self.pull_down = pull_down
        self.press_time = press_time
        if pull_down:
            pull = GPIO.PUD_DOWN
            self.pressed_state = GPIO.HIGH
        else:
            pull = GPIO.PUD_UP
            self.pressed_state = GPIO.LOW

        GPIO.setup(self.pin_id, GPIO.IN, pull_up_down=pull)

    def check_pressed(self):
        start_time = time.time()
        while GPIO.input(self.pin_id) == self.pressed_state:
            time.sleep(0.01)
            if time.time() - start_time > self.press_time:
                if self.action is not None:
                    self.action()

class RpiPin:
    state = None
    on = GPIO.HIGH
    off = GPIO.LOW

    def __init__(self, pin_id, reverse=True):
        self.pin_id = pin_id

        if reverse:
            self.on, self.off = self.off, self.on

        GPIO.setup(self.pin_id, GPIO.OUT, initial=self.off)
        self.turn_off()

    def _turn_on(self):
        if not self.state is self.on:
            GPIO.output(self.pin_id, self.on)
            self.state = self.on

    def _turn_off(self):
        if not self.state is self.off:
            GPIO.output(self.pin_id, self.off)
            self.state = self.off

    def turn_on(self, time_interval=None):
        print(f"Turn on {self.pin_id}.")
        self._turn_on()
        if time_interval is not None:
            time.sleep(time_interval)
            self._turn_off()

    def turn_off(self, time_interval=None):
        print(f"Turn off {self.pin_id}.")
        self._turn_off()
        if time_interval is not None:
            time.sleep(time_interval)
            self._turn_on()


def test_output(pin_id, pause=1):
    print(f"Testing output on GPIO pin {pin_id}.")

    pin = RpiPin(pin_id)
    for _ in range(100):
        pin.turn_on()
        time.sleep(pause)
        pin.turn_off()
        time.sleep(pause)


def test_button(pin_id):
    print(f"Testing input from GPIO pin {pin_id}")

    def print_pressed():
        print("Pressed")

    button = RpiInput(pin_id, action=print_pressed)
    while True:
        button.check_pressed()
        time.sleep(0.1)
        print(".")


if __name__ == "__main__":
    test_output(EFFECT_4_PIN)

    # test_button(BUTTON_PIN_3)
    # pin = RpiPin(PANEL_LED_PIN)
    # pin.turn_on()


    # test_pin(PANEL_LED_PIN)
    # time.sleep(2.5)
    # test_pin(EFFECT_1_PIN)
    # time.sleep(2.5)
    # test_pin(EFFECT_2_PIN)
    # time.sleep(2.5)
    # test_pin(EFFECT_3_PIN)
