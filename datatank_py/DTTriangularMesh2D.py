#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This software is under a BSD license.  See LICENSE.txt for details.

import numpy as np

class DTTriangularMesh2D(object):
    """2D triangular mesh object."""
    
    dt_type = ("2D Triangular Mesh",)
    """Type strings allowed by DataTank"""
    
    def __init__(self, grid, values):
        """
        :param grid: :class:`datatank_py.DTTriangularGrid2D.DTTriangularGrid2D` instance
        :param values: vector or list of values in nodal order
                
        """            

        super(DTTriangularMesh2D, self).__init__()
                           
        values = np.squeeze(values)
        assert grid.number_of_points() == len(values)
        self._grid = grid
        self._values = values
    
    def __dt_type__(self):
        return "2D Triangular Mesh"
        
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
        :param name: the mesh variable's name
        :param grid_name: the grid name to be shared (will not be visible in DataTank)
        :param time: the time value for this step (DataTank's ``t`` variable)
        :param time_index: the corresponding integer index of this time step
        
        This is an advanced technique, but it can give a significant space savings in
        a data file. It's not widely implemented, since it's not clear yet if this
        is the best API, but the following example shows how it's used::
        
            #!/usr/bin/env python
            
            import numpy as np

            from datatank_py.DTDataFile import DTDataFile
            from datatank_py.DTTriangularGrid2D import DTTriangularGrid2D
            from datatank_py.DTTriangularMesh2D import DTTriangularMesh2D
            
            # files that exist in the current directory
            grid_filename = "grid.txt"
            
            # this is a time-varying list of depths at each node
            depth_filename = "depths.txt"
            
            # function that returns a DTTriangularGrid2D
            grid = parse_grid_from_path(grid_filename)
            
            # this can be any string; the user won't see it
            shared_grid_name = grid_filename
            
            with DTDataFile("Output.dtbin", truncate=True) as dtf:
                
                # a bunch of this is related to parsing the textfile                
                with open(depth_filename, "rU") as asciivalues:
                    
                    # here we have some state variables, but the time ones are relevant
                    passed_header = False
                    accumulated_values = []
                    
                    # this is a time extracted from the file (a floating point value)
                    timeval = None
                    
                    # this is the zero-based index of the timeval
                    time_index = 0
                    
                    # this is the initial value of the timeval variable
                    base_timeval = None
                    
                    for lineidx, line in enumerate(asciivalues):
                        
                        line = line.strip()
                        if line.startswith("TS"):
                            
                            # If we've already seen a timeval, a "TS" marker means that we're starting 
                            # another block of depth values so we're going to save the previous 
                            # timestep to disk.
                            if timeval is not None:
                                assert passed_header is True
                                
                                # save the t0 if we haven't already done so
                                if base_timeval is None:
                                    base_timeval = timeval
                                    
                                # create a DTTriangularMesh2D as usual, with grid and values
                                # note that a 32-bit float will save significant space over
                                # a double, if you can live with the reduced precision.
                                mesh = DTTriangularMesh2D(grid, np.array(accumulated_values, dtype=np.float32))
                                
                                # This is the floating point time value that will be used for
                                # DataTank's time slider. Here I'm using hours.
                                dttime_hours = (timeval - base_timeval) / 3600.
                                
                                # Now, save it off. The variable in the file will be visible as "Depth",
                                # and write_with_shared_grid() will take care of saving the grid for the
                                # first time and then saving the name on subsequent time steps.
                                #
                                # The dttime_hours variable is our slider time, and time_index is passed
                                # so that write_with_shared_grid() can create the correct variable name,
                                # i.e., "Depth_0, Depth_1, Depth_2, … Depth_N" for successive time steps.
                                #
                                mesh.write_with_shared_grid(dtf, "Depth", shared_grid_name, dttime_hours, time_index)
                                
                                #
                                # This code shows what write_with_shared_grid() is really doing in our specific
                                # example:
                                #
                                # dtf.write(mesh, "Depth_%d" % (time_index), time=(timeval - base_timeval))
                                # dtf.write_anonymous(shared_grid_name, "Depth_%d" % (time_index))
                                # dtf.write_anonymous(np.array(accumulated_values).astype(np.float32), "Depth_%d_V" % (time_index))
                                # dtf.write_anonymous(np.array((timeval - base_timeval,)), "Depth_%d_time" % (time_index))
                                
                                time_index += 1
                            
                            # update our state variables and continue parsing the file    
                            ts, zero, time_str = line.split()
                            timeval = float(time_str)
                            
                            # this will be the start of a new vector of depth values
                            accumulated_values = []
                            passed_header = True
                    
                        elif passed_header and not line.startswith("ENDDS"):
                            # here we're just saving off an individual depth value for a node
                            accumulated_values.append(float(line))    
                        else:
                            print "Ignored: %s" % (line)


        """
        
        if grid_name not in datafile:
            datafile.write_anonymous(self._grid, grid_name)
            datafile.write_anonymous(self.__dt_type__(), "Seq_" + name)
            
        varname = "%s_%d" % (name, time_index)
        datafile.write_anonymous(grid_name, varname)
        datafile.write_anonymous(self._values, varname + "_V")
        datafile.write_anonymous(np.array((time,)), varname + "_time")
        
    def __str__(self):
        return self.__dt_type__() + ":\n  grid = " + str(self._grid)
        
    def __dt_write__(self, datafile, name):
        datafile.write_anonymous(self._values, name + "_V")
        datafile.write_anonymous(self._grid, name)
        
    @classmethod
    def from_data_file(self, datafile, name):
        
        name = datafile.resolve_name(name)
        values = datafile[name + "_V"]
        grid = datafile[name]
        assert values != None, "DTTriangularMesh2D: no such variable %s in %s" % (name + "_V", datafile.path())
        assert grid != None, "DTTriangularMesh2D: no such variable %s in %s" % (name, datafile)
        return DTStructuredMesh2D(grid, values)

