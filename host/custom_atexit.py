import atexit

import logging


class CustomAtExit:
    """This singleton enables us to manually trigger the atexit functions in case we have the slight suspicion that the program
        might be ending soon, like right before calling os.execv..."""

    class __CustomAtExit:
        """Inner class doing all the things the class should actually do"""
        def __init__(self):
            self.atexit_functions = {}
            atexit.register(self.trigger)

        def register(self, function, args = None):
            """register a new function that must be called on trigger()"""
            self.atexit_functions[function] = args

        def trigger(self):
            """call all registered functions"""
            logging.info("custom atexit triggered.")
            for function, args in self.atexit_functions.items():
                try:
                    if args is not None:
                        function(args)
                    else:
                        function()
                except:
                    logging.warning("got exception during exit :(")

    # the singleton instance variable
    instance = None

    def __init__(self):
        """Create singleton instance if necessary"""
        if not CustomAtExit.instance:
            CustomAtExit.instance = CustomAtExit.__CustomAtExit()

    def __getattr__(self, name):
        """redirect all calls to the singleton instance"""
        return getattr(self.instance, name)
