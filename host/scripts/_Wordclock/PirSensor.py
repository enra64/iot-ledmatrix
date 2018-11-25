import RPi.GPIO as GPIO


class PirSensor:
    def __init__(self):
        self.__sensor_pin = 23
        self.__pir_output_high = True
        self.__initizalize_gpio()

    def __initizalize_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.__sensor_pin, GPIO.IN)
        GPIO.add_event_detect(self.__sensor_pin, GPIO.RISING, callback=self.__pir_on)
        GPIO.add_event_detect(self.__sensor_pin, GPIO.FALLING, callback=self.__pir_off)

    def __pir_on(self) -> None:
        self.__pir_output_high = True

    def __pir_off(self) -> None:
        self.__pir_output_high = False

    def is_something_visible(self) -> bool:
        return self.__pir_output_high
