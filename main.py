from matserial import MatrixProtocolException, MatrixSerial

def red_display_test(serial: MatrixSerial):
    # "red" color specification
    r = [255, 0, 0]

    # construct test data showing red on all leds
    red_test_data = bytearray()
    for i in range(0, serial.get_led_count()):
        red_test_data.extend(r)

    print(str(red_test_data))

    while(True):
        serial.update(red_test_data)


if __name__ == "__main__":
    ser = MatrixSerial("/dev/ttyUSB0", 156, connect=True)

    red_display_test(ser)