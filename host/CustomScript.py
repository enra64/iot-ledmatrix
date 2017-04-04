from Canvas import Canvas


# noinspection PyMethodMayBeStatic
class CustomScript:
    """
    The CustomScript class is the class you want to inherit from to implement a new matrix mode.

    In addition to the constructor, there are six methods that will be called by the manager:
        * update(canvas), where the state may be updated
        * draw(canvas), where the matrix content may be drawn
        * on_data(obj, source_id), called when messages from clients arrive
        * exit(), last call before the instance is discarded
        * on_client_connected(client_id), called with an id parameter when a new client is approved
        * on_client_disconnected(client_id), called with an id parameter when a client has disconnected
    
    They have default implementations, so you only need to override them if you need to do anything.
        
    A few methods can also be called by the script itself (self.<function_name>(<param1...>)):
        * send_object(obj, id) to send objects to specific clients
        * send_object_to_all(obj) to send objects to all clients
        * start_script(script) start a script by name. will replace current script.
        * restart_self() restarts the current script
        * get_connected_clients() gets a list of approved client ids
        * set_frame_period(period) allows to set a custom update cycle period in seconds
        * set_frame_rate(rate) allows to set a custom update cycle calling rate in Hz
        
    All of these functions are documented more detailed in their method documentations.

    The constructor will always be called first. Do your initialization here.
    Update will always be called before draw. The two functions are called in a loop, and will repeatedly execute.
    exit is always the last method call.
    See the method documentation for further information.
    """

    def __init__(self,
                 canvas,
                 send_object,
                 send_object_to_all,
                 start_script,
                 restart_self,
                 set_frame_period,
                 set_frame_rate,
                 get_connected_clients):
        """
        The constructor is the first time the script comes alive. After running through it, calls to update and then draw
        are to be expected. All parameters but canvas are stored in the instance by the CustomScript constructor.

        :param canvas: the canvas object is for information (like width and height) purposes. Not guaranteed to be the
            same instance that will be given to update or draw.
        :param send_object: send an object to a single client.
        :param send_object_to_all: send an object to all clients
        :param start_script: start another script, stopping this one.
        :param restart_self: helper call for start_script(this_one)
        :param set_frame_period: set the period with which the script update cycle is called. overwrites set_framerate.
        :param set_frame_rate: set the frame rate with which the script update cycle is called. overwrites set_frame_period.
        """
        self.__send_object = send_object
        self.__send_object_to_all = send_object_to_all
        self.__start_script = start_script
        self.__restart_self = restart_self
        self.__set_frame_period = set_frame_period
        self.__set_frame_rate = set_frame_rate
        self.__get_connected_clients = get_connected_clients

    def get_connected_clients(self):
        return self.__get_connected_clients()

    def send_object(self, obj, target):
        """
        Send an object to the target id. The object can be anything. No JSON serialization needs to be
        performed by you.

        :param obj: the object to be sent
        :param target_id: target id of the client
        :return: nothing
        """
        self.__send_object(obj, target)

    def send_object_to_all(self, obj):
        """
        Send an object to all connected clients. The object can be anything. No JSON serialization needs to be
        performed by you.
    
        :param obj: the object to be sent
        :return: nothing
        """
        self.__send_object_to_all(obj)

    def start_script(self, script_name, source_id):
        """
        Will load the class in the scripts/ folder that has the given name in the file with the same name.

        :param script_name: the name of _both_ the script and the class implementing the callback functions
        :param source_id: the id of the client requesting the script to be loaded
        """
        self.__start_script(script_name, source_id)

    def restart_self(self):
        """
        Will restart the current script. exit() will be called on this instance. A new instance will be
        created. No additional arguments can be given.
        
        :return: nothing 
        """
        self.__restart_self()

    def set_frame_period(self, period):
        """
        Change the frame period with which the script will be updated

        :param period: the target frame period. resulting frame rate must be 0 <= f <= 60, in Hz 
        :return: nothing
        """
        self.__set_frame_period(period)

    def set_frame_rate(self, frame_rate):
        """
        Change the frame rate with which the script will be updated

        :param frame_rate: the target frame rate. must be 0 <= f <= 60, in Hz 
        :return: nothing
        """
        self.__set_frame_rate(frame_rate)

    def on_client_connected(self, id):
        """
        Called when a client connects
    
        :param id: id of the client that disconnected 
        :return: 
        """
        pass

    def on_client_disconnected(self, id):
        """
        Called when a client disconnects
        
        :param id: id of the client that disconnected 
        :return: 
        """
        pass

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
