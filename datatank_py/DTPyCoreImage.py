#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This software is under a BSD license.  See LICENSE.txt for details.

# NB: loading all of the bridged modules up front results in a
# pretty huge performance hit (~ 1 second just in importing).

import numpy as np

def __interleaved_rgb_from_planes(red, green, blue):
    
    red = np.asarray(red)
    green = np.asarray(green)
    blue = np.asarray(blue)

    (height, width) = red.shape
    plane_length = height * width
    mesh_data = np.zeros(plane_length * 3, dtype=red.dtype)
    
    mesh_data[0::3] = red.flatten()
    mesh_data[1::3] = green.flatten()
    mesh_data[2::3] = blue.flatten()
        
    return mesh_data
    
def __ns_data_from_array(a):
    
    from Foundation import NSData
    
    a = np.asarray(a).flatten()
    if a.dtype == np.uint8 or a.dtype == np.int8:
        datasize = 1
    elif a.dtype == np.uint16 or a.dtype == np.int16:
        datasize = 2
    elif a.dtype == np.float32:
        datasize = 4
    else:
        assert 0, "unhandled data type %s" % (a.dtype)
        
    buf = buffer(a)
    
    return datasize, NSData.dataWithBytes_length_(buf, len(buf) * datasize)
    
def __bitmap_planes_from_imagerep(image_rep):
    
    assert image_rep.pixelsWide() == image_rep.bytesPerRow() / 4, "packed rows required"
    buf = image_rep.bitmapData()
    height = image_rep.pixelsHigh()
    width = image_rep.pixelsWide()
    
    red = np.fromstring(buf[0::4], dtype=np.uint8).reshape((height, width))
    green = np.fromstring(buf[1::4], dtype=np.uint8).reshape((height, width))
    blue = np.fromstring(buf[2::4], dtype=np.uint8).reshape((height, width))
    alpha = np.fromstring(buf[3::4], dtype=np.uint8).reshape((height, width))
    
    return (red, green, blue, alpha)
    
def ci_image_from_planes(red, green, blue):
    """Create a Quartz CIImage from bitmap data.
    
    :param red: a NumPy 2D array of bitmap values
    :param green: a NumPy 2D array of bitmap values
    :param blue: a NumPy 2D array of bitmap values
    
    :returns: a :class:`Quartz.CIImage` instance
    
    **Requires Mac OS X and PyObjC**
    
    The :class:`Quartz.CIImage` is only useful for applying :class:`Quartz.CIFilter`
    or other transformations using PyObjC. Only 8-bit RGB images are supported at
    this time, and your image data will be truncated if it is not 8-bit.
    
    """
    
    from Quartz import CIImage
    from Quartz import CGDataProviderCreateWithCFData, CGImageCreate, CGColorSpaceCreateWithName
    from Quartz import kCGImageAlphaNone, kCGBitmapByteOrderDefault, kCGRenderingIntentDefault, kCGColorSpaceGenericRGB
    
    # convert to 8 bits, just to simplify life a bit
    red = red.astype(np.uint8)
    green = green.astype(np.uint8)
    blue = blue.astype(np.uint8)
    
    (height, width) = red.shape
    plane_length = height * width
    
    # I can't create an NSBitmapImageRep with these parameters, and it
    # squawks about them.  Since it works in Obj-C, there's apparently something
    # screwed up in the bridge.  CGImage is more reliable, but it doesn't accept
    # planar data, so I have to interleave it manually.  Not a big deal, but it's
    # not a big speed win, and it's annoying.
    
    mesh_data = __interleaved_rgb_from_planes(red, green, blue)
    bytes_per_sample, ns_mesh_data = __ns_data_from_array(mesh_data)
    
    cspace = CGColorSpaceCreateWithName(kCGColorSpaceGenericRGB)
    provider = CGDataProviderCreateWithCFData(ns_mesh_data)
    info = kCGImageAlphaNone | kCGBitmapByteOrderDefault
    cg_image = CGImageCreate(width, height, 8, 24, width * 3 * bytes_per_sample, cspace, info, provider, None, False, kCGRenderingIntentDefault)
    assert cg_image, "unable to create CGImage"
    ci_image = CIImage.imageWithCGImage_(cg_image)
    assert ci_image, "unable to create CIImage"
    
    return ci_image
    
def dt_bitmap2d_from_ci_image(ci_image, width, height, grid):
    """
    :param ci_image: a :class:`Quartz.CIImage` instance from PyObjC
    :param width: desired width in pixels
    :param height: desired height in pixels
    :param grid: a four-tuple (x0, y0, dx, dy) spatial grid
    
    :returns: a :class:`datatank_py.DTBitmap2D.DTBitmap2D` instance
    
    **Requires Mac OS X and PyObjC**

    This function allows you to turn a :class:`Quartz.CIImage` into an object
    that DataTank can use. Only 8-bit RGB images are supported at this time.
    
    """
    
    from datatank_py.DTBitmap2D import DTBitmap2D
    from Quartz import CGRectMake, CGPointZero
    from AppKit import NSBitmapImageRep, NSCalibratedRGBColorSpace, NSGraphicsContext
    
    # No matter what, I can't get NSBitmapImageRep to create a rep from planar data or
    # a passed-in buffer, so I have to let it manage the buffer.  Constraining row bytes
    # seems to work properly, so at least I don't have to deal with that.  I really think
    # PyObjC is buggy here as well.
    
    image_rep = NSBitmapImageRep.alloc().initWithBitmapDataPlanes_pixelsWide_pixelsHigh_bitsPerSample_samplesPerPixel_hasAlpha_isPlanar_colorSpaceName_bitmapFormat_bytesPerRow_bitsPerPixel_(None, width, height, 8, 4, True, False, NSCalibratedRGBColorSpace, 0, 4 * width, 32)
    
    ns_context = NSGraphicsContext.graphicsContextWithBitmapImageRep_(image_rep)
    ns_context.CIContext().drawImage_atPoint_fromRect_(ci_image, CGPointZero, CGRectMake(0, 0, width, height))
    ns_context.flushGraphics()
    
    (red, green, blue, alpha) = __bitmap_planes_from_imagerep(image_rep)
    dt_bitmap = DTBitmap2D()
    dt_bitmap.red = red
    dt_bitmap.green = green
    dt_bitmap.blue = blue
    dt_bitmap.grid = grid
    
    return dt_bitmap
    
def ci_filter_named(filter_name):
    """:returns: a :class:`Quartz:CIFilter` with the given name

    **Requires Mac OS X and PyObjC**
    
    These filters can be applied to a :class:`Quartz.CIImage` using::
    
        ci_image = ci_image_from_planes(r, g, b)
        filt = ci_filter_named("CIExposureAdjust")
        filt.setValue_forKey_(ci_image, "inputImage")
        filt.setValue_forKey_(0.2, "inputEV")
        ci_image = filt.valueForKey_("outputImage")
    
    From this point, you would apply another filter or use :func:`dt_bitmap2d_from_ci_image` 
    to convert the image to
    a :class:`datatank_py.DTBitmap2D.DTBitmap2D` for DataTank.
    
    """
    from Quartz import CIFilter
    return CIFilter.filterWithName_(filter_name)

