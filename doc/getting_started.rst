.. _getting_started:


***************
Getting started
***************

.. _installing-docdir:

Installing your doc directory
=============================

You may already have `datatank_py <https://github.com/amaxwell/datatank_py>`_
installed -- you can check by doing::

  python -c 'import datatank_py'

If that fails grab the latest version from GitHub with::

  > git clone https://github.com/amaxwell/datatank_py.git
  > cd datatank_py
  > sudo python setup.py install
  
.. _simple_example:

A simple example
================

.. image:: _static/mesh_example_ss.png

.. sourcecode:: python

    #!/usr/bin/env python
    # coding: utf-8

    # These are basically like C includes; you can also use
    # `from datatank_py import *` to get everything, but then
    # you refer to classes as DTDataFile.DTDataFile("/tmp/blah")
    # and so forth.
    from datatank_py.DTDataFile import DTDataFile
    from datatank_py.DTMesh2D import DTMesh2D

    from time import time
    import sys

    def computation(mesh, scalar):
    
        # mesh is DTMesh2D
        # scalar is float
        # return a DTMesh2D object
    
        # here we get the values, which is a 2D mesh
        values = mesh.values()
    
        # just multiply all values by the constant
        values *= scalar
    
        # return a new mesh object, reusing the same grid with our new values
        return DTMesh2D(values, grid=mesh.grid())

    if __name__ == '__main__':
    
        with DTDataFile("Input.dtbin") as input_file:
        
            # This is the highest level way to get an object, but isn't a complete
            # feature for all classes yet. Alternate way to get it would be
            # mesh = DTMesh2D.from_data_file(input_file, "input")
            mesh = input_file.dt_object_named("input")
        
            # This use Python's dictionary getter syntax to get a primitive object
            # that isn't wrapped in a DT class. This is the most convenient way to
            # get an array, number, string, or list of strings.
            scalar = input_file["scalar"]
        
            start_time = time()
            errors = []
        
            # This is just an example; another possibility is wrapping the entire
            # main call in an exception handler.
            try:
                output_mesh = computation(mesh, scalar)
            except Exception, e:
                errors.append("Exception raised: %s" % (e))
            
            # create or truncate the output file    
            with DTDataFile("Output.dtbin", truncate=True) as output_file:
                # record computation time
                output_file["ExecutionTime"] = (time() - start_time)
        
                # DataTank seems to display stderr instead of the error list, so
                # make sure to write to both.
                if len(errors):
                    output_file["ExecutionErrors"] = errors
                    sys.stderr.write("%s\n" % errors)
            
                else:
                    # save the output variable; this will be visible to DataTank
                    #sys.stderr.write("%s: %s\n" % (type(output_string), output_string))
                    output_file["Var"] = output_mesh            
