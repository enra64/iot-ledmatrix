.. _custom_script_label:

Custom scripts
==============

Custom scripts make the iot-ledmatrix code powerful. You can add any gimmick you want by adding a compatible script file
in the `scripts`-subfolder. When your new script is requested in the app, it will be loaded and given access to draw on
the led matrix.

Creating a new script
=====================

Custom scripts must contain a class that is exactly the name of the source file minus the `.py`. A new instance of this
class will be created whenever the script is requested.
The class should inherit from CustomScript, which is documented here:

CustomScript class
------------------

.. automodule:: CustomScript
.. autoclass:: CustomScript.CustomScript
    :members: