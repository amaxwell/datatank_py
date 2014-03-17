#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This software is under a BSD license.  See LICENSE.txt for details.

from DTRegion2D import DTRegion2D
import numpy as np

class DTTriangularGrid2D(object):
    """2D triangular grid object. This is a collection of points interconnected
    to form triangles. DataTank does not support a mask for this type of grid,
    but it's very useful for creating 3D surfaces and certain computations.
    """
    
    dt_type = ("2D Triangular Grid",)
    """Type strings allowed by DataTank"""
    
    def __init__(self, connections, points):
        """
        :param connections: 2D array of connections [ m x 3 ]
        :param points: 2D array of points [ m x 2 ]
        
        Each x,y node is connected to three other nodes, as seen in this
        contrived example:
        
        ===========   =======  =======  ============  ============  ============
        Point Index   Point X  Point Y  Connection 1  Connection 2  Connection 3
        ===========   =======  =======  ============  ============  ============
        0             1.0      1.0      2             5             7
        1             2.0      1.0      1             7             9
        …             …        …        …             …             …
        m             99.0     99.0     m-1           m-20          m-57
        ===========   =======  =======  ============  ============  ============
        
        The values in the ``connections`` array refer to point indices, and
        allow reconstruction of the unstructured triangular network.
                
        """            
                           
        super(DTTriangularGrid2D, self).__init__()

        assert np.shape(connections)[1] == 3
        assert np.shape(points)[1] == 2
        self._connections = connections
        self._points = points
    
    def __dt_type__(self):
        return "2D Triangular Grid"
        
    def number_of_points(self):
        """:returns: the number of points in the grid"""
        return np.shape(self._points)[0]
        
    def bounding_box(self):
        """:returns: a :class:`datatank_py.DTRegion2D.DTRegion2D` instance"""
        return DTRegion2D(np.nanmin(self._points[:,0]), np.nanmax(self._points[:,0]), np.nanmin(self._points[:,1]), np.nanmax(self._points[:,1]))
        
    def __str__(self):
        return self.__dt_type__() + ":\n  Bounding Box: " + str(self.bounding_box()) + "\n  Points: " + str(self.number_of_points())
        
    def __dt_write__(self, datafile, name):
        datafile.write_anonymous(self.bounding_box(), name + "_bbox2D")
        datafile.write_anonymous(self._points, name + "_pts")
        datafile.write_anonymous(self._connections, name)
        
    @classmethod
    def from_data_file(self, datafile, name):
        
        name = datafile.resolve_name(name)
        points = datafile[name + "_pts"]
        conns = datafile[name]
        assert points != None, "DTTriangularGrid2D: no such variable %s in %s" % (name + "_pts", datafile.path())
        assert conns != None, "DTTriangularGrid2D: no such variable %s in %s" % (name, datafile)
        return DTStructuredGrid2D(conns, points)

