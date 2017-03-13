import iot_ledmatrix_component_tests
from matserial import MatrixSerial

def test_all():
    #ser = MatrixSerial("/dev/ttyUSB0", 156, connect=True)

    #iot_ledmatrix_component_tests.red_display_test(ser)
    #iot_ledmatrix_component_tests.test_canvas_draw_pixel_line(ser)
    #iot_ledmatrix_component_tests.test_canvas_pixel_line()
    #iot_ledmatrix_component_tests.test_pixel_index_conversion()
    #iot_ledmatrix_component_tests.test_canvas_rect()
    iot_ledmatrix_component_tests.test_canvas_line()

if __name__ == "__main__":
    test_all()


