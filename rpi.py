import time
from paths import PANEL_LED_PIN, EFFECT_1_PIN, EFFECT_2_PIN, EFFECT_3_PIN
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


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


def test_pin(pin_id):
    print(f"Testing GPIO pin {pin_id}.")
    pin = RpiPin(pin_id)
    print(pin)
    pin.turn_on(3)


if __name__ == "__main__":
    test_pin(EFFECT_2_PIN)
