#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This software is under a BSD license.  See LICENSE.txt for details.

import numpy as np
import sys

def _is_string(x):
    try:
        basestring
    except NameError:
        basestring = str
    return isinstance(x, basestring)

class _DTBitmap2D(type):
    """Metaclass of DTBitmap2D which implements __call__ in order to
    return a private subclass based on input arguments.  First argument 
    is a path or PIL image, or None.  Returns None if PIL and GDAL fail, 
    which may or may not be correct.
    """
    def __call__(cls, *args, **kwargs):
        
        obj = None
        path_or_image = args[0] if len(args) else None
        if path_or_image is None:
            cls = DTBitmap2D
            obj = cls.__new__(cls, *args, **kwargs)
            obj.__init__(*args, **kwargs)
        else:
            # a string must be a path, so try GDAL first
            if _is_string(path_or_image):
                try:
                    cls = _DTGDALBitmap2D
                    obj = cls.__new__(cls, *args, **kwargs)
                    obj.__init__(*args, **kwargs)
                except Exception as e:
                    sys.stderr.write("Failed to create GDAL representation: %s\n" % (e))
                    obj = None
            
            # if GDAL failed or we had a PIL image, try PIL
            if obj == None:
                try:
                    cls = _DTPILBitmap2D
                    obj = cls.__new__(cls, *args, **kwargs)
                    obj.__init__(*args, **kwargs)
                except Exception as e:
                    sys.stderr.write("Failed to create PIL representation: %s\n" % (e))
                    obj = None

        return obj

# Using metaclass as kw argument is the Python 3 style, as __metaclass__
# is now ignored. That was a nightmare to find.
class DTBitmap2D(object, metaclass=_DTBitmap2D):
    """Base implementation for DTBitmap2D. This is a gray or color (RGB)
    image, with an optional alpha channel. It also has spatial data, so
    it can be displayed in DataTank on a physical grid, rather than the
    logical grid of pixels.
        
    Provides implementation of :class:`datatank_py.DTPyWrite.DTPyWrite` for
    all subclasses, and can be instantiated directly to use as a container.
            
    """
    
    __metaclass__ = _DTBitmap2D
    CHANNEL_NAMES = ("red", "green", "blue", "alpha", "gray")
    dt_type = ("2D Bitmap",)
    
    def __init__(self, path_or_image=None, rgba_bands=None):
        """
        :param path_or_image: a path to an image file or a PIL image object
        :param rgba_bands: a 1-4 element tuple mapping one-based band indexes to (r, g, b, a)

        :returns: An object that implements :class:`datatank_py.DTPyWrite.DTPyWrite`. Don't rely on the class name for anything.
        
        If you pass the default argument, you'll get back
        an object that implements :meth:`dt_write`, and you are responsible for
        filling in its attributes.  These are:
        
        :member grid: optional, of the form [x0, y0, dx, dy]
        :member red: required for RGB image only
        :member green: required for RGB image only
        :member blue: required for RGB image only
        :member gray: required for grayscale image only
        :member alpha: optional
        :member projection: optional WKT string
          
        Each must be a 2D numpy array, and you are responsible for ensuring
        a consistent shape and proper dimension.  This is basically 
        equivalent to the way DTSource constructs a C++ :class:`DTBitmap2D`.  Note that 
        DataTank only supports 8 bit and 16 bit images.

        If a PIL image is provided, it will be used as-is, and the grid
        will be a unit grid with origin at (0, 0).  If a path is provided,
        :class:`DTBitmap2D` will try to use GDAL to load the image and extract its
        components, as well as any spatial referencing included with the
        image.  If GDAL fails for any reason, PIL will be used as a fallback.
        
        If you have an image with more than 4 bands, you can choose which to
        represent as red, green, blue, and alpha by passing :param rgba_bands:.
        For instance, if you have LANDSAT 8 multispectral imagery, you could pass
        (4, 3, 2) to get a true color image. By default, instantiating an image
        with more than 4 bands will give an error.

        Note that :class:`DTBitmap2D` does not attempt to be lazy at loading data; it
        will read the entire image into memory as soon as you instantiate it.
        
        """
        super(DTBitmap2D, self).__init__()
        self.grid = (0, 0, 1, 1)
        self.nodata = None
        self.projection = None
        for n in DTBitmap2D.CHANNEL_NAMES:
            setattr(self, n, None)
    
    def dtype(self):
        """:returns: a NumPy array datatype :class:`numpy.dtype`"""
        for x in DTBitmap2D.CHANNEL_NAMES:
            v = getattr(self, x)
            if v is not None:
                return v.dtype
        return None
        
    def channel_count(self):
        """:returns: number of channels, including data and alpha
        
        Compatible with multiband images.
        """
        count = 0
        for nm in DTBitmap2D.CHANNEL_NAMES:
            if getattr(self, nm) is not None:
                count += 1
        return count
        
    def has_alpha(self):
        """:returns boolean: ``True`` if the image has an alpha channel
        
        Only valid for grayscale or RGB image models, not arbitrary
        multiband images.
        """
        nchan = self.channel_count()
        return nchan == 2 or nchan == 4
        
    def is_gray(self):
        """:returns boolean: ``True`` if the image is grayscale (not RBG or RBGA)
        
        Only valid for grayscale or RGB image models, not arbitrary
        multiband images.
        """
        return self.channel_count() < 3
        
    def synthesize_alpha(self):
        """Adds or overwrites an alpha channel corresponding to all zero-valued RGB pixels.
        This is not very smart, as it doesn't check for neighboring pixels; you can end up
        turning actual black pixels transparent.
        """
        
        # more generally, should probably be dtype.min values
        image_dtype = self.dtype()
        alpha = np.zeros(self.red.shape, dtype=image_dtype)
        data_flag = np.iinfo(image_dtype).max
        
        # sum all channels; it'll overflow, but we only care about pixels that
        # are zero (ignoring possible wraparound to zero in summation)
        alpha += self.red
        alpha += self.green
        alpha += self.blue
        
        # make sure to set the data type, or DataTank will squawk
        self.alpha = np.where(alpha == 0, 0, data_flag).astype(image_dtype)
        
    def equalize_histogram(self):
        """Alters the image by equalizing the histogram among any non-alpha bands.
        """      
        
        try:
            from skimage import exposure, img_as_uint, img_as_ubyte
        except Exception as e:
            sys.stderr.write("You need to install scikit-image with `sudo pip install scikit-image`")
            return None
            
        im_type = self.dtype()
        max_value = np.finfo(im_type).max if im_type in (np.float32, np.float64, np.float) else np.iinfo(im_type).max
        min_value = np.finfo(im_type).min if im_type in (np.float32, np.float64, np.float) else np.iinfo(im_type).min
        scale = (min_value, max_value)
        
        # This is a bit hacky; we do allow floating point images, mainly for
        # conversion to DTMesh2D, but DataTank does not. Treat them as pass-through
        # even though it's weird to call this on a float image. For int8 and int16,
        # convert to unsigned, since scikit-image does weird shit with signed types,
        # and __dt_write__ now converts unsigned to signed when saving.
        def __convert_type(array):
            if im_type in (np.int16, np.uint16):
                return img_as_uint(array)
            elif im_type in (np.int8, np.uint8):
                return img_as_ubyte(array)
            else:
                return array
                
        for channel_name in DTBitmap2D.CHANNEL_NAMES:
            # don't muck with the alpha channel
            if channel_name == "alpha":
                continue
            values = getattr(self, channel_name)
            if values is not None:
                values = exposure.rescale_intensity(__convert_type(exposure.equalize_hist(values)), out_range=(scale))
                setattr(self, channel_name, values)
        
    def pil_image(self):
        """Attempt to convert a raw image to a :mod:`PIL` Image object.
        
        :returns: a :mod:`PIL` Image, or ``None`` if :mod:`PIL` can't be loaded or if the conversion failed.
        
        **Requires PIL**
        
        This allows you to run PIL image filters and operations. 
        *Only tested with 8-bit images, but gray/gray+alpha and RGB/RGBA
        have all been tested.*
        
        """
        
        try:
            from PIL import Image
        except Exception as e:
            return None
            
        if self.is_gray():
            mode = "L"
            raw_mode = mode
            channels = [self.gray]
            if self.has_alpha():
                mode = "LA"
                raw_mode = "LA;L"
                channels.append(self.alpha)
        else:
            mode = "RGB"
            raw_mode = mode
            channels = [self.red, self.green, self.blue]
            if self.has_alpha():
                mode = "RGBA"
                raw_mode += "A"
                channels.append(self.alpha)
            raw_mode += ";L"
        
        size = np.flipud(channels[0].shape)
        data = np.hstack(channels).tostring()
        return Image.fromstring(mode, size, data, "raw", raw_mode, 0, -1)
        
    def mesh_from_channel(self, channel="gray", alpha_as_mask=False):
        """Extract a given bitmap plane as a DTMesh2D object.
        
        :param channel: may be one of (`red`, `green`, `blue`, `gray`, `alpha`)
        
        :returns: a :class:`datatank_py.DTMesh2D.DTMesh2D` instance
        
        **Requires GDAL**
        
        This is how you would extract raw pixels and georegistration data from
        e.g., a 32-bit GeoTIFF or other image supported by GDAL, and bring it
        in to DataTank. This is particularly useful for elevation data.
        
        The returned mesh will use the spatial grid (origin and pixel size) of the image.
        Note that the image's ``nodata`` attribute will be used to create
        an appropriate :class:`datatank_py.DTMask.DTMask` which will be applied
        to the mesh. The nodata value is obtained from GDAL.

        >>> from datatank_py.DTBitmap2D import DTBitmap2D
        >>> img = DTBitmap2D("int16.tiff")
        >>> img.mesh_from_channel()
        <datatank_py.DTMesh2D.DTMesh2D object at 0x101a7a1d0>
        >>> img = DTBitmap2D("rgb_geo.tiff")
        >>> img.mesh_from_channel(channel="red")
        <datatank_py.DTMesh2D.DTMesh2D object at 0x10049ab90>
        
        **The returned mesh will contain values in floating point**
                
        """
        
        from datatank_py.DTMesh2D import DTMesh2D
        from datatank_py.DTMask import DTMask
        values = getattr(self, channel)
        mask = None
        if alpha_as_mask:
            assert self.nodata is None, "Attempting to use alpha as mask but image has NODATA values"
            assert self.alpha is not None, "Image does not have an alpha channel"
            mask_array = self.alpha.astype(np.int8) 
            #np.zeros(values.shape, dtype=np.int8)
            #mask_array[np.where(self.alpha != 0)] = 1
            mask = DTMask(mask_array)
        elif self.nodata is not None:
            mask_array = np.zeros(values.shape, dtype=np.int8)
            mask_array[np.where(values != self.nodata)] = 1
            mask = DTMask(mask_array)
        return DTMesh2D(values, grid=self.grid, mask=mask)
        
    def raster_size(self):
        """:returns: size in pixels, 2-tuple ordered as `(horizontal, vertical)`."""
        for nm in DTBitmap2D.CHANNEL_NAMES:
            values = getattr(self, nm)
            if values is not None:
                return tuple(reversed(values.shape))
        assert False, "No valid channels to compute raster size"
        
    def write_geotiff(self, output_path, projection_name=None):
        """Save a DTBitmap2D as a GeoTIFF file.
        
        :param output_path: a file path; all parent directories must exist
        :param projection_name: the spatial reference system to associate with the image
        
        **Requires GDAL**

        The spatial reference must be a string recognized by GDAL.
        For example, `EPSG:4326` and `WGS84` are both
        valid. See the documentation for OSRSpatialReference::SetFromUserInput
        at `<http://www.gdal.org/ogr/classOGRSpatialReference.html>`_
        for more specific details.
        
        Note that exceptions will be raised if the :class:`DTBitmap2D` is not valid
        (has no data), or if any GDAL functions fail.  This method has only
        been tested with 8-bit images, but gray/rgb/alpha images work as
        expected.
        
        """
        
        from osgeo import gdal, osr
        from osgeo.gdalconst import GDT_UInt16, GDT_Byte
        
        # throw instead of printing to stderr
        gdal.UseExceptions()
        osr.UseExceptions()
                
        # gdal doesn't like unicode objects...
        output_path = output_path.encode(sys.getfilesystemencoding())
        
        # default to whatever the internal projection is, in case this
        # was originally loaded with GDAL
        if projection_name is None:
            projection_name = self.projection
        elif self.projection is not None:
            assert self.projection == projection_name, "attempt to assign a different projection to this image"
            
        projection_name = projection_name.encode("utf-8")
        
        band_count = self.channel_count()
        assert band_count > 0, "No channels to save"

        (raster_x, raster_y) = self.raster_size()

        # base spatial transform
        grid = self.grid
        (xmin, dx, rot1, ymax, rot2, dy) = (0, 0, 0, 0, 0, 0)
        xmin = grid[0]
        dx = grid[2]
        dy = grid[3]
        ymax = grid[1] + abs(dy) * raster_y

        geotiff = gdal.GetDriverByName("GTiff")
        
        # only support 8 or 16 bit unsigned images; make the caller scale
        assert self.dtype() in (np.uint8, np.uint16), "Unhandled bit depth %s" % (self.dtype())
        etype = GDT_Byte if self.dtype() == np.uint8 else GDT_UInt16
        
        dst = geotiff.Create(output_path, raster_x, raster_y, bands=band_count, eType=etype)
        assert dst, "Unable to create destination dataset at %s" % (output_path)

        # Recall that dx and dy are signed, with positive upwards;
        # this is bizarre, but http://www.gdal.org/gdal_tutorial.html
        # shows it also.
        dst.SetGeoTransform((xmin, dx, rot1, ymax, rot2, -abs(dy)))
        dst_srs = osr.SpatialReference()
        
        # This accepts a variety of inputs, notably EPSG and PROJ.4,
        # as well as NAD27, NAD83, WGS84, WGS72.
        dst_srs.SetFromUserInput(projection_name)
        dst.SetProjection(dst_srs.ExportToWkt())
            
        band_index = 1
        for band_name in DTBitmap2D.CHANNEL_NAMES:
            
            values = getattr(self, band_name)
            
            if values is not None:
                
                band = dst.GetRasterBand(band_index)
                band_index += 1
                    
                values = np.flipud(values)
                # reverse transforms applied in DTDataFile
                shape = list(values.shape)
                shape.reverse()
                data = values.reshape(shape, order="C").tostring()
            
                band.WriteRaster(0, 0, dst.RasterXSize, dst.RasterYSize, data, buf_xsize=dst.RasterXSize, buf_ysize=dst.RasterYSize, buf_type=band.DataType)
        
        dst = None
        
    def __dt_type__(self):
            return DTBitmap2D.dt_type[0]

    def __dt_write__(self, datafile, name):
        
        suffix = "16" if self.dtype() in (np.uint16, np.int16) else ""
        assert self.dtype() not in (np.float64, np.float32), "DataTank does not support floating-point images"            
        
        for channel_name in DTBitmap2D.CHANNEL_NAMES:
            values = getattr(self, channel_name)
            if values is not None:
                # DataTank only supports signed images, so we need to preserve scaling
                # and avoid truncation if we have unsigned 8 or 16 data.
                if self.dtype() == np.uint16:
                    values = values.view(np.int16)
                    values -= 2**16
                elif self.dtype() == np.uint8:
                    values = values.view(np.int8)
                    values -= 2**8               
                channel_name = channel_name.capitalize() + suffix
                datafile.write_anonymous(values, "_".join((name, channel_name)))
            
        datafile.write_anonymous(self.grid, name)
        
    @classmethod
    def from_data_file(self, datafile, name):
        """Create a new instance from a DTDataFile by name.
        
        :param datafile: an open DTDataFile instance
        :param name: the name of the DTBitmap2D object in the file (including any time index)
        
        :returns: a new DTBitmap2D instance
        
        """
        from DTStructuredGrid2D import _squeeze2d
        
        bitmap = DTBitmap2D()
        bitmap.grid = np.squeeze(datafile[name])
        for suffix in ("", "16"):
            for channel_name in DTBitmap2D.CHANNEL_NAMES:
                dt_channel_name = "%s_%s%s" % (name, channel_name.capitalize(), suffix)
                values = datafile[dt_channel_name]
                if values is not None:
                    # need our squeeze hack to get rid of the leading singleton dimension
                    setattr(bitmap, channel_name, _squeeze2d(values))
        return bitmap

class _DTGDALBitmap2D(DTBitmap2D):
    """Private subclass that wraps up the GDAL logic."""
    def __init__(self, image_path, rgba_bands=None):
        
        super(_DTGDALBitmap2D, self).__init__()
        
        from osgeo import gdal
        from osgeo.gdalconst import GA_ReadOnly
                
        # throw instead of printing to stderr
        gdal.UseExceptions()
        
        from datatank_py.DTProgress import DTProgress

        # NB: GDAL craps out if you pass a unicode object as a path
        image_path = image_path.encode(sys.getfilesystemencoding())
            
        dataset = gdal.Open(image_path, GA_ReadOnly)
        (xmin, dx, rot1, ymax, rot2, dy) = dataset.GetGeoTransform()
        self.projection = dataset.GetProjectionRef()
        
        bands = []
        self.nodata = None
        if rgba_bands is None or len(rgba_bands) == 0:
            rgba_bands = range(1, dataset.RasterCount + 1)
        else:
            rgba_bands = [int(x) for x in rgba_bands]
            # should truncate here? how to handle default for a module?
            
        channel_count = len(rgba_bands)
        
        assert channel_count <= dataset.RasterCount, "Requested %d raster bands from an image that has %d bands" % (channel_count, dataset.RasterCount)
            
        for band_index in rgba_bands:
            try:
                band = dataset.GetRasterBand(band_index)
                sys.stderr.write("Read band %d (image has %d bands)\n" % (band_index, dataset.RasterCount))
            except Exception as e:
                sys.stderr.write("Failed reading band %d (image has %d bands)\n" % (band_index, dataset.RasterCount))
                sys.stderr.write("%s\n" % (e))
                raise e
            if self.nodata == None:
                self.nodata = band.GetNoDataValue()
            if band == None:
                break
            bands.append(band)
            
        ymin = ymax + dy * dataset.RasterYSize
        self.grid = (xmin, ymin, dx, abs(dy))
                
        # Gray + Alpha, RGB, or RGBA
        if channel_count in (2, 3, 4):

            # zero-based
            name_map = {}
            
            if channel_count == 2:
                # Gray + Alpha
                name_map = {0:"gray", 1:"alpha"}

            elif channel_count == 3:
                # RGB (tested with screenshot)
                name_map = {0:"red", 1:"green", 2:"blue"}

            elif channel_count == 4:
                # RGBA
                name_map = {0:"red", 1:"green", 2:"blue", 3:"alpha"}

            for idx in name_map:
                band = bands[idx]
                channel = band.ReadAsArray()
                channel = np.flipud(channel)
                sys.stderr.write("Interpreted band %d as %s\n" % (idx + 1, name_map[idx]))
                sys.stderr.write("min = %s, max = %s, mean = %s\n" % (np.min(channel), np.max(channel), np.mean(channel)))
                setattr(self, name_map[idx], channel)
                
        elif channel_count == 1:
            
            # we only have one band anyway on this path, so see if we have an indexed image,
            band = bands[0]
            mesh = band.ReadAsArray()

            mesh = np.flipud(mesh)
            ctab = band.GetRasterColorTable()
            
            if ctab is not None:
                                
                sys.stderr.write("Interpreted image as indexed RGB\n")

                # indexed images have to be expanded to RGB, and this is pretty slow
                progress = DTProgress()
                
                red = np.zeros(mesh.size, dtype=np.uint8)
                green = np.zeros(mesh.size, dtype=np.uint8)
                blue = np.zeros(mesh.size, dtype=np.uint8)
                
                # hash lookup is faster than array lookup by index and
                # faster than calling GetColorEntry for each pixel
                cmap = {}
                for color_index in xrange(min(256, ctab.GetCount())):
                    cmap[int(color_index)] = [np.uint8(x) for x in ctab.GetColorEntry(int(color_index))]
                
                for raster_index, color_index in enumerate(mesh.flatten()):
                    try:
                        (red[raster_index], green[raster_index], blue[raster_index], ignored) = cmap[int(color_index)]
                    except Exception as e:
                        # if not in table, leave as zero
                        pass
                    progress.update_percentage(raster_index / float(mesh.size))

                self.red = np.reshape(red, mesh.shape)
                self.green = np.reshape(green, mesh.shape)
                self.blue = np.reshape(blue, mesh.shape)

                    
            else:
                # Gray (tested with int16)
                self.gray = mesh
                sys.stderr.write("Interpreted image as single-channel grayscale\n")
                
        else:
            sys.stderr.write("Unable to decode an image with %d raster bands\n" % (channel_count))

        del dataset

def _array_from_image(image):
    """Convert a PIL image to a numpy ndarray.
    
    Arguments:
    image -- a PIL image instance
    
    Returns:
    a numpy ndarray or None if an error occurred
    
    """
    
    array = None
    if image.mode.startswith(("I", "F")):
        
        def _parse_mode(mode):
            # Modes aren't very well documented, and I see results that
            # differ from the documentation.  They seem to follow this:
            # http://www.pythonware.com/library/pil/handbook/decoder.htm
            suffix = mode.split(";")[-1]
            np_type = ""
            if suffix != mode:
                mode_size = ""
                mode_fmt = ""
                for c in suffix:
                    if c.isdigit():
                        mode_size += c
                    else:
                        mode_fmt += c
                if mode_fmt.startswith("N") is False:
                    # big-endian if starts with B, little otherwise
                    np_type += ">" if mode_fmt.startswith("B") else "<"
                if mode_fmt.endswith("S"):
                    # signed int
                    np_type += "i"
                else:
                    # float or unsigned int
                    np_type += "f" if mode.endswith("F") else "u"
                # convert to size in bytes
                np_type += str(int(mode_size) / 8)
            elif mode == "F":
                np_type = "f4"
            elif mode == "I":
                np_type = "i4"
            else:
                return None
            return np.dtype(np_type)
        
        dt = _parse_mode(image.mode)
        if dt is None:
            sys.stderr.write("Warning: DTBitmap2D.py unable to determine image bit depth and byte order for mode \"%s\"\n" % (image.mode))
        else:
            try:
                # fails for signed int16 images produced by GDAL, but works with unsigned
                array = np.fromstring(image.tostring(), dtype=dt)
                array = array.reshape((image.size[1], image.size[0]))
            except Exception as e:
                sys.stderr.write("Warning: DTBitmap2D.py image.tostring() failed for image with mode \"%s\" (PIL error: %s)\n" % (image.mode, str(e)))
        
    else:    
        # doesn't seem to work reliably for GDAL-produced 16 bit GeoTIFF
        array = np.asarray(image)
    
    return array
        
class _DTPILBitmap2D(DTBitmap2D):
    """Private subclass that wraps up the PIL logic."""
    def __init__(self, image_or_path, rgba_bands=None):
        
        super(_DTPILBitmap2D, self).__init__()
        
        from PIL import Image
        image = Image.open(image_or_path) if _is_string(image_or_path) else image_or_path
        
        if rgba_bands is not None:
            sys.stderr.write("WARNING: ignoring rgba_bands = %s for PIL image\n" % (rgba_bands))
        
        array = _array_from_image(image)
        assert array is not None, "unable to convert the image to a numpy array"
        assert array.dtype in (np.int16, np.uint16, np.uint8, np.int8, np.bool), "unsupported bit depth"
                
        if image.mode in ("1", "P", "L", "LA") or image.mode.startswith(("F", "I")):

            # Convert binary image of dtype=bool to uint8, although this is probably
            # a better candidate for a or use as a mask.
            if image.mode == "1":
                sys.stderr.write("Warning: DTBitmap2D.py converting binary image to uint8\n")
                # TODO: this crashes when I test it with a binary TIFF, but it looks like a
                # bug in numpy or PIL.  Strangely, it doesn't crash if I copy immediately after
                # calling asarray above.
                array = array.copy().astype(np.uint8)
                array *= 255

            if image.mode in ("1", "L", "P") or image.mode.startswith(("F", "I")):
                self.gray = np.flipud(array)
            else:
                assert image.mode == "LA", "requires gray + alpha image"
                self.gray = np.flipud(array[:,0])
                self.alpha = np.flipud(array[:,1])

        elif image.mode in ("RGB", "RGBA"):

            self.red = np.flipud(array[:,:,0])
            self.green = np.flipud(array[:,:,1])
            self.blue = np.flipud(array[:,:,2])
            if image.mode == "RGBA":
                self.alpha = np.flipud(array[:,:,3])
        
        del image

