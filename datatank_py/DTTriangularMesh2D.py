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
            
            grid_filename = "grid.txt"
            depth_filename = "depths.txt"
            
            bathy_mesh = parse_bathymetry_mesh_from_path(grid_filename)
            shared_grid_name = grid_filename
            
            with DTDataFile("Output.dtbin", truncate=True) as dtf:
                dtf["Bathymetry"] = bathy_mesh
                dtf.write_anonymous(bathy_mesh.grid(), shared_grid_name)
                dtf.write_anonymous("2D Triangular Mesh", "Seq_Depth")
                
                with open(depth_filename, "rU") as asciivalues:
                    
                    passed_header = False
                    timeval = None
                    accumulated_values = []
                    time_index = 0
                    base_timeval = None
                    
                    for lineidx, line in enumerate(asciivalues):
                        
                        line = line.strip()
                        if line.startswith("TS"):
                            if timeval is not None:
                                assert passed_header is True
                                if base_timeval is None:
                                    base_timeval = timeval
                                mesh = DTTriangularMesh2D(bathy_mesh.grid(), np.array(accumulated_values, dtype=np.float32))
                                dttime_hours = (timeval - base_timeval) / 3600.
                                mesh.write_with_shared_grid(dtf, "Depth", shared_grid_name, dttime_hours, time_index)
                                #dtf.write(mesh, "Depth_%d" % (time_index), time=(timeval - base_timeval))
                                #dtf.write_anonymous(shared_grid_name, "Depth_%d" % (time_index))
                                #dtf.write_anonymous(np.array(accumulated_values).astype(np.float32), "Depth_%d_V" % (time_index))
                                #dtf.write_anonymous(np.array((timeval - base_timeval,)), "Depth_%d_time" % (time_index))
                                time_index += 1
                                
                            ts, zero, time_str = line.split()
                            timeval = float(time_str)
                            accumulated_values = []
                            passed_header = True
                    
                        elif passed_header and not line.startswith("ENDDS"):
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

