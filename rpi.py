import time
from paths import PANEL_LED_PIN, EFFECT_1_PIN, EFFECT_2_PIN, EFFECT_3_PIN, BUTTON_PULL_DOWN
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


class RpiInput:
    def __init__(self, pin_id, pull_down=BUTTON_PULL_DOWN, action=None):
        self.pin_id = pin_id
        if pull_down:
            pull = GPIO.PUD_DOWN
        else:
            pull = GPIO.PUD_UP
        GPIO.setup(self.pin_id, GPIO.IN, pull_up_down=pull)
        GPIO.add_event_detect(self.pin_id, GPIO.FALLING, callback=action, bouncetime=200)


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


def test_pin(pin_id):
    print(f"Testing GPIO pin {pin_id}.")
    pin = RpiPin(pin_id)
    pin.turn_on()
    time.sleep(0.5)
    pin.turn_off()


if __name__ == "__main__":
    # for _ in range(100):
    #     test_pin(EFFECT_1_PIN)
    #     time.sleep(0.1)
    test_pin(PANEL_LED_PIN)
    time.sleep(2.5)
    test_pin(EFFECT_1_PIN)
    time.sleep(2.5)
    test_pin(EFFECT_2_PIN)
    time.sleep(2.5)
    test_pin(EFFECT_3_PIN)
