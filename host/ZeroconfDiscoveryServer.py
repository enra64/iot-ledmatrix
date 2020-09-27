from zeroconf import ServiceInfo, Zeroconf


class ZeroconfDiscoveryServer:
    service_type = "_iot-ledmatrix._tcp.local."
    zeroconf = Zeroconf()

    def __init__(self, matrix_name: str, data_port: int, matrix_width: int, matrix_height: int):
        self.led_matrix_service_info = ServiceInfo(
            self.service_type,
            matrix_name + "." + self.service_type,
            port=data_port,
            properties={
                'matrix_width': str(matrix_width),
                'matrix_height': str(matrix_height)
            }
        )

    def start_advertising(self):
        self.zeroconf.register_service(self.led_matrix_service_info)

    def stop_advertising(self):
        self.zeroconf.unregister_service(self.led_matrix_service_info)
