WHAT IS THIS?
=============

This is a Python module that allows you to read and write DataTank data files using
Python. [DataTank](http://visualdatatools.com/DataTank/) is a visualization and 
analysis tool for Mac OS X. Although DataTank itself is proprietary (now free of
charge for students and postdocs), it includes open-source C++ libraries for most
of the internal data structures, so you can easily create data files to be loaded
into it.

When would I use it?
--------------------

* You're using DataTank for analysis, and need a quickie module (external program) to transform some data. You could use the excellent C++ libraries, but sometimes Xcode is more trouble than it's worth, especially since Apple turned it into iTunes for code.
* You're already running numerical experiments in Python using numpy/scipy, and want to easily view the results in DataTank.
* Sometimes data isn't wrapped up nicely in a netCDF file, or you want to create a smaller subset of a large dataset to analyze in DataTank.
* You have an HDF-5 file, and need to use PyTables to extract the relevant parts.
* You have some gruesome ASCII data format that a colleague invented while drunk, and you need to parse it with Python because it has better string APIs than certain popular commercial analysis packages.

I use it to incorporate GIS data with 3D hydrodynamic model output for coastal flow
and transport simulations. Being able to reproject images to/from Lat/Lon or Cartesian
coordinates using GDAL is a great asset. See the examples for ideas on how to do
some of this.

When should I not use it?
-------------------------

* Not all objects are fully supported in datatank_py_, unlike the C++ DTSource libraries.
* The C++ libraries are highly optimized, and can be significantly faster than using Python.
* You need to use other libraries (C/C++/FORTRAN/etc), and equivalent functions are not available in Python.

INSTALL
=======

The module can be installed using as usual, using

    python setup.py install
    
in a terminal. If you get a permission error, you likely need to add `sudo` before
that command. If you're developing and want to just point it to the development
copy, you can use

    python setup.py develop
    
to set up the path appropriately.

Some of the test scripts assume that various symlinks exist in datatank_py/examples.
This is mainly so I can test on multiple systems without hardcoding absolute paths.

REQUIREMENTS
============

Operating System
----------------

DTDataFile has been tested with Python 2.5, 2.6, and 2.7 on Mac OS X 10.5-10.9, and
Python 2.5 on Red Hat Enterprise Linux 5 (64 bit).  Some of the examples may
require Python 2.6 at minimum, or inclusion of 

    from __future__ import with_statement

before any other import statements for Python 2.5. It should still work with PowerPC,
but that hasn't been tested in years, and you're on your own.

NumPy
-----

NumPy is a requirement, and I have no interest in working with Numeric or Numarray.
You can download [NumPy](http://numpy.scipy.org/) or make do with Apple's lobotomized
and ancient version as shipped with OS X.  If you do compile your own, I've found it
necessary to get rid of the OS-installed version, particularly since SciPy won't
compile with it installed.  To do this, I use the following Terminal commands on
Mac OS X 10.6. For later versions, you may not need to do this:

    cd /System/Library/Frameworks/Python.framework/Versions/2.6/Extras/lib/python
    sudo tar -czf numpy.apple.tgz numpy
    rm -r numpy

This leaves you a backup of the system-installed NumPy, in case you ever want it.
If there's a better way to handle this, please tell me.

GDAL
----

Some of the examples require [GDAL](http://www.gdal.org/) with Python bindings. 
I find this invaluable for getting geospatial data into DataTank, even though 
the SWIG bindings seem like writing C++ using Python syntax.

PIL
---

Some of the examples require [PIL](http://www.pythonware.com/products/pil/), 
the Python Imaging Library. If you don't have PIL installed, you should.

DOCUMENTATION
=============

DTDataFile is extensively documented in the source, so help(DTDataFile) in an
interpreter should get you started.  There are a bunch of private methods and
functions that won't show up in pydoc, but they are documented so I don't forget
what they're supposed to do.

BUGS
====

Please email me at amaxwell AT mac DOT com with suggestions for improvement,
or use the tracker at GitHub. For bug fixes, feel free to send a pull request,
and I'll try and figure out how to use git enough to merge it in.

LICENSE
=======

DTDataFile.py and associated scripts are released under the BSD license as follows:

This software is Copyright (c) 2010-2014
Adam Maxwell. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

- Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

- Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

- Neither the name of Adam Maxwell nor the names of any contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


