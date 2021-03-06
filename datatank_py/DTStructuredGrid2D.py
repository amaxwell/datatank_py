#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This software is under a BSD license.  See LICENSE.txt for details.

from datatank_py.DTRegion2D import DTRegion2D
from datatank_py.DTMask import DTMask
import numpy as np

def _squeeze2d(array):
    assert array is not None, "DTStructuredGrid2D: nonexistent array passed to _squeeze2d"
    array = np.asarray(array)
    shape = np.shape(array)
    if len(shape) == 2:
        return array

    # let the caller deal with this error; we only want to squeeze
    # a singleton dimension
    if shape[0] != 1:
        return array
        
    new_array = np.zeros(shape[1:], dtype=array.dtype)
    new_array[:,:] = array[0,:,:]
    return new_array

class DTStructuredGrid2D(object):
    """2D structured grid object.
    
    This class corresponds to DataTank's DTStructuredGrid2D.
    
    """
    
    dt_type = ("2D Structured Grid",)
    """Type strings allowed by DataTank"""
    
    def __init__(self, x, y, mask=None):
        """
        :param x: vector or 2D array of x values
        :param y: vector or 2D array of y values
        :param mask: optional :class:`datatank_py.DTMask.DTMask` object
        
        Note: if a full 2D array is passed, it must be ordered as (y, x)
        for compatibility with DataTank.  When using vectors, this is handled
        automatically.
                
        """            
        
        super(DTStructuredGrid2D, self).__init__()
        
        # DataTank saves these with a singleton dimension in z,
        # so we have a special case for reading those files in
        # order to end up with the correct logical shape.
        x = _squeeze2d(x)
        y = _squeeze2d(y)
        
        # this predates the singleton saving changes in DTDataFile
        if (len(np.shape(x)) == 1 and len(np.shape(y)) == 2) and np.shape(y)[1] == 1:
            y = np.squeeze(y)
        
        # datatank_py allows a 1D list or vector; DataTank does not
        if (len(np.shape(x)) == 1 and len(np.shape(y)) == 1):
            
            # If we pass in vectors, DataTank expects them to have a 2D shape,
            # which is kind of peculiar.  This does avoid expanding the full
            # arrays, though.
            
            self._x = np.zeros((1, len(x)), dtype=np.float32)
            self._y = np.zeros((len(y), 1), dtype=np.float32)
            
            self._x[0,:] = x
            self._y[:,0] = y
            self._logical_shape = (len(y), len(x))
            
        elif np.shape(x)[0] == 1 and np.shape(y)[1] == 1:
            
            # 2D arrays with singleton dimension; this is how DataTank passes
            # a square 2D structured grid, for instance
            xlen = np.shape(x)[1]
            ylen = np.shape(y)[0]
            self._x = x
            self._y = y
            self._logical_shape = (ylen, xlen)
                
        else:
            assert np.shape(x) == np.shape(y)
            self._x = np.array(x, dtype=np.float32)
            self._y = np.array(y, dtype=np.float32)            
            self._logical_shape = np.shape(x)
            
        if mask != None:
            assert self.shape() == (mask.n(), mask.m()) and mask.o() == 1, "Invalid mask"
            self._mask = mask
        else:
            self._mask = np.array([], dtype=np.int32)
    
    def __dt_type__(self):
        return "2D Structured Grid"
        
    def shape(self):
        """:returns: the logical grid size (y, x), even if stored as vectors."""
        return self._logical_shape
        
    def bounding_box(self):
        """:returns: a :class:`datatank_py.DTRegion2D.DTRegion2D` instance"""
        return DTRegion2D(np.nanmin(self._x), np.nanmax(self._x), np.nanmin(self._y), np.nanmax(self._y))
        
    def mask(self):
        """:returns: a :class:`datatank_py.DTMask.DTMask` instance or None"""
        return self._mask
        
    def full_x(self):
        """:returns: a 2D array of all x-values"""
        if self._logical_shape == np.shape(self._x):
            return self._x

        full_x = np.zeros(self._logical_shape, dtype=np.float32)
        for idx in xrange(self._logical_shape[0]):
            full_x[idx,:] = self._x[0,:]
        return full_x
 
    def full_y(self):
        """:returns: a 2D array of all y-values"""
        if self._logical_shape == np.shape(self._y):
            return self._y

        full_y = np.zeros(self._logical_shape, dtype=np.float32)
        for idx in xrange(self._logical_shape[1]):
            full_y[:,idx] = self._y[:,0]
        return full_y
                   
    def __str__(self):
        return self.__dt_type__() + ":\n  Bounding Box: " + str(self.bounding_box()) + "\n  Shape: " + str(self.shape())
        
    def __dt_write__(self, datafile, name):
        #datafile.write_anonymous(self.bounding_box(), name + "_bbox2D")
        datafile.write_anonymous(self._x, name + "_X")
        datafile.write_anonymous(self._y, name + "_Y")
        datafile.write_anonymous(self._mask, name)
        
    @classmethod
    def from_data_file(self, datafile, name):
        
        name = datafile.resolve_name(name)
        gridx = datafile[name + "_X"]
        gridy = datafile[name + "_Y"]
        mask = DTMask.from_data_file(datafile, name + "_dom")
        assert gridx is not None, "DTStructuredGrid2D: no such variable %s in %s" % (name + "_X", datafile.path())
        assert gridy is not None, "DTStructuredGrid2D: no such variable %s in %s" % (name + "_Y", datafile)
        return DTStructuredGrid2D(gridx, gridy, mask=mask)

if __name__ == '__main__':
    
    from DTDataFile import DTDataFile
    with DTDataFile("test/structured_grid2d.dtbin", truncate=True) as df:
                
        grid = DTStructuredGrid2D(range(10), range(20))
        df["grid"] = grid
    
        assert grid.shape() == grid.full_x().shape, "inconsistent shapes"
        assert grid.shape() == grid.full_y().shape, "inconsistent shapes"
        
