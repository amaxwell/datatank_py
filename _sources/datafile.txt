.. _dtdatafile:

**********
Data Files
**********

DTDataFile
==========

This is the primary interface for communication between DataTank
and a Python-based helper program, assuming you use files for
communication. It allows you to read, write, and append to a
DataTank binary file (extension `.dtbin`).

.. autoclass:: datatank_py.DTDataFile.DTDataFile
   :members:
   :special-members: __init__

DTPyWrite
=========

.. automodule:: datatank_py.DTPyWrite
   :members:
   :special-members: __dt_write__, __dt_type__
   
DTError
=======

.. automodule:: datatank_py.DTError
   :members:

DTProgress
==========

.. autoclass:: datatank_py.DTProgress.DTProgress
   :members:
