# dependencies
* sudo pip install pyserial freetype-py

# improvements
* remove hard-coded wait in draw code, or parametrise it so timer code can be used above eliminating the problem (which 
is, by the way, that the arduino gets confused if you send data too quickly)

# todo
* server broadcasting, forwarding etc

# working
* matserial

# untested
* matgraphics

# thanks
* [dbader](https://dbader.org/blog/monochrome-font-rendering-with-freetype-and-python)

# to self
* default arguments will be created on import o.O, so dont default-argument a MatrixSerial...