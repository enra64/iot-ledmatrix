import atexit

import logging

import traceback

import sys


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
            self.logger = logging.getLogger("customatexit")
            self.__is_shutdown_initiated = False
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
            self.logger.info("custom atexit triggered.")
            self.__is_shutdown_initiated = True
            for atexit_function, args in self.atexit_functions.items():
                try:
                    if args is not None:
                        atexit_function(args)
                    else:
                        atexit_function()
                except (Exception, AssertionError) as e:
                    if not isinstance(e, KeyboardInterrupt):
                        self.logger.error(
                            "exception during exit trigger():\n" +
                            traceback.format_exc())

        def is_shutdown_initiated(self) -> bool:
            """
            Returns True if the registered functions have been triggered. After that, you *probably* shouldn't start
            anything anymore, even though it is possible.

            :return: True if the registered functions have been triggered
            """
            return self.__is_shutdown_initiated

    # the singleton instance variable
    instance = None

    def __init__(self):
        """Create singleton instance if necessary"""
        if not CustomAtExit.instance:
            CustomAtExit.instance = CustomAtExit.__CustomAtExit()

    def __getattr__(self, name):
        """redirect all calls to the singleton instance"""
        return getattr(self.instance, name)
