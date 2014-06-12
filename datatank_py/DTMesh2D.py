#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This software is under a BSD license.  See LICENSE.txt for details.

import numpy as np
from DTMask import DTMask

class DTMesh2D(object):
    """2D Mesh object.
    
    This class corresponds to DataTank's DTMesh2D object. Note that
    a 2D Mesh object is always single or double precision floating
    point, so integer values will be converted.
    
    """
    
    dt_type = ("2D Mesh", "Mesh2D")
    """Type strings allowed by DataTank"""
    
    def __init__(self, values, grid=None, mask=None):
        """
        :param values: 2D array of values
        :param grid: (xmin, ymin, dx, dy) or `None` for unit grid
        :param mask: a :class:`datatank_py.DTMask.DTMask` instance
        
        """
        
        super(DTMesh2D, self).__init__()

        # 2D mesh is floating point, either single or double precision
        if values.dtype in (np.int8, np.uint8, np.int16, np.uint16):
            values = values.astype(np.float32)
            
        self._values = values
        self._grid = grid if grid != None else (0, 0, 1, 1)
        self._mask = mask
        
        self._x = None
        self._y = None
        
    def grid(self):
        """:returns: tuple with (xmin, ymin, dx, dy)"""
        return self._grid
        
    def values(self):
        """:returns: numpy array of floating-point values at each grid node"""
        return self._values
        
    def convert_to_dtype(self, value_type):
        """for meshes to be used in computation; may not be saved"""
        self._values = self._values.astype(value_type)
        
    def __iter__(self):
        """:returns: tuple with (x, y, z) where (x, y) is on the spatial grid"""
        vals = self.values()
        mdim, ndim = np.shape(vals)
        
        # create coordinate vectors; may be public at some point
        if self._x is None:
            xmin, ymin, dx, dy = self.grid()
            self._x = np.arange(xmin, ndim * dx + xmin, dx)
            self._y = np.arange(ymin, mdim * dy + ymin, dy)
        
        for m in xrange(0, mdim):
            for n in xrange(0, ndim):
                x = self._x[n]
                y = self._y[m]
                yield((x, y, vals[m, n]))
        
    def mask(self):
        """:returns: a :class:`datatank_py.DTMask.DTMask` instance or None"""
        return self._mask
    
    def __dt_type__(self):
        return "2D Mesh"
        
    def __dt_write__(self, datafile, name):
        
        #
        # 1. Write bounding box as DTRegion2D as "name" + "_bbox2D"
        #    This is a double array with corners ordered (xmin, xmax, ymin, ymax)
        # 2. Write grid using WriteNoSize as "name" + "_loc"
        #    This is a double array with (xmin, ymin, dx, dy)
        # 3. Write mask (ignored for now)
        # 4. Write values as array "name"
        # 5. Write name and type for DataTank
        #
        
        (xmin, ymin, dx, dy) = self._grid 
        xmax = xmin + self._values.shape[1] * float(dx)
        ymax = ymin + self._values.shape[0] * float(dy)

        # will be converted to double arrays
        bbox = (xmin, xmax, ymin, ymax)

        datafile.write_anonymous(bbox, name + "_bbox2D")
        datafile.write_anonymous(self._grid, name + "_loc")
        if self._mask != None:
            datafile.write_anonymous(self._mask, name + "_dom")
        datafile.write_anonymous(self._values, name)

    @classmethod
    def from_data_file(self, datafile, name):
        
        values = np.squeeze(datafile[name])
        grid = np.squeeze(datafile[name + "_loc"])
        # TODO: make sure this is correct; should be writing a packed array instead in __dt_write__?
        mask = DTMask.from_data_file(datafile, name + "_dom")
        if mask != None:
            mask = mask.mask_array()
        assert values != None, "Mesh %s not found in data file" % (name)
        return DTMesh2D(values, grid=grid, mask=mask)

