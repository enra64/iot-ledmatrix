import logging

from zeroconf import ServiceInfo, Zeroconf, IPVersion, NonUniqueNameException


class ZeroconfDiscoveryServer:
    service_type = "_iot-ledmatrix._tcp.local."
    zeroconf = Zeroconf(
        ip_version=IPVersion.V4Only
    )

    def __init__(self, matrix_name: str, data_port: int, matrix_width: int, matrix_height: int):
        self.logger = logging.getLogger("ZeroconfDiscoveryServer")
        self.led_matrix_service_info = ServiceInfo(
            type_=self.service_type,
            name=self._generate_name(matrix_name, matrix_width, matrix_height),
            port=data_port
        )
        self.logger.info("ZeroConf Advertiser initialized")

    def _generate_name(self, name, width, height):
        return "{}:{}:{}.{}".format(
            name,
            width,
            height,
            self.service_type
        )

    def start_advertising(self):
        try:
            self.zeroconf.register_service(self.led_matrix_service_info)
            self.logger.info("ZeroConf Advertiser start")
        except NonUniqueNameException as e:
            self.logger.error(e)

    def stop_advertising(self):
        self.zeroconf.unregister_service(self.led_matrix_service_info)
        self.logger.info("ZeroConf Advertiser stop")
