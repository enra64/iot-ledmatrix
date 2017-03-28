from matgraphics import Canvas


class CustomScript:
    """
    The CustomScript class is the class you want to inherit from to implement a new matrix mode.

    In addition to the constructor, there are four methods that will be called by the manager:
        * update, where the state may be updated
        * draw, where the matrix content may be drawn
        * on_data, called when messages from clients arrive
        * exit, last call before the instance is discarded

    The constructor will always be called first. Do your initialization here.
    Update will always be called before draw. The two functions are called in a loop, and will repeatedly execute.
    exit is always the last method call.
    See the method documentation for further information.
    """

    def __init__(self, canvas, send_object, send_object_to_all, start_script):
        """
        The constructor is the first time the script comes alive. After running through it, calls to update and then draw
        are to be expected. All parameters but canvas are stored in the instance by the CustomScript constructor.

        :param canvas: the canvas object is for information (like width and height) purposes. Not guaranteed to be the
            same instance that will be given to update or draw.

        :param send_object: send an object to a single client
        :param send_object_to_all: send an object to all clients
        :param start_script: start another script, stopping this one.
        """
        self.send_object = send_object
        self.send_object_to_all = send_object_to_all
        self.start_script = start_script

    def update(self, canvas):
        """
        Called before draw. Do any updating you want to do here.
        :param canvas: canvas object for information like width and height
        """
        pass

    def draw(self, canvas: Canvas):
        """
        Called after update. Make any modifications of the canvas you want to do here. After this method has finished
        executing, the canvas buffer will be sent to the arduino and displayed.
        :param canvas: the canvas you can draw on. will be displayed on the arduino
        :return: nothing
        """
        pass

    def on_data(self, data_dictionary, source_id):
        """
        Called whenever the android app sends data for the script.
        :param data_dictionary: a dictionary of data received from the android app.
        :param source_id: the network id of the sending android device
        :return: nothing
        """
        pass

    def exit(self):
        """Called when the manager gracefully wants to stop this script. This instance will be discarded of after."""
        pass
