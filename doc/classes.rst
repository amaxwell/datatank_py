.. _0d_classes:

*****************
0D and 1D Classes
*****************

DTPlot1D
==============
.. autoclass:: datatank_py.DTPlot1D.DTPlot1D
   :members:
   :special-members: __init__   

DTMask
======
.. autoclass:: datatank_py.DTMask.DTMask
   :members:
   :special-members: __init__
   
DTDictionary
============
.. autoclass:: datatank_py.DTDictionary.DTDictionary
   :members:
   :special-members: __init__
   
.. sourcecode:: python

    #!/usr/bin/env python
    # -*- coding: utf-8 -*-

    from datatank_py.DTDataFile import DTDataFile
    from datatank_py.DTDictionary import DTDictionary

    if __name__ == '__main__':
    
        dt_dict = DTDictionary()
    
        dt_dict["Test_scalar_float"] = 2.573
        dt_dict["Test_scalar_int"] = 5
        dt_dict["Test_string"] = "This is only a test"
        dt_dict["Test_array"] = (1.1, 2, 5, 7.5, 11.978)
    
        with DTDataFile("/tmp/dict_test.dtbin", truncate=True) as dtf:
            dtf["dictionary test"] = dt_dict
    
        # read the dictionary back from the file
        with DTDataFile("/tmp/dict_test.dtbin") as dtf:
            dt_dict = DTDictionary.from_data_file(dtf, "dictionary test")
            
            # iterate and print each key/value pair
            for k in dt_dict:
                print "%s = %s" % (k, dt_dict[k])
            
            # normal dictionary print
            print dt_dict


   
.. _2d_classes:

**********
2D Classes
**********

DTMesh2D
========

.. autoclass:: datatank_py.DTMesh2D.DTMesh2D
   :members:
   :special-members: __init__
   
DTPoint2D
=========

.. autoclass:: datatank_py.DTPoint2D.DTPoint2D
   :members:
   :special-members: __init__
   
DTPointCollection2D
===================

.. autoclass:: datatank_py.DTPointCollection2D.DTPointCollection2D
   :members:
   :special-members: __init__

DTPointValue2D
==============

.. autoclass:: datatank_py.DTPointValue2D.DTPointValue2D
   :members:
   :special-members: __init__
   
DTPointValueCollection2D
========================

.. autoclass:: datatank_py.DTPointValueCollection2D.DTPointValueCollection2D
   :members:
   :special-members: __init__
      
DTStructuredGrid2D
==================

.. autoclass:: datatank_py.DTStructuredGrid2D.DTStructuredGrid2D
   :members:
   :special-members: __init__
   
DTStructuredMesh2D
==================

.. autoclass:: datatank_py.DTStructuredMesh2D.DTStructuredMesh2D
   :members:
   :special-members: __init__
   
DTStructuredVectorField2D
=========================

.. autoclass:: datatank_py.DTStructuredVectorField2D.DTStructuredVectorField2D
   :members:
   :special-members: __init__

DTTriangularGrid2D
==================

.. autoclass:: datatank_py.DTTriangularGrid2D.DTTriangularGrid2D
   :members:
   :special-members: __init__

DTTriangularMesh2D
==================

.. autoclass:: datatank_py.DTTriangularMesh2D.DTTriangularMesh2D
   :members:
   :special-members: __init__

DTTriangularVectorField2D
=========================

.. autoclass:: datatank_py.DTTriangularVectorField2D.DTTriangularVectorField2D
   :members:
   :special-members: __init__
   
DTPath2D
========
.. autoclass:: datatank_py.DTPath2D.DTPath2D
   :members:
   :special-members: __init__

DTPathValues2D
==============
.. autoclass:: datatank_py.DTPathValues2D.DTPathValues2D
   :members:
   :special-members: __init__
   
DTRegion2D
==========
.. autoclass:: datatank_py.DTRegion2D.DTRegion2D
   :members:
   :special-members: __init__
   
DTVector2D
==========
.. autoclass:: datatank_py.DTVector2D.DTVector2D
   :members:
   :special-members: __init__

.. _3d_classes:

**********
3D Classes
**********
   
DTRegion3D
==========
.. autoclass:: datatank_py.DTRegion3D.DTRegion3D
   :members:
   :special-members: __init__  

DTStructuredGrid3D
==================
.. autoclass:: datatank_py.DTStructuredGrid3D.DTStructuredGrid3D
   :members:
   :special-members: __init__  
 
DTStructuredMesh3D
==================
.. autoclass:: datatank_py.DTStructuredMesh3D.DTStructuredMesh3D
   :members:
   :special-members: __init__  

DTStructuredVectorField3D
=========================

.. autoclass:: datatank_py.DTStructuredVectorField3D.DTStructuredVectorField3D
   :members:
   :special-members: __init__
