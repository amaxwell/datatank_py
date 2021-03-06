#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This software is under a BSD license.  See LICENSE.txt for details.

import os
import numpy as np
from datatank_py.DTDataFile import DTDataFile
from datatank_py.DTBitmap2D import DTBitmap2D
from time import time
from syslog import syslog, LOG_WARNING

if __name__ == '__main__':
    
    #
    # This program replaces a standard DataTank External Program module
    # in C++.  Note that it must be executable (chmod 755 in Terminal)
    # and gdal and numpy are required.
    #
    # It takes as input a file path, then loads an image from it, using
    # GDAL to determine the raster origin and pixel size.  The image is
    # then saved as a 2D Mesh object.  Integer 8 and 16-byte images are
    # converted to 32-bit floats. 
    #
    
    # DT creates this hard link in the working directory, if passed a file
    # this is preferred, as it's fewer variables in DataTank, but if you
    # have a world file, GDAL needs to be able to find it in the original
    # directory.
    image_path = "Image File"
        
    # if no path set, then use the file itself (preferable)
    if os.path.exists(image_path) == False:
        try:
            input_file = DTDataFile("Input.dtbin", readonly=True)
            image_path = input_file["Image Path"]
            input_file.close()
        except Exception, e:
            syslog(LOG_WARNING, "No Input.dtbin file exists")
            
    start_time = time()
    errors = []
    
    if image_path:
        image_path = os.path.expanduser(image_path)
    if image_path is None or os.path.exists(image_path) is False:
        errors.append("\"%s\" does not exist" % (image_path))
    
    try:
        img = DTBitmap2D(image_path)
    except Exception, e:
        errors.append("Failed to open image at %s with exception %s" % (image_path, e))
        img = None
        syslog(LOG_WARNING, "failed to open image at %s with exception %s" % (image_path, e))

    if img is None:
        # set an error and bail out; DataTank doesn't appear to use this, but displays
        # stderr output instead, so print them also
        errors.append("Unable to open as an image file")
        with DTDataFile("Output.dtbin", truncate=True) as output_file:
            output_file.write_anonymous(errors, "ExecutionErrors")
            output_file.write_anonymous(time() - start_time, "ExecutionTime")
            exit(1)
                        
    with DTDataFile("Output.dtbin", truncate=True) as output_file:
        
        output_file.write_anonymous(time() - start_time, "ExecutionTime")
        output_file["Var"] = img.mesh_from_channel()
                        
        # need to save a StringList of execution errors as Seq_ExecutionErrors
        if len(errors):
            output_file.write_anonymous(errors, "ExecutionErrors")
