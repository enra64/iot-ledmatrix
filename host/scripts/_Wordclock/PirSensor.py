import RPi.GPIO as GPIO


class PirSensor:
    def __init__(self):
        self.__sensor_pin = 14
        self.__pin_high = True
        self.__initizalize_gpio()

    def __initizalize_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.__sensor_pin, GPIO.IN)
        GPIO.add_event_detect(self.__sensor_pin, GPIO.BOTH, callback=self.__pir_event)

    def __pir_event(self, channel):
        sensor_value = GPIO.input(self.__sensor_pin)
        print("event! input=" + str(sensor_value))
        self.__pin_high = sensor_value == GPIO.HIGH

    def is_something_visible(self) -> bool:
        return self.__pin_high
