.. _custom_script_label:

Custom scripts
==============

Custom scripts are what makes iot-ledmatrix powerful.
You can add any gimmick you want by adding an implementation to one of the subfolders of `scripts`.

Scripts placed in `scripts/does_not_require_custom_fragment` can be loaded manually in the accompanying app, while those
placed in `scripts/requires_custom_fragment` will only be loaded by custom fragments in the app. Other than that,
new custom scripts do not need any configuration effort. These directories may change depending on your execution parameters.
When your new script is requested in the app, it will be loaded and can draw to the led matrix.

How to draw from within the script
----------------------------------
Drawing to the matrix is done by using the functions of the canvas supplied with the draw calls. Detailed
documentation is available here: :ref:`canvas_class_label`

Creating a new script
---------------------

Custom scripts must contain a class that is exactly the name of the source file minus the `.py`.

For example, if you create a "flashlight" script, the file name would be ``flashlight.py``, and the class name would be ``flashlight``.

The class must inherit from CustomScript, which is documented here:

CustomScript class
------------------

.. automodule:: CustomScript
.. autoclass:: CustomScript.CustomScript
    :members: