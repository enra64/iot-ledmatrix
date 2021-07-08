import logging
import serial, time
import serial.tools.list_ports


class MatrixReadException(Exception):
    """Exception raised when reading from the arduino failed"""
    pass


class MatrixProtocolException(Exception):
    """Exception raised when the arduino did not follow the communication protocol as expected"""
    pass


def get_connected_arduinos():
    ports = list(serial.tools.list_ports.comports())
    return ports


def guess_arduino():
    ports = get_connected_arduinos()
    probably_an_arduino = None
    for port in ports:
        # this is the raspberry GPIO UART, where we are not connected
        if port.device == "/dev/ttyAMA0":
            pass
        # my arduino UNO
        elif "/dev/ttyACM" in port.device:
            probably_an_arduino = port.device
        # my arduino nano
        elif "/dev/ttyUSB" in port.device:
            probably_an_arduino = port.device
    return probably_an_arduino


class MatrixSerial:
    """This class handles the communication with the arduino"""

    def __init__(self, interface: str, led_count: int, baud: int = 115200, connect: bool = False,
                 enable_arduino_connection=False):
        """
        Create new MatrixSerial, immediately connecting to the arduino.

        :param interface the device name
        :param led_count: number of leds to use
        :param baud: baud rate to be used
        :param fps the maximum fps to use for updating
        """
        # store serial config
        self.interface = interface
        self.baud = baud
        self.serial = None

        # init buffer
        self.buffer = bytearray(led_count * 3)

        self.was_connected = False

        self.enable_arduino_connection = enable_arduino_connection

        self.logger = logging.getLogger("matrixserial")

        # convenience function for immediately connecting
        if connect and enable_arduino_connection:
            self.connect()

    def connect(self, timeout: float = 2):
        """
        connect to the arduino given the current configuration

        :param timeout: the number of seconds after which the connection attempt will be aborted
        :return: true if the handshake was completed successfully, false otherwise
        :raises: ValueError Will be raised when parameter are out of range, e.g. baud rate, data bits.
        :raises: SerialException In case the device can not be found or can not be configured.
        :raises: MatrixProtocolException if the arduino does not shake hands
        :
        """
        if not self.enable_arduino_connection:
            self.logger.info("the matrix serial was started in silent mode. connect() was ignored.")
            return

        self.was_connected = True

        self.logger.info(f"beginning arduino connection attempt to {self.interface} which has {self.get_led_count()} LEDs")

        # begin serial connection
        self.serial = serial.Serial(self.interface, self.baud, timeout=timeout)
        self.serial.flushInput()
        self.serial.flushOutput()

        # wait for arduino reset
        time.sleep(2)

        # begin handshake
        self.serial.write(b'hello')

        # wait for response
        response = self.serial.read(3)

        if response != b'SAM' and response != b'kSA':
            self.logger.warning("Handshake failed: expected b'SAM', got " + str(response))
            raise MatrixProtocolException("Handshake failed: expected b'SAM', got " + str(response))

        self.logger.info("successfully connected to arduino")

    def stop(self):
        if self.serial is not None:
            self.serial.close()

    def get_led_count(self) -> int:
        """ Query the number of leds this serial connection is configured for """
        # btw: // enforces integer division
        return len(self.buffer) // 3

    def get_buffer_length(self) -> int:
        """ Query the length of the buffer required to send data to the arduino """
        return len(self.buffer)

    @staticmethod
    def current_time_ms() -> int:
        """Helper function. Returns a timestamp in ms"""
        return int(round(time.time() * 1000))

    def update(self, data: bytearray):
        """
        Update the data sent to the connected arduino
        :param data: a bytearray containing the new data, of len
        :raises: MatrixProtocolException if the arduino did not acknowledge the updated data
        """
        # ensure correct data length
        if len(data) != len(self.buffer):
            self.logger.error(
                "Bad data length! len(data) should be " + str(len(self.buffer)) + ", is " + str(len(data)))
            raise MatrixProtocolException(
                "Bad data length! len(data) should be " + str(len(self.buffer)) + ", is " + str(len(data)))

        # copy buffer
        self.buffer[:] = data

        # trigger internal draw call
        self.__draw()

    def __draw(self):
        """
        Draw the current buffer content by sending it to the arduino as-is
        :raises: MatrixProtocolException if the arduino did not acknowledge a sent buffer
        """

        if not self.enable_arduino_connection:
            return

        # we need to wait some time before writing the next set of data. testing required for better accuracy
        time.sleep(0.009)

        # write out internal buffer to arduino
        self.serial.write(self.buffer)

        # read arduino acknowledgement char
        try:
            ack = self.serial.read(1)
        except serial.serialutil.SerialException as e:
            self.logger.exception("A serial error occurred when trying to read from the matrix!")
            raise MatrixReadException(str(e))
        else:
            # check acknowledgement char correctness
            if ack != b'k':
                self.logger.exception("No acknowledgement received, expected b'k', got " + str(ack))
                raise MatrixProtocolException("No acknowledgement received, expected b'k', got " + str(ack))
