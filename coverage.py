#!/usr/bin/env python
# -*- coding: utf-8 -*-
# project   : Simple WCS Server
# begin     : 2014-07-26
# copyright : (C) 2014 Minoru Akagi
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import math
import numpy as np
import os

from osgeo import gdal
from osgeo import osr

import settings

memFileIndex = 0
def tempMemFilePath():
  global memFileIndex
  path = "/vsimem/wcs_tmp{0}.tif".format(memFileIndex)
  memFileIndex += 1
  return path

def coverage(params=None):
  if params is None:
    params = {}

  buffer_max_size = 64 * 1024 * 1024  # max data size
  format = "GTiff"
  driver = gdal.GetDriverByName(format)

  bbox = params.get("BBOX", "0,0,0,0")
  bbox = map(float, bbox.split(","))
  xmin, ymin, xmax, ymax = bbox

  xsize = int(params.get("WIDTH", 1))
  ysize = int(params.get("HEIGHT", 1))
  #TODO: check validity

  # QGIS requests 32 x 32 image many times to get legend image.
  #if xsize == 32 and ysize == 32:
  #  with open(os.path.join(os.path.dirname(__file__), "32x32.tif"), "rb") as f:
  #    image = f.read()
  #  return image

  coverage = None
  identifier = params.get("COVERAGE")
  if identifier:
    for cv in settings.coverages:
      if cv.identifier == identifier:
        coverage = cv
        break
  if not coverage:
    return ""

  crs = osr.SpatialReference()
  crs_param = params.get("CRS", "")
  if crs_param.startswith("EPSG:"):
    crs.ImportFromEPSG(int(crs_param[5:]))
  else:
    crs.ImportFromEPSG(coverage.epsg_code)

  srs_ds = None
  if coverage.source == "GSITILE":
    from GSIElevTileProvider import GSIElevTileProvider
    src_ds = GSIElevTileProvider().getDataset(xsize, ysize, bbox)
  else:
    src_ds = gdal.Open(coverage.source, gdal.GA_ReadOnly)

  if src_ds is None:
    return ""

  # create a virtual file in memory
  filename = tempMemFilePath()
  dst_ds = driver.Create(filename, xsize, ysize, 1, gdal.GDT_Float32, [])
  if dst_ds is None:
    return ""

  geotransform = [xmin, (xmax - xmin) / xsize, 0, ymax, 0, (ymin - ymax) / ysize]
  dst_ds.SetProjection(crs.ExportToWkt())
  dst_ds.SetGeoTransform(geotransform)

  # reproject image
  if params.get("RESAMPLE", "").upper() == "NEAREST":
    gdal.ReprojectImage(src_ds, dst_ds, None, None, gdal.GRA_NearestNeighbour)
  else:
    gdal.ReprojectImage(src_ds, dst_ds, None, None, gdal.GRA_Bilinear)

  band = dst_ds.GetRasterBand(1)

  if coverage.shade:
    # hillshade
    # http://geoexamples.blogspot.com/2014/03/shaded-relief-images-using-gdal-python.html
    array = np.fromstring(band.ReadRaster(0, 0, xsize, ysize, xsize, ysize, gdal.GDT_Float32), dtype=np.float32, count=xsize * ysize)
    array = array.reshape((ysize, xsize))
    azimuth = 315
    angle_altitude = 45

    x, y = np.gradient(array)
    slope = math.pi / 2. - np.arctan(np.sqrt(x * x + y * y))
    aspect = np.arctan2(-x, y)
    azimuthrad = azimuth * math.pi / 180
    altituderad = angle_altitude * math.pi / 180

    shade = math.sin(altituderad) * np.sin(slope) + math.cos(altituderad) * np.cos(slope) * np.cos(azimuthrad - aspect)
    shade = np.uint8(255 * (shade + 1) / 2)

    gdal.Unlink(filename)
    dst_ds = driver.Create(filename, xsize, ysize, 1, gdal.GDT_Byte, [])
    dst_ds.SetProjection(crs.ExportToWkt())
    dst_ds.SetGeoTransform(geotransform)
    band = dst_ds.GetRasterBand(1)
    band.WriteRaster(0, 0, xsize, ysize, shade.tostring())
  else:
    nodata_value = -9999
    band.SetNoDataValue(nodata_value)

  # make sure that all data have been written
  dst_ds.FlushCache()

  # read the contents of the virtual file
  f = gdal.VSIFOpenL(filename, "rb")
  buffer = gdal.VSIFReadL(1, buffer_max_size, f)
  gdal.VSIFCloseL(f)

  # remove the memory file
  gdal.Unlink(filename)

  return buffer

if __name__ == "__main__":
  data = coverage()
  print len(data)

