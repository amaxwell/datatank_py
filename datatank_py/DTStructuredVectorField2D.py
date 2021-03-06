#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This software is under a BSD license.  See LICENSE.txt for details.

from datatank_py.DTStructuredGrid2D import DTStructuredGrid2D
import numpy as np

class DTStructuredVectorField2D(object):
    """2D vector field on a structured grid."""
    
    dt_type = ("2D Structured Vector Field",)
    """Type strings allowed by DataTank"""
    
    def __init__(self, u, v, grid=None):
        """
        :param u: 2D array of values
        :param v: 2D array of values
        :param grid: :class:`datatank_py.DTStructuredGrid2D.DTStructuredGrid2D` object (defaults to unit grid) or the name of a previously saved grid
        
        Note that the ``u``, ``v`` arrays must be arranged as ``(y, x)`` for compatibility
        with the grid and DataTank.
                        
        """
        
        super(DTStructuredVectorField2D, self).__init__()        
        
        u = np.squeeze(u)
        v = np.squeeze(v)
        shape = np.shape(u)
        assert len(shape) == 2, "values array must be 2D"
        assert np.shape(u) == np.shape(v), "inconsistent array shapes"

        if isinstance(grid, basestring) == False:
            
            if grid == None:
                grid = DTStructuredGrid2D(range(shape[1]), range(shape[0]))
            
            assert shape == grid.shape(), "grid shape %s != value shape %s" % (grid.shape(), shape)
            
        self._grid = grid
        self._u = u
        self._v = v
        
    def grid(self):
        """:returns: a :class:`datatank_py.DTStructuredGrid2D.DTStructuredGrid2D` instance"""
        return self._grid
        
    def u(self):
        """:returns: u component of vector field (2D array)"""
        return self._u
        
    def v(self):
        """:returns: v component of vector field (2D array)"""
        return self._v
    
    def __dt_type__(self):
        return "2D Structured Vector Field"
                
    def __str__(self):
        return self.__dt_type__() + ": " + str(self._grid)
        
    def __dt_write__(self, datafile, name):
        datafile.write_anonymous(self._u, name + "_VX")
        datafile.write_anonymous(self._v, name + "_VY")
        datafile.write_anonymous(self._grid, name)
        
    @classmethod
    def from_data_file(self, datafile, name):
        
        grid = DTStructuredGrid2D.from_data_file(datafile, name)
        u = datafile[name + "_VX"]
        v = datafile[name + "_VY"]
        assert u != None, "Unable to find %s" (name + "_VX")
        assert v != None, "Unable to find %s" (name + "_VY")
        return DTStructuredVectorField2D(u, v, grid=grid)

if __name__ == '__main__':
    
    from DTDataFile import DTDataFile
    with DTDataFile("test/structured_vector_field2d.dtbin", truncate=True) as df:
                
        grid = DTStructuredGrid2D(range(20), range(10))
        # must order value arrays as z, y, x for compatibility with the grid
        u = np.ones((10, 20))
        v = np.ones((10, 20))
        mesh = DTStructuredVectorField2D(u, v, grid=grid)
        df["2D vector field"] = mesh
    
        print (mesh)
