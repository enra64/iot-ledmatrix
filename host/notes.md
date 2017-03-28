# dependencies
* sudo pip install pyserial freetype-py pyzmq numpy

# improvements
* remove hard-coded wait in draw code, or parametrise it so timer code can be used above eliminating the problem (which 
is, by the way, that the arduino gets confused if you send data too quickly)
* make available a flag to reboot
* better callbacks for the scripts

# todo
* somehow better handle exceptions in client script code. maybe notify app?
* check whether script data was actually sent for the current script, or another script

# thanks
* [dbader](https://dbader.org/blog/monochrome-font-rendering-with-freetype-and-python)
