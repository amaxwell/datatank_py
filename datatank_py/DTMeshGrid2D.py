#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This software is under a BSD license.  See LICENSE.txt for details.

import numpy as np
from DTMask import DTMask

class DTMeshGrid2D(object):
    """2D Grid object.
    
    This class corresponds to DataTank's DTMeshGrid2D object.
    
    """
    
    dt_type = ("2D Mesh Grid", "Mesh2DGrid")
    """Type strings allowed by DataTank"""
    
    def __init__(self, x, y, dx, dy, m, n, mask=None):
        """
        :param x: lower left origin x in physical space
        :param y: lower left origin y in physical space
        :param dx: dx in physical space
        :param dy: dy in physical space
        :param m: grid y dimension in logical space
        :param n: grid x dimension in logical space
        :param mask: a :class:`datatank_py.DTMask.DTMask` instance
        
        """
        
        super(DTMeshGrid2D, self).__init__()

        self._mask = mask
        
        # N dimension: spatial X
        # M dimension: spatial Y
        
        self._m = m
        self._n = n
        
        self._dx = dx
        self._dy = dy
        
        self._x = np.arange(x, n * dx + x, dx)
        self._y = np.arange(y, m * dy + y, dy)

    def tuple(self):
        return (self._x, self._y, self._dx, self._dy)
        
    def x_vec(self):
        return self._x
        
    def y_vec(self):
        return self._y
        
    def full_x(self):
        xvals, yvals = np.meshgrid(self.x_vec(), self.y_vec())
        return xvals
        
    def full_y(self):
        xvals, yvals = np.meshgrid(self.x_vec(), self.y_vec())
        return yvals
        
    def __iter__(self):
        """:returns: tuple with (x, y) where (x, y) is on the spatial grid"""        
        for m in xrange(0, self._m):
            for n in xrange(0, self._n):
                yield((self._x[n], self._y[m]))
        
    def mask(self):
        """:returns: a :class:`datatank_py.DTMask.DTMask` instance or None"""
        return self._mask
    
    def __dt_type__(self):
        return "2D Mesh Grid"
        
    def __dt_write__(self, datafile, name):

        datafile.write_anonymous((self._m, self._n), name + "_size")
        if self._mask != None:
            datafile.write_anonymous(self._mask, name + "_mask")
        datafile.write_anonymous(self.tuple(), name)

    @classmethod
    def from_data_file(self, datafile, name):
        
        base = np.squeeze(datafile[name])
        size = np.squeeze(datafile[name + "_size"])
        
        # TODO: make sure this is correct; should be writing a packed array instead in __dt_write__?
        mask = DTMask.from_data_file(datafile, name + "_dom")
        if mask != None:
            mask = mask.mask_array()
        assert base != None, "Grid %s not found in data file" % (name)
        return DTMeshGrid2D(base[0], base[1], base[2], base[3], size[0], size[1], mask=mask)

