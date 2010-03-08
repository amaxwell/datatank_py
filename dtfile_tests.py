#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement
import os
import numpy as np
from DTDataFile import DTDataFile

def write_2dmesh(file_path):
    
    output_file = DTDataFile(file_path)
    output_file.DEBUG = True
    # Create and save a single 2D Mesh.  The mesh_function is kind of
    # unnecessary since you can just multiply xx and yy directly, 
    # but it fits well with using a 2D function + grid in DataTank.
    def mesh_function(x,y):
        return x**2+y**2
    
    # return the step to avoid getting fouled up in computing it
    (x, dx) = np.linspace(-10, 10, 50, retstep=True)
    (y, dy) = np.linspace(-10, 10, 100, retstep=True)
    xx, yy = np.meshgrid(x, y)
    mesh = mesh_function(xx, yy)
    
    # save to separate files
    with DTDataFile("mesh.dtbin", truncate=True) as mesh_file:
        mesh_file.write_2dmesh_one(mesh, np.min(x), np.min(y), dx, dy, "TestMesh")
    output_file.write_2dmesh_one(mesh, np.min(x), np.min(y), dx, dy, "TestMesh")
    output_file.close()

def write_images(file_path):
            
    output_file = DTDataFile(file_path)
    output_file.DEBUG = True
    # write a single bitmap image (requires PIL)
    try:
        from PIL import Image
        if os.path.exists("/Library/Desktop Pictures/Art/Poppies Blooming.jpg"):
            image = Image.open("/Library/Desktop Pictures/Art/Poppies Blooming.jpg")
        else:
            image = Image.open("/Library/Desktop Pictures/Nature/Earth Horizon.jpg")
        output_file.write_image_one(image, "Image")
    
        # add an alpha channel and save the new image
        image.putalpha(200)
        output_file.write_image_one(image, "ImageAlpha")
        
    except Exception, e:
        print "failed to load or write image:", e
    output_file.close()
    
def write_arrays(file_path):
    
    output_file = DTDataFile(file_path)
    output_file.DEBUG = True
    # write a 1D array of shorts
    test_array = np.array(range(0, 10), dtype=np.int16)
    output_file.write(test_array, "Test0")
    
    # write a Python list
    output_file.write([0, 10, 5, 7, 9], "TestPythonList")
    
    # write a single number
    output_file.write(10.5, "TestRealNumber")
    
    # write a 2D array of ints
    test_array = np.array(range(0, 10), dtype=np.int32)
    test_array = test_array.reshape((5, 2))
    output_file.write_array(test_array, "Test1", dt_type="Array")
    
    # write a 2D array of doubles
    test_array = test_array.astype(np.float64)
    test_array /= 2.3
    output_file.write_array(test_array, "Test2", dt_type="Array")
    
    # write a 3D array of floats
    test_array = np.array(range(0, 12), dtype=np.float)
    test_array = test_array.reshape(3, 2, 2)
    output_file.write_array(test_array, "Test3", dt_type="Array")
    output_file.close()

def write_test(file_path):
    
    assert os.path.exists(file_path) is False, "delete file before running tests"
    
    # 
    # Note: I tried creating the file here and keeping it open while calling the
    # following functions, but that failed horribly and caused an inconsistent file.
    # Summary: having these open at the same time will cause problems.  Maybe I should
    # add a table of open files or something, and force subsequent access as read-only?
    #
        
    write_2dmesh(file_path)
    write_images(file_path)
    write_arrays(file_path)
        
    output_file = DTDataFile(file_path, truncate=False)    
    output_file.DEBUG = True
    
    # write a time-varying 1D array (list of numbers)
    for idx in xrange(0, 10):
        time_test = np.array(range(idx, idx + 10), np.double)
        output_file.write(time_test, "TimeTest_%d" % (idx), time=idx * 2.)
    
    # write a single string
    output_file.write("Test single string", "TestSingleString")

    # write a time-varying string with Unicode characters
    for idx in xrange(0, 10):
        output_file.write_string(u"Χριστός : time index %d" % (idx), "StringTest_%d" % (idx), time=idx * 2.)
        
    # write a time-varying 2D point collection
    for idx in xrange(0, 10):
        point_test = np.array(range(idx, idx + 10), np.double)
        point_test = point_test.reshape((point_test.size / 2, 2))
        output_file.write_array(point_test, "PointTest_%d" % (idx), dt_type="2D Point Collection", time=idx * 2.)
            
    output_file.close()   

def read_test(file_path):
    
    f = DTDataFile(file_path)
    f.DEBUG = True
    print f
    for name in f:
        # Call this to make sure the variables are actually read, since that will
        # potentially have numerous side effects.  Printing this is overwhelming.
        ignored = f[name]
        
    f.close()
        
if __name__ == '__main__':
    
    if os.path.exists("test.dtbin"):
        os.remove("test.dtbin")
    write_test("test.dtbin")
    read_test("test.dtbin")
    read_test("mesh.dtbin")