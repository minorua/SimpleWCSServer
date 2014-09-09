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
import urllib2

from osgeo import gdal
from osgeo import osr

import settings

TILE_SIZE = 256
TSIZE1 = 20037508.342789244
NODATA_VALUE = 0
ZMAX = 14

class GSIElevTileProvider:

  def __init__(self):
    self.cacheRoot = settings.cacheRoot
    if self.cacheRoot:
      self.cacheRoot = os.path.join(os.path.dirname(__file__), self.cacheRoot, "gsitile")
    self.fetchLogPath = settings.fetchLogPath
    self.userAgent = settings.userAgent

    self.wgs84 = osr.SpatialReference()
    self.wgs84.ImportFromEPSG(4326)
    self.crs = osr.SpatialReference()
    self.crs.ImportFromEPSG(3857)
    self.toWgs84 = osr.CoordinateTransformation(self.crs, self.wgs84)

  def getDataset(self, width, height, bbox):
    """ #TODO: rename. return a source dataset (GDAL MEM Driver) """
    xmin, ymin, xmax, ymax = bbox

    # calculate zoom level
    mpp1 = TSIZE1 / TILE_SIZE
    mapUnitsPerPixel = (xmax - xmin) / width
    zoom = int(math.ceil(math.log(mpp1 / mapUnitsPerPixel, 2) + 1))
    zoom = max(0, min(zoom, ZMAX))

    # calculate tile range (yOrigin is top)
    size = TSIZE1 / 2 ** (zoom - 1)
    matrixSize = 2 ** zoom
    ulx = max(0, int((xmin + TSIZE1) / size))
    uly = max(0, int((TSIZE1 - ymax) / size))
    lrx = min(int((xmax + TSIZE1) / size), matrixSize - 1)
    lry = min(int((TSIZE1 - ymin) / size), matrixSize - 1)

    cols = lrx - ulx + 1
    rows = lry - uly + 1

    # download count limit
    count = cols * rows
    if count > 64:
      return None   #TODO: Error message

    tiles = self.fetchFiles("http://cyberjapandata.gsi.go.jp/xyz/dem/{z}/{x}/{y}.txt", zoom, ulx, uly, lrx, lry)
    #tiles = self.fetchFiles("http://localhost/xyz/dem/{z}/{x}/{y}.txt", zoom, ulx, uly, lrx, lry)

    if self.fetchLogPath:
      with open(self.fetchLogPath, "a") as f:
        f.write("tile count: " + str(len(tiles)) + "\n")

    width = cols * TILE_SIZE
    height = rows * TILE_SIZE
    res = size / TILE_SIZE
    geotransform = [ulx * size - TSIZE1, res, 0, TSIZE1 - uly * size, 0, -res]

    mem_driver = gdal.GetDriverByName("MEM")
    ds = mem_driver.Create("", width, height, 1, gdal.GDT_Float32, [])

    #mem_driver = gdal.GetDriverByName("GTiff")
    #ds = mem_driver.Create(r"D:\debug.tif", width, height, 1, gdal.GDT_Float32, [])

    # WKT: http://epsg.io/3857
    ds.SetProjection('PROJCS["WGS 84 / Pseudo-Mercator",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Mercator_1SP"],PARAMETER["central_meridian",0],PARAMETER["scale_factor",1],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["X",EAST],AXIS["Y",NORTH],EXTENSION["PROJ4","+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs"],AUTHORITY["EPSG","3857"]]')
    ds.SetGeoTransform(geotransform)

    band = ds.GetRasterBand(1)
    for i, tile in enumerate(tiles):
      if tile:
        col = i % cols
        row = i / cols
        band.WriteRaster(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE, tile)

    ds.FlushCache()
    return ds

  def fetchFiles(self, urltmpl, zoom, xmin, ymin, xmax, ymax):
    if self.fetchLogPath:
      with open(self.fetchLogPath, "a") as f:
        f.write(", ".join(map(str, [urltmpl, zoom, xmin, ymin, xmax, ymax])) + "\n")
        f.write(os.path.join(self.cacheRoot, str(zoom)) + "\n")

    ext = ""
    tileSize = TSIZE1 / 2 ** (zoom - 1)
    bbox = settings.bbox_gsitile
    fetchedFiles = []
    for y in range(ymin, ymax + 1):
      for x in range(xmin, xmax + 1):
        # check the center of tile is in bbox (TODO: check the tile intersects bbox)
        cx, cy, cz = self.toWgs84.TransformPoint((x + 0.5) * tileSize - TSIZE1, TSIZE1 - (y + 0.5) * tileSize)
        if cx < bbox.xmin or bbox.xmax < cx or cy < bbox.ymin or bbox.ymax < cy:
          fetchedFiles.append("")
          if self.fetchLogPath:
            with open(self.fetchLogPath, "a") as f:
              f.write("Out of bounding box: {0}, {1}\n".format(cx, cy))
          continue

        # check cache
        if self.cacheRoot:
          cacheDir = os.path.join(self.cacheRoot, str(zoom), str(x))
          cachePath = os.path.join(cacheDir, str(y) + ext)
          if os.path.exists(cachePath):
            with open(cachePath, "rb") as f:
              data = f.read()
            if data:
              fetchedFiles.append(data)
            else:
              array = np.empty(TILE_SIZE * TILE_SIZE, dtype=np.float32)
              array.fill(NODATA_VALUE)
              fetchedFiles.append(array.tostring())
            continue

        # make url
        url = urltmpl.replace("{x}", str(x)).replace("{y}", str(y)).replace("{z}", str(zoom))
        if self.fetchLogPath:
          with open(self.fetchLogPath, "a") as f:
            f.write(url + "\n")

        # download
        try:
          request = urllib2.Request(url)
          request.add_header("User-agent", self.userAgent)
          response = urllib2.urlopen(request)
          data = response.read()
        except:
          data = ""

        if data:
          data = np.fromstring(data.replace("e", str(NODATA_VALUE)).replace("\n", ","), dtype=np.float32, sep=",").tostring()   # to byte array
          fetchedFiles.append(data)
        else:
          array = np.empty(TILE_SIZE * TILE_SIZE, dtype=np.float32)
          array.fill(NODATA_VALUE)
          fetchedFiles.append(array.tostring())

        # cache
        if self.cacheRoot:
          if not os.path.exists(cacheDir):
            os.makedirs(cacheDir)
          with open(cachePath, "wb") as f:
            f.write(data)

    return fetchedFiles
