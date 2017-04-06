Configuration options
=====================

All configuration options are command-line arguments.

.. code-block:: none

    --test-with-serial               run only tests testing serial connection
    --test                           run all tests but those requiring an arduino + leds be connected
    --set-arduino-port=              set the port the arduino is connected on manually, like /dev/ttyUSB0
    --name=                          set the name the ledmatrix will advertise itself as
    --width=                         set the horizontal number of leds
    --height=                        set the vertical number of leds
    --data-port=                     set the data port the ledmatrix server will use
    --discovery-port=                set the discovery port the led matrix discovery server will use
    --loglevel=                      set python logging loglevel
    --disable-arduino-connection     disable arduino connection. mostly useful for debugging without an arduino
    --errors-to-console              divert errors to console instead of logfile
    --logfile=                       set log file location. best to use absolute paths.