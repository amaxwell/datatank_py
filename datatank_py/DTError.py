#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This software is under a BSD license.  See LICENSE.txt for details.

__all__ = ["DTErrorMessage", "DTSaveError"]

import sys
import os

_errors = []

def DTErrorMessage(fcn, msg):
    """Accumulate a message and echo to standard error.
    
    :param fcn: typically a function or module name
    :param msg: an error or warning message
    
    Typically you call this each time an error or warning
    should be presented, then call :func:`DTSaveError` before exiting.
    This is aimed exclusively at DataTank module/external program
    usage.
    
    """
    
    if fcn == None:
        fcn = os.path.basename(sys.argv[0])
    
    err_msg = "%s: %s" % (fcn, msg)
    _errors.append(err_msg)
    sys.stderr.write(err_msg + "\n")

def DTSaveError(datafile, name="ExecutionErrors"):
    """Save accumulated messages to a file.
    
    :param datafile: a DTDataFile instance, open for writing
    :param name: defaults to "ExecutionErrors" for DataTank
    
    This will cause all messages accumulated with :func:`DTErrorMessage`
    to be displayed in DataTank's Messages panel.
    This is aimed exclusively at DataTank module/external program
    usage.
    
    """
    
    if len(_errors):
        datafile.write_anonymous(_errors, name)
