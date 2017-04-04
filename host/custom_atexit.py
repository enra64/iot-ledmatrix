import atexit

import logging

import traceback


class CustomAtExit:
    """
    This singleton enables us to manually trigger the atexit functions in case we have the slight suspicion that the program
    might be ending soon, like right before calling os.execv...
    """

    class __CustomAtExit:
        """Inner class doing all the things the class should actually do"""

        def __init__(self):
            """init functions to be called, register ourselves for the official atexit"""
            self.atexit_functions = {}
            atexit.register(self.trigger)

        def register(self, function, args=None):
            """register a new function that will be called on exit"""
            self.atexit_functions[function] = args

        def disarm_system_atexit(self):
            """
            Can be used to remove the trigger this class has set for triggering on atexit. Useful to avoid double-
            triggering on manual triggering.
            
            :return: nothing 
            """
            atexit.unregister(self.trigger)

        def trigger(self):
            """call all registered functions"""
            logging.info("custom atexit triggered.")
            for function, args in self.atexit_functions.items():
                try:
                    if args is not None:
                        function(args)
                    else:
                        function()
                except (Exception, AssertionError) as e:
                    if not isinstance(e, KeyboardInterrupt):
                        logging.error(
                            "exception during exit trigger():\n " +
                            traceback.format_exc() +
                            "\n now trying to execute next function :/")

    # the singleton instance variable
    instance = None

    def __init__(self):
        """Create singleton instance if necessary"""
        if not CustomAtExit.instance:
            CustomAtExit.instance = CustomAtExit.__CustomAtExit()

    def __getattr__(self, name):
        """redirect all calls to the singleton instance"""
        return getattr(self.instance, name)
