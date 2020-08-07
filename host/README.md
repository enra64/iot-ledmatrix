# Wordclock Server
This component of the iot-ledmatrix framework runs on the
device you want to control, communicating with the LEDs via an
Arduino

## Local Testing
An example to run the code in local testing mode with a GUI:
```shell script
python3 main.py --errors-to-console --name=test-server --width=10 --height=10 --disable-arduino-connection --start-script=_Wordclock --enable-gui
```