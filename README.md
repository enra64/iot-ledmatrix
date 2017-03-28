# iot-ledmatrix
This repository contains the code gSilas and I produced in order to run our iot ledmatrix. It consists of three parts, as follows.

## arduino
The arduino code is a simple sketch. The number of used leds must be set before uploading the code. 
The arduino will partake in a simple handshake to confirm correct usage and initialization. After that, the arduino writes
all received data into the led buffer. Whenever ```NUMBER_OF_LEDS * 3``` bytes have arrived, the leds will show the new data.

## Raspberry pi (host) code
The raspberry pi code is responsible for pushing the correct colors to the arduino, and also constitutes the bridge between 
the matrix, the internet and an optional android phone.

### host scripts
The host code is capable of loading scripts following a specific format. These can then modify the display of the led matrix using
a canvas abstraction.

## android code
The android app included in ```client-android``` makes working with the matrix really easy. It supports some administration
features, and it is the basis for interactive scripts.

### Administration
Users can reboot the raspberry pi, shut it down or simply restart the host code. A log viewer is also implemented, so failures
can be quickly debugged.

### host script Fragments
Programmers can write [Fragments](https://developer.android.com/guide/components/fragments.html) that display an arbitrary user
interface to implement any required custom functionality. Two-Way communication between the matrix 
(a running instance of the host and the custom script code) is available.
