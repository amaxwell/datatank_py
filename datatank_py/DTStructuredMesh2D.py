#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This software is under a BSD license.  See LICENSE.txt for details.

from DTStructuredGrid2D import DTStructuredGrid2D, _squeeze2d
import numpy as np

class DTStructuredMesh2D(object):
    """2D structured mesh object.
    
    This class corresponds to DataTank's DTStructuredMesh2D.
    
    """
    
    dt_type = ("2D Structured Mesh",)
    """Type strings allowed by DataTank"""
    
    def __init__(self, values, grid=None):
        """
        :param values: 2D array of values
        :param grid: DTStructuredGrid2D object (defaults to unit grid) or the name of a previously saved grid
        
        Note that the values array must be ordered as (y, x) for compatibility
        with the grid and DataTank.
                
        """                   
        
        super(DTStructuredMesh2D, self).__init__()
        
        values = _squeeze2d(values)
        shape = np.shape(values)
        assert len(shape) == 2, "values array must be 2D"

        if isinstance(grid, basestring) == False:
            
            if grid == None:
                grid = DTStructuredGrid2D(range(shape[1]), range(shape[0]))
            
            assert shape == grid.shape(), "grid shape %s != value shape %s" % (grid.shape(), shape)
            
        self._grid = grid
        self._values = values
    
    def grid(self):
        """:returns: a :class:`datatank_py.DTStructuredGrid2D.DTStructuredGrid2D` instance"""
        return self._grid
        
    def values(self):
        """:returns: a 2D numpy array of values at each grid node"""
        return self._values
        
    def __dt_type__(self):
        return "2D Structured Mesh"
                
    def __str__(self):
        return self.__dt_type__() + ":\n " + str(self._grid) + "\n" + " Values:\n " + str(self._values)
        
    def __dt_write__(self, datafile, name):
        datafile.write_anonymous(self._grid, name)
        datafile.write_anonymous(self._values, name + "_V")
        
    def write_with_shared_grid(self, datafile, name, grid_name, time, time_index):
        """Allows saving a single grid and sharing it amongst different time
        values of a variable.
        
        :param datafile: a :class:`datatank_py.DTDataFile.DTDataFile` open for writing
        :param name: the mesh variable's name
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
        datafile.write_anonymous(self._values, varname + "_V")
        datafile.write_anonymous(np.array((time,)), varname + "_time")
        
    @classmethod
    def from_data_file(self, datafile, name):
    
        grid = DTStructuredGrid2D.from_data_file(datafile, name)
        values = datafile[name + "_V"]
        return DTStructuredMesh2D(values, grid=grid)

if __name__ == '__main__':
    
    from DTDataFile import DTDataFile
    with DTDataFile("test/structured_mesh2D.dtbin", truncate=True) as df:
                
        xvals = np.exp(np.array(range(18), dtype=np.float) / 5)
        yvals = np.exp(np.array(range(20), dtype=np.float) / 5)
        grid = DTStructuredGrid2D(xvals, yvals)
        values = np.zeros(len(xvals) * len(yvals))
        for i in xrange(len(values)):
            values[i] = i
            
        # DataTank indexes differently from numpy; the grid is z,y,x ordered
        values = values.reshape(grid.shape())
        
        mesh = DTStructuredMesh2D(values, grid=grid)
        df["2D mesh"] = mesh

        