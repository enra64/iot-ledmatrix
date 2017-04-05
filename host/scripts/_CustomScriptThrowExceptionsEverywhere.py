import Canvas
from CustomScript import CustomScript


class TestError(Exception):
    """
    Exception raised by the script exception handling script
    """
    pass


class _CustomScriptThrowExceptionsEverywhere(CustomScript):
    def __init__(self, canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                 set_frame_rate, get_connected_clients):
        super().__init__(canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                         set_frame_rate, get_connected_clients)
        # comment out to avoid exec abort
        # raise TestError()

    def update(self, canvas):
        # comment out to avoid exec abort
        # raise TestError()
        pass

    def on_client_disconnected(self, id):
        raise TestError()

    def draw(self, canvas: Canvas):
        # comment out to avoid exec abort
        # raise TestError()
        pass

    def on_data(self, data_dictionary, source_id):
        raise TestError()

    def on_client_connected(self, id):
        raise TestError()

    def exit(self):
        raise TestError()
