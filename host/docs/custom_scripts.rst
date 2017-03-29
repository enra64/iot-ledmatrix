.. _custom_script_label:

Custom scripts
==============

Custom scripts are what makes iot-ledmatrix powerful. You can add any gimmick you want by adding an implementation
to the `scripts`-subfolder. When your new script is requested in the app, it will be loaded and can draw to the led matrix.


Creating a new script
---------------------

Custom scripts must contain a class that is exactly the name of the source file minus the `.py`.

For example, if you create a "flashlight" script, the file name would be ``flashlight.py``, and the class name would be ``flashlight``.

The class must inherit from CustomScript, which is documented here:

How to draw from within the script
----------------------------------
Drawing to the matrix is done by using the functions of the canvas supplied with the draw calls. Detailed
documentation is available here: :ref:`canvas_class_label`

CustomScript class
------------------

.. automodule:: CustomScript
.. autoclass:: CustomScript.CustomScript
    :members: