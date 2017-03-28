.. iot-ledmatrix documentation master file, created by
   sphinx-quickstart on Tue Mar 28 19:35:56 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to iot-ledmatrix's documentation!
=========================================

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    custom_scripts

iot-ledmatrix is a code base produced to use a diy rgb led matrix made from WS2812B leds.
The code was written by `enra64 <github.com/enra64>`_ and `gSilas <https://www.github.com/gSilas>`_.

The code consists of three parts:

* the arduino code required to talk to the leds
* the python code used on the raspberry pi inside the matrix
* the android code making up the control app

arduino sketch
==============
The arduino code is simple, but ``NUM_LEDS_CURRENT`` must be set before uploading the code.
The arduino will partake in a simple handshake to confirm correct usage and initialization.
After that, the arduino writes all received data into the led buffer.
Whenever enough bytes for a single frame have arrived, the leds will show the new data.

Raspberry pi (host) code
========================
The raspberry pi code is responsible for pushing the correct colors to the arduino,
and also constitutes the bridge between the matrix, the internet and an optional android phone.

custom scripts
--------------
Custom scripts enable you to easily create new features for the matrix. They are discussed in detail here: :ref:`custom_script_label`

android code
============
The android app included in client-android makes working with the matrix really easy. It supports some administration features, and it is the basis for interactive scripts.

administration
--------------
Users can reboot the raspberry pi, shut it down or simply restart the host code. A log viewer is also implemented, so failures can be quickly debugged.

host script fragments
---------------------
Programmers can write Fragments that display an arbitrary user interface to implement any required custom functionality. Two-Way communication between the matrix (a running instance of the host and the custom script code) is available.