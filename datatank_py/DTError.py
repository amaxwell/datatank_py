#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This software is under a BSD license.  See LICENSE.txt for details.

__all__ = ["DTErrorMessage", "DTSaveError", "dt_set_log_identifier", "dt_use_syslog"]

import sys
import os
from syslog import syslog, openlog, LOG_ERR

_errors = []
_DEFAULT_CONTEXT = os.path.basename(sys.argv[0])
_USE_SYSLOG = False

def dt_set_log_identifier(ctxt):
    """Sets the default logging identifier to something useful.
    
    :param ctxt: a string that will usefully identify this log message
    
    Typically you should just pass in the basename of your Python script here.
    Since DataTank changes executable names in modules (and perhaps other times),
    the default of ``sys.argv[0]`` isn't effective in tracking down
    error messages, since they're all attributed to "runme" or something similar.
    
    """
    
    global _DEFAULT_CONTEXT
    _DEFAULT_CONTEXT = ctxt
    openlog(ident=ctxt)
    
def dt_use_syslog(should_use):
    """Allows you to copy all messages to syslog.
    
    :param should_use: pass ``True`` to use syslog
    
    """
    
    global _USE_SYSLOG
    _USE_SYSLOG = should_use

def DTErrorMessage(fcn, msg):
    """Accumulate a message and echo to standard error.
    
    :param fcn: typically a function or module name (pass ``None`` to use argv[0])
    :param msg: an error or warning message
        
    Typically you call this each time an error or warning
    should be presented, then call :func:`DTSaveError` before exiting.
    This is aimed exclusively at DataTank module/external program
    usage.
    
    """
        
    if fcn == None:
        fcn = _DEFAULT_CONTEXT
    
    err_msg = "%s: %s" % (fcn, msg)
    _errors.append(err_msg)
    
    # this is harmless, and lets you get errors when running in console mode
    sys.stderr.write(err_msg + "\n")
    
    # syslog will do its own ident string if we haven't set it explicitly
    if _USE_SYSLOG:
        syslog(LOG_ERR, msg)
    
def DTWarningMessage(fcn, msg):
    """Calls :func:`DTErrorMessage`, which is what C++ DTSource does."""
    DTErrorMessage(fcn, msg)

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
