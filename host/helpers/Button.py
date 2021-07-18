import threading
import RPi.GPIO as GPIO

# noinspection PyUnresolvedReferencess
class Button(threading.Thread):
    """
    Debounced button handler from https://raspberrypi.stackexchange.com/a/76738

    """

    def __init__(self, pin, func=None, edge='both', bouncetime=200):
        super().__init__(daemon=True)

        self._edge = edge
        self._callback = func
        self._pin = pin
        self._bounce_time = float(bouncetime) / 1000

        GPIO.setmode(GPIO.BCM)
        self._last_pin_value = GPIO.input(self._pin)
        self._lock = threading.Lock()

    def register(self):
        self.start()
        GPIO.add_event_detect(self._pin, GPIO.RISING, callback=self)

    def __call__(self, *args):
        if not self._lock.acquire(blocking=False):
            return

        t = threading.Timer(self._bounce_time, self.read, args=args)
        t.start()

    def read(self, *args):
        pin_value = GPIO.input(self._pin)

        if (
                self._callback is not None and
                ((pin_value == 0 and self._last_pin_value == 1) and (self._edge in ['falling', 'both'])) or
                ((pin_value == 1 and self._last_pin_value == 0) and (self._edge in ['rising', 'both']))
        ):
            self._callback(*args)

        self._last_pin_value = pin_value
        self._lock.release()

    def is_high(self) -> bool:
        return self._last_pin_value == GPIO.HIGH
