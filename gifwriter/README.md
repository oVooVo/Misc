Writes gif images to a QByteArray

The code bases on https://github.com/charlietangora/gif-h

There are no functional improvements over the base implementation.
I.e., the outputs shall be bitwise the same. Note that the base implementation does not initialize all buffers, hence it's not always reproductible.
However, some things are different:

 - Implementation in cpp-file. Allows to `#include` the header multiple times.
 - Works with `QImage`. If you already use Qt, this will simplify your life.
 - Writes to `QBuffer`. That is, the code is less platform-dependent (e.g., it's difficult to get a file handle on Android.).
 - Minor refactoring: improve variable names, more consistent object oriented design, typdefs for common structures, don't reinvent STL
 - initialize buffers. That makes the output reproductible.

