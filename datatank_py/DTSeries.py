#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This software is under a BSD license.  See LICENSE.txt for details.

import numpy as np

def _times_considered_same(t1, t2):
    """docstring for _times_considered_same"""
    return abs(t1 - t2) <= 0.000001 * (t1 + t2)

class DTSeries(object):
    """Base class for series support.
    
    In general, you shouldn't need to use this class; it's only provided for
    symmetry with DTSource, and to be used by DTSeriesGroup.  However, it
    may also be useful for non-group objects in future.
    
    """
    
    def __init__(self, datafile, series_name, series_type):
        """
        :param datafile: an empty :class:`datatank_py.DTDataFile.DTDataFile` instance
        :param series_name: the name of the series variable
        :param series_type: the type of the series variable
        
        The name will typically be "Var", and the type will be whatever is the
        base type stored, such as "Group" for a group object.
        
        """
        super(DTSeries, self).__init__()
        
        self._name = series_name
        self._time_values = []
        
        self._datafile = datafile
        # appending and reading is too much work at this point
        assert len(datafile.variable_names()) == 0, "an empty data file is required"
        
        # add series type descriptor
        datafile.write_anonymous(series_type, "Seq_" + series_name)
    
    def datafile(self):
        """:returns: the :class:`datatank_py.DTDataFile.DTDataFile` instance used for storage"""
        return self._datafile
        
    def savecount(self):
        """:returns: the number of time values stored"""
        return len(self.time_values())
        
    def basename(self):
        """:returns: name of the form 'name_N' where N is the result of :meth:savecount"""
        return "%s_%d" % (self._name, self.savecount() - 1)
    
    def time_values(self):
        """:returns: vector of time values stored"""
        return self._time_values
        
    def last_time(self):
        """:returns: last time value stored or ``None`` if no values are stored"""
        return self.time_values()[-1] if self.savecount() else None
        
    def shared_save(self, time):
        """
        :param time: time value to store to disk
        
        Saves the current time value and an appropriate variable name to
        disk.
        """
        # DTSource logs error and returns false here; assert since these are really
        # programmer errors in our case.
        assert time >= 0, "time must not be negative"
        if len(self.time_values()):
            assert time > self.last_time(), "time must be strictly increasing"
        
        if self.last_time() >= 0:
             assert _times_considered_same(time, self.last_time()) == False, "time values too close together"
             
        self._time_values.append(time)
        self._datafile.write_anonymous(time, self.basename() + "_time")
        
class DTSeriesGroup(DTSeries):
    """Base series group class."""
    
    def __init__(self, datafile, name, name_to_type):
        """
        :param datafile: an empty :class:`datatank_py.DTDataFile.DTDataFile` instance
        :param name: the name of the group
        :param name_to_type: a dictionary mapping variable names to DataTank types
                        
        This ``name_to_type`` dictionary defines the structure of the group::
        
            { "My Output Array":"Array", "My Scalar Value":"Real Number" }
            
        You can look up the DataTank type names in its PDF help manual, or for
        compound objects supported in :mod:`datatank_py`, you can use something
        like::
        
            from datatank_py.DTMesh2D import DTMesh2D
            from datatank_py.DTPointCollection2D import DTPointCollection2D
            { "My 2D Mesh":DTMesh2D.dt_type[0], "My Points":DTPointCollection2D.dt_type[0] }
                        
        """
        
        super(DTSeriesGroup, self).__init__(datafile, name, "Group")
        
        # save for sanity checking
        self._names = set(name_to_type.keys())
        basename = "SeqInfo_" + name

        # WriteStructure equivalent; unordered in this case
        idx = 1
        for varname in name_to_type:
            datafile.write_anonymous(varname, "%s_%dN" % (basename, idx))
            datafile.write_anonymous(name_to_type[varname],  "%s_%dT" % (basename, idx))
            idx += 1
            
        datafile.write_anonymous(len(name_to_type), basename + "_N")
        datafile.write_anonymous("Group", basename)
        
    def add(self, time, values):
        """Add a dictionary of values.
        
        :param time: the time value represented by these values
        :param values: dictionary mapping variable name to value
                
        When adding to the group, all variables must be present, or an exception 
        will be raised.  The caller is responsible for ensuring that value types 
        must be consistent with the expected data.  Compound types (e.g., 2D Mesh) 
        are supported via wrapper objects that implement the dt_write protocol.
        See DTDataFile documentation for more details.
        
        Example::
        
            group.add(idx / 10., { "Output Mesh":DTMesh2D(mesh, grid=grid), "Output Index":idx })
            
        
        """
        
        assert self._names == set(values.keys()), "inconsistent variable names"
        
        # DTSeries::SharedSave
        self.shared_save(time)
        
        # DTRetGroup::Write
        for name in values:
            self.datafile().write_anonymous(values[name], "%s_%s" % (self.basename(), name))
        
        # expose the variable for DT
        self.datafile().write_anonymous(np.array([], dtype=np.float64), self.basename())

