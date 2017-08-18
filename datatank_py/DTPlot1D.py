#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This software is under a BSD license.  See LICENSE.txt for details.

import numpy as np

class DTPlot1D(object):
    """1D Plot object.
    
    Supported functions:
    
    * :py:func:`len`
    * :py:func:`for`
    
    """
    
    dt_type = ("1D Plot",)
    
    def __init__(self, xvalues, yvalues, points_only=True):
        """
        :param xvalues: array of x values
        :param yvalues: array of y values
        :param boolean points_only: indicating whether shape information is included
        
        **The input arrays must have the same length.**
        
        If `points_only` is set to `False`, `xvalues` and `yvalues` are assumed to have the
        correct packed array format for a :class:`DTPlot1D`, including all subpaths.  Otherwise,
        they are assumed to define points of a single path, and the necessary subpath
        metadata is computed.  In general, you would only pass `False` if reading a path
        from a file generated by DataTank.
        
        In DTSource, the array has one of two formats:
          #. 2xN with a packed loop format.
          #. 4xN that saves every line segment.
          
        In datatank_py, only the 2xN format is supported.  It's more efficient, and more
        compatible with DTSource manipulation.
        
        Layout is:
          | ``DTPlot1D._xvalues = [ 0 x1 .... xN 0 x1 ... xM ...]``
          | ``DTPlot1D._yvalues = [ N y1 .... yN M y1 ... yM ...]``
        
        This allows multiple loops to be saved in a single array.
        
        :class:`DTPlot1D` allows iteration over subpaths (called "loops" in DTSource),
        for easier manipulation and serialization of individual paths.
        
        """
        super(DTPlot1D, self).__init__()
        assert xvalues is not None and yvalues is not None, "DTPlot1D: both x and y arrays are required"
        assert len(xvalues) == len(yvalues), "DTPlot1D: inconsistent lengths"   
        
        xvalues = np.array(xvalues).astype(np.double)
        yvalues = np.array(yvalues).astype(np.double)
        
        if points_only and len(xvalues):
            xvalues = np.insert(xvalues, 0, 0)
            yvalues = np.insert(yvalues, 0, len(yvalues))
            
        self._xvalues = xvalues
        self._yvalues = yvalues
    
    def add_loop(self, xvalues, yvalues):
        """Add a loop (subpath) to this path.
        
        :param xvalues: vector of x coordinates
        :param yvalues: vector of y coordinates
        
        """
        assert len(xvalues) == len(yvalues), "DTPlot1D: inconsistent lengths"
        xvalues = np.array(xvalues).astype(np.double)
        yvalues = np.array(yvalues).astype(np.double)
        if len(xvalues) > 0:
            xvalues = np.insert(xvalues, 0, 0)
            yvalues = np.insert(yvalues, 0, len(yvalues))
            self._xvalues = np.append(self._xvalues, xvalues)
            self._yvalues = np.append(self._yvalues, yvalues)
    
    def number_of_loops(self):
        """:returns: number of subpaths (loops) in this path."""
        return len(self._offsets())
        
    def point_list(self):
        """:returns: a list of DTPoint2D objects.
        
        Raises an exception if this path has subpaths, so iterate
        if you have multiple loops. Note that these loops will be
        single-loop paths.
        
        >>> all_points = []
        >>> for subpath in path:
        ...   all_points += subpath.point_list()
        
        """
        
        from DTPoint2D import DTPoint2D
        assert self.number_of_loops() == 1, "Point access is only available for single-loop paths"
        return [DTPoint2D(x, y) for x, y in zip(self._xvalues[1:], self._yvalues[1:])]
        
    def point_arrays(self):
        """:returns: a two-tuple with x and y vectors

        Raises an exception if this path has subpaths, so iterate
        if you have multiple loops.

        """

        assert self.number_of_loops() == 1, "Point access is only available for single-loop paths"
        return (self._xvalues[1:], self._yvalues[1:])
            
    def sparsified_path(self, step):
        """:returns: a sparsified path (copy) of the receiver.
        
        Sparsifies by index; no smoothing or distance considerations
        
        Sparsifies a new path by taking every N-th point, where N = step.
        Does not modify the original path object.  If a closed path was
        passed in, the returned path is also closed.  Raises an exception
        if sparsifying any subpath would result in fewer than 2 points.
        
        """
        
        sparse_path = None
        # may be a double, if coming from DTDataFile
        step = int(step)
        
        for subpath in self:
            
            # only 1 deep, so these have no subpaths
            xvals = subpath._xvalues[1:]
            yvals = subpath._yvalues[1:]
            
            indices = np.arange(0, len(xvals), step)
            xvals = xvals[indices]
            yvals = yvals[indices]            
            
            # DTSource doesn't appear to impose this, but DataTank does
            assert len(xvals) > 1, "DTPlot1D: A valid path requires at least two points."
            
            def _is_subpath_closed(path):
                
                # can't close an empty path or a single point
                if len(xvals) < 2:
                    return False
                    
                first_x, first_y = path._xvalues[1], path._yvalues[1]
                last_x, last_y = path._xvalues[-1], path._yvalues[-1]
                return first_x == last_x and first_y == last_y
                
            # manipulates the new path in-place
            def _close_subpath(path):
                # don't close a path that is already closed
                if not _is_subpath_closed(path):
                    first_x, first_y = path._xvalues[1], path._yvalues[1]
                    path._xvalues = np.append(path._xvalues, (first_x,))
                    path._yvalues = np.append(path._yvalues, (first_y,))
                    # update length metadata for this subpath!
                    path._yvalues[0] += 1
            
            if sparse_path == None:
                sparse_path = DTPlot1D(xvals, yvals)
                if _is_subpath_closed(subpath):
                    _close_subpath(sparse_path)
            else:
                sparse_path.add_loop(xvals, yvals)
                
        return sparse_path
    
    def _offsets(self):
        """List of starting index and length of each subpath element"""        
        
        offsets = []
        # (start, length)
        # int conversion is necessary to use this as a slice
        offset = (1, int(self._yvalues[0]))
        offsets.append(offset)
        next = offset[1] + 1
        
        while (next + 1) < len(self._yvalues):
            # next is index of the length; start is the index after that
            assert self._yvalues[next] > 0, "DTPlot1D: negative index in offset computation"
            offset = (next + 1, self._yvalues[next])
            offsets.append(offset)
            next += offset[1] + 1
                            
        return offsets
        
    def __iter__(self):
        """Iterate subpaths in order of addition as DTPlot1D objects"""
        
        for offset in self._offsets():
            start, length = offset
            yield (DTPlot1D(self._xvalues[start:start + length], self._yvalues[start:start + length]))
        
    def __str__(self):
        s = super(DTPlot1D, self).__str__() + " {\n"
        for idx, subpath in enumerate(self):
            s += "\n  Subpath %d (%d elements)\n" % (idx, len(subpath._xvalues) - 1)
            for x, y in zip(subpath._xvalues[1:], subpath._yvalues[1:]):
                s += "    (%s, %s)\n" % (x, y)
        s += "}\n"
        return s
        
    def __len__(self):
        total_length = 0
        for p in self:
            total_length += (len(p._xvalues) - 1)
        return total_length
    
    def __dt_type__(self):
        return "1D Plot"
        
    def __dt_write__(self, datafile, name):
        datafile.write_anonymous(np.dstack((self._xvalues, self._yvalues)), name)
        
    @classmethod
    def from_data_file(self, datafile, name):
        
        packed_values = datafile[name]
        packed_values = np.squeeze(packed_values)
        
        xvalues = packed_values[:,0]
        yvalues = packed_values[:,1]
        path = DTPlot1D(xvalues, yvalues, points_only=False)
            
        return path

if __name__ == '__main__':
    
    # this entire file is just a copy-paste hack of DTPath2D
    
    from datatank_py.DTDataFile import DTDataFile
    
    with DTDataFile("plot_1d.dtbin", truncate=True) as df:
        
        xvalues = (1, 2, 2, 1, 1)
        yvalues = (1, 1, 2, 2, 1)

        df["Plot 1"] = DTPlot1D(xvalues, yvalues)
        
        xvalues = np.array(xvalues) * 2
        yvalues = np.array(yvalues) * 2
        df["Plot 2"] = DTPlot1D(xvalues, yvalues)
        
        xvalues = np.linspace(0, 10, num=100)
        yvalues = np.sin(xvalues)
        xvalues = np.append(xvalues, np.flipud(xvalues))
        xvalues = np.append(xvalues, xvalues[0])
        yvalues = np.append(yvalues, -yvalues)
        yvalues = np.append(yvalues, yvalues[0])
        df["Plot 3"] = DTPlot1D(xvalues, yvalues)
        
        xvalues = np.array((-1, -1, 1, 1, -1))
        yvalues = np.array((-1, 1, 1, -1, -1))
        Plot = DTPlot1D(xvalues, yvalues)
        xvalues = xvalues * 0.5
        yvalues = yvalues * 0.5
        path.add_loop(xvalues, yvalues)
        df["Plot 4"] = path
        
        for idx, subpath in enumerate(path):
            df["Subplot %d" % (idx)] = path
        
        
