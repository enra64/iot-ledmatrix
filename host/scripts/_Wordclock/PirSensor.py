import RPi.GPIO as GPIO


# noinspection PyUnresolvedReferences
class PirSensor:
    """
    A helper class to encapsulate reading out a PIR sensor from a given pin
    """

    def __init__(self, sensor_pin: int):
        """
        Create a new PirSensor instance listening on the given sensor pin

        :param sensor_pin: the pin number for the PIR sensor (BCM numbering)
        :return: nothing
        """
        self.__sensor_pin = sensor_pin
        self.__pin_high = True
        self.__initizalize_gpio()

    def __initizalize_gpio(self) -> None:
        """
        Initialize the GPIO pin used for reading the sensor pin

        :return: nothing
        """
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.__sensor_pin, GPIO.IN)
        GPIO.add_event_detect(self.__sensor_pin, GPIO.BOTH, callback=self.__pir_event)

    # noinspection PyUnusedLocal
    def __pir_event(self, channel) -> None:
        """
        Callback function when a rising or falling edge has been detected on self.__sensor_pin

        :param channel: the channel on which the edge has been detected - ignored, should always bee __sensor_pin
        :return: nothing
        """
        sensor_value = GPIO.input(self.__sensor_pin)
        self.__pin_high = sensor_value == GPIO.HIGH

    def is_something_visible(self) -> bool:
        """
        Returns true if the PIR is currently reporting something to be visible
        
        :return: true iff PIR saw something recently, false otherwise
        """
        return self.__pin_high
