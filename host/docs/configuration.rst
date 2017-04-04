Configuration options
=====================

All configuration options are command-line arguments.

.. code-block:: none

    --set-arduino-port=              set the port the arduino is connected on manually.
    --name=                          set the name the ledmatrix will advertise itself as
    --width=                         horizontal number of leds
    --height=                        vertical number of leds
    --data-port=                     set the data port this ledmatrix will use
    --discovery-port=                set the discovery port this ledmatrix will use
    --loglevel=                      set python logging loglevel
    --disable-arduino-connection     disable arduino connection. mostly useful for debugging without an arduino
    --no_custom_fragment_directory=  set custom directory for where to look for custom scripts requiring no custom fragment.
                                     be aware that changing this might cause some default fragments to not be found
    --custom_fragment_directory=     set custom directory for where to look for custom scripts requiring a custom fragment.
                                     be aware that changing this might cause some default fragments to not be found.