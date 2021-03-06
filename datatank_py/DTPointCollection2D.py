#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This software is under a BSD license.  See LICENSE.txt for details.

from __future__ import with_statement
import numpy as np

class DTPointCollection2D(object):
    """2D Point collection object.
    
    Supported functions:
    
    * :py:func:`len`
    * :py:func:`for`
    * indexed access, e.g., ``foo[2]`` to get the second point
    
    """
    
    dt_type = ("2D Point Collection",)
    """Type strings allowed by DataTank"""
    
    def __init__(self, xvalues, yvalues):
        """
        :param xvalues: array of x values
        :param yvalues: array of y values
        
        Pass empty arrays to get an empty collection
        that can be added to with add_point().
        
        """
        
        super(DTPointCollection2D, self).__init__()
        
        # Create a new point collection as either
        #     DTPointCollection2D(array)
        # or
        #     DTPointCollection2D(array,vector)
        # the array needs to be allocated as (2,N), where N = number of points.
        # 
        # If you don't know beforehand the size of the array, use the
        # IncreaseSize(...) and TruncateSize(...) functions to resize the array.
        # 
        # The array is layed out as:
        # array(0,j) = x coordinate of point j, array(1,j) = y coordinate of point j.
        
        assert xvalues != None and yvalues != None, "both x and y arrays are required"
        assert len(xvalues) == len(yvalues), "inconsistent lengths"
        
        # internal storage as lists, so add_point performance doesn't suck
        self._xvalues = list(xvalues)
        self._yvalues = list(yvalues)
            
    def bounding_box(self):
        """:returns: tuple with ``(xmin, xmax, ymin, ymax)``"""
        if self._xvalues == None or len(self._xvalues) == 0:
            return (-np.inf, np.inf, -np.inf, np.inf)
        return (np.nanmin(self._xvalues), np.nanmax(self._xvalues), np.nanmin(self._yvalues), np.nanmax(self._yvalues))
        
    def add_point(self, point):
        """Add a point to the collection
        
        :param point: a :class:`datatank_py.DTPoint2D.DTPoint2D` instance
        
        """
        self._xvalues.append(point.x)
        self._yvalues.append(point.y)
        
    def __len__(self):
        # xvalues is a vector, so len works
        return len(self._xvalues)
        
    def __iter__(self):
        for i in xrange(len(self)):
            yield (self._xvalues[i], self._yvalues[i])
        
    def __getitem__(self, idx):
        return (self._xvalues[idx], self._yvalues[idx])
        
    def __str__(self):
        s = "{\n"
        for x, y in self:
            s += "(%s, %s)\n" % (x, y)
        s += "}\n"
        return s
    
    def __dt_type__(self):
        return "2D Point Collection"
        
    def __dt_write__(self, datafile, name):
        datafile.write_anonymous(self.bounding_box(), name + "_bbox2D")
        xvalues = np.array(self._xvalues).astype(np.double)
        yvalues = np.array(self._yvalues).astype(np.double)
        datafile.write_anonymous(np.dstack((xvalues, yvalues)), name)

    @classmethod
    def from_data_file(self, datafile, name):
        
        # 1 x length x 2
        values = datafile[name]
        # now length x 2
        values = np.squeeze(values)
        return DTPointCollection2D(values[:, 0], values[:, 1])
        

if __name__ == '__main__':
    
    from datatank_py.DTDataFile import DTDataFile
    from datatank_py.DTPoint2D import DTPoint2D
    
    with DTDataFile("point_collection_2d.dtbin", truncate=True) as df:
        
        collection = DTPointCollection2D([], [])
        for x in xrange(100):
            collection.add_point(DTPoint2D(x, x * x / 100.))

        df["Point collection 1"] = collection
        
        xvals = (10, 20, 30, 40, 50)
        yvals = xvals
        pc = DTPointCollection2D(xvals, yvals)
        df["Point collection 2"] = pc
        
        print(pc)
