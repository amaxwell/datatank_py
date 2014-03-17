#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This software is under a BSD license.  See LICENSE.txt for details.

import numpy as np

class DTTriangularVectorField2D(object):
    """2D triangular vector field object."""
    
    dt_type = ("2D Triangular Vector Field",)
    """Type strings allowed by DataTank"""
    
    def __init__(self, grid, u, v):
        """
        :param grid: :class:`datatank_py.DTTriangularGrid2D.DTTriangularGrid2D` instance
        :param u: vector or list of values in nodal order
        :param v: vector or list of values in nodal order
                
        """
        
        super(DTTriangularVectorField2D, self).__init__()
                           
        u = np.squeeze(u)
        v = np.squeeze(v)
        assert grid.number_of_points() == len(u)
        assert grid.number_of_points() == len(v)
        self._grid = grid
        self._u = u
        self._v = v
    
    def __dt_type__(self):
        return "2D Triangular Vector Field"
        
    def grid(self):
        """:returns: a :class:`datatank_py.DTTriangularGrid2D.DTTriangularGrid2D` instance"""
        return self._grid
        
    def bounding_box(self):
        """:returns: a :class:`datatank_py.DTRegion2D.DTRegion2D` instance"""
        return self._grid.bounding_box()
        
    def write_with_shared_grid(self, datafile, name, grid_name, time, time_index):
        """Allows saving a single grid and sharing it amongst different time
        values of a variable.
        
        :param datafile: a :class:`datatank_py.DTDataFile.DTDataFile` open for writing
        :param name: the vector field variable's name
        :param grid_name: the grid name to be shared (will not be visible in DataTank)
        :param time: the time value for this step (DataTank's ``t`` variable)
        :param time_index: the corresponding integer index of this time step
        
        This is an advanced technique, but it can give a significant space savings in
        a data file. It's not widely implemented, since it's not clear yet if this
        is the best API.
        
        """

        if grid_name not in datafile:
            datafile.write_anonymous(self._grid, grid_name)
            datafile.write_anonymous(self.__dt_type__(), "Seq_" + name)
            
        varname = "%s_%d" % (name, time_index)
        datafile.write_anonymous(grid_name, varname)
        datafile.write_anonymous(self._u, varname + "_VX")
        datafile.write_anonymous(self._v, varname + "_VY")
        datafile.write_anonymous(np.array((time,)), varname + "_time")
        
    def __str__(self):
        return self.__dt_type__() + ":\n  grid = " + str(self._grid)
        
    def __dt_write__(self, datafile, name):
        datafile.write_anonymous(self._u, name + "_VX")
        datafile.write_anonymous(self._v, name + "_VY")
        datafile.write_anonymous(self._grid, name)
        
    @classmethod
    def from_data_file(self, datafile, name):
        
        name = datafile.resolve_name(name)
        u = datafile[name + "_VX"]
        v = datafile[name + "_VY"]
        grid = datafile[name]
        assert u != None, "DTTriangularVectorField2D: no such variable %s in %s" % (name + "_VX", datafile.path())
        assert v != None, "DTTriangularVectorField2D: no such variable %s in %s" % (name + "_VY", datafile.path())
        assert grid != None, "DTTriangularVectorField2D: no such variable %s in %s" % (name, datafile)
        return DTStructuredMesh2D(grid, u, v)

