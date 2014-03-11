#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This software is under a BSD license.  See LICENSE.txt for details.

def dt_writer(obj):
    """Check to ensure conformance to dt_writer protocol.
    
    :returns: ``True`` if the object implements the required methods
    
    """
    return hasattr(obj, "__dt_type__") and hasattr(obj, "__dt_write__")

class DTPyWrite(object):
    """Class documenting methods that must be implemented for DTDataFile to load
    complex types by name.
    
    This is never instantiated directly. :class:`datatank_py.DTDataFile.DTDataFile` 
    checks to ensure that an object implements all of the required methods, but you 
    are not required to use :class:`DTPyWrite` as a base class.  It's mainly 
    provided as a convenience and formal documentation.
    
    """
    
    def __dt_type__(self):
        """The variable type as required by DataTank.
        
        :returns: variable type as a string
        
        This is a string description of the variable, which can be found in the
        DataTank manual PDF or in DTSource.  It's easiest to look in DTSource, 
        since you'll need to look there for the :meth:`__dt_write__` implementation anyway.
        You can find the type in the ``WriteOne()`` function for a particular class,
        such as:
        
        .. code-block:: cpp
        
            // this is taken from DTPath2D.cpp
            void WriteOne(DTDataStorage &output,const string &name,const DTPath2D &toWrite)
            {
                Write(output,name,toWrite);
                Write(output,"Seq_"+name,"2D Path");
                output.Flush();
            }
        
        where the type is the string "2D Path".  In some cases, it seems that
        multiple type names are recognized; e.g., "StringList" is written by
        DataTank, but "List of Strings" is used in DTSource.  Regardless, this
        is trivial; the :meth:`datatank_py.DTPath2D.DTPath2D.__dt_type__` 
        method looks like this::
        
          def __dt_type__(self):
              return "2D Path"
        
        """
        
        raise NotImplementedError("This method is required")
        
    def __dt_write__(self, datafile, name):
        """Write all associated values to a file.
    
        :param datafile: a :class:`datatank_py.DTDataFile.DTDataFile` instance
        :param name: the name of the variable as it should appear in DataTank
        
        This method collects the necessary components of the compound object and
        writes them to the datafile.  The name is generally used as a base for
        associated variable names, since only one of the components can have the 
        "primary" name.  Again, the DataTank manual PDF or DTSource must be used
        here as a reference (DTSource is more complete).  In particular, you need
        to look at the ``Write()`` function implemented in the C++ class:
        
        .. code-block:: cpp
        
            // this is taken from DTPath2D.cpp
            void Write(DTDataStorage &output,const string &name,const DTPath2D &thePath)
            {
                Write(output,name+"_bbox2D",BoundingBox(thePath));
                Write(output,name,thePath.Data());
            }
        
        Here the bounding box is written as `name_bbox2D`; this is just a 4 element
        double-precision array.  Next, the actual path array is saved under the name
        as passed in to the function.  The equivalent Python implementation is::
        
          def __dt_write__(self, datafile, name):
              datafile.write_anonymous(self.bounding_box(), name + "_bbox2D")
              datafile.write_anonymous(np.dstack((self._xvalues, self._yvalues)), name)
        
        Note that :meth:`datatank_py.DTDataFile.DTDataFile.write_anonymous` should be 
        used in order to avoid any variable name munging 
        (prepending "Seq\_" in order to make the variable visible in DataTank).
        
        """
        
        raise NotImplementedError("This method is required")        

    @classmethod
    def from_data_file(self, datafile, name):
        """Instantiate a :mod:`datatank_py` high-level object from a file.
        
        :param datafile: a :class:`datatank_py.DTDataFile.DTDataFile` instance
        :param name: the name of the variable
        
        :returns: a properly initialized instance of the calling class
        
        This class method can be implemented to read necessary components of an object
        from a datafile.  For example::
         
          from datatank_py.DTPath2D import DTPath2D
          from datatank_py.DTDataFile import DTDataFile
        
          with DTDataFile("Input.dtbin") as df:
              path = DTPath2D.from_data_file(df, "My Path")
            
        will try to create a :class:`datatank_py.DTPath2D.DTPath2D` from
        variables named "My Path" in the given data file.  
        In general, this is the inverse of the :meth:`__dt_write__` method,
        but may be slightly more tricky due to naming conventions in DataTank and
        optional data that DataTank may or may not include.
        
        """
        
        raise NotImplementedError("Optional read method is not implemented")
        
