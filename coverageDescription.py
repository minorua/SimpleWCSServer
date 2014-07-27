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

from osgeo import gdal
from osgeo import osr

from xmldocument import MyXMLDocument
import settings

def coverageDescription(params=None):
  if params is None:
    params = {}

  wgs84 = osr.SpatialReference()
  wgs84.ImportFromEPSG(4326)

  doc = MyXMLDocument()
  E = doc.append
  root = E(None, "CoverageDescription", {"xmlns": "http://www.opengis.net/wcs",
                                         "xmlns:gml": "http://www.opengis.net/gml"})
  coverages = []
  identifier = params.get("COVERAGE")
  if identifier:
    for coverage in settings.coverages:
      if coverage.identifier == identifier:
        coverages = [coverage]
        break
  else:
    coverages = settings.coverages

  for coverage in coverages:
    env = coverage.lonLatEnvelope
    crs = osr.SpatialReference()
    crs.ImportFromEPSG(coverage.epsg_code)
    trans = osr.CoordinateTransformation(wgs84, crs)

    offering = E(root, "CoverageOffering", {"version": "1.0.0"})
    E(offering, "name", text=coverage.identifier)
    E(offering, "label", text=coverage.label)

    e = E(offering, "lonLatEnvelope", {"srsName": "urn:ogc:def:crs:EPSG::4326"})
    E(e, "gml:pos", text="{0} {1}".format(env.xmin, env.ymin))
    E(e, "gml:pos", text="{0} {1}".format(env.xmax, env.ymax))

    e = E(offering, "domainSet")
    sDomain = E(e, "spatialDomain")

    e = E(sDomain, "gml:Envelope", {"srsName": "EPSG:" + str(coverage.epsg_code)})
    x, y, z = trans.TransformPoint(env.xmin, env.ymin)
    E(e, "gml:pos", text="{0} {1}".format(x, y))
    x, y, z = trans.TransformPoint(env.xmax, env.ymax)
    E(e, "gml:pos", text="{0} {1}".format(x, y))

    # gml:RectifiedGrid, which is required by GDAL WCS driver
    if coverage.source == "GSITILE":
      e = E(sDomain, "gml:RectifiedGrid", {"dimension": "2"})
      e1 = E(e, "gml:limits")
      e1 = E(e1, "gml:GridEnvelope")
      E(e1, "gml:low", text="0 0")
      E(e1, "gml:high", text="373248 355328")     # z:14, (13779, 5856) - (15236, 7243)
      E(e, "gml:axisName", text="x")
      E(e, "gml:axisName", text="y")
      e1 = E(e, "gml:origin")
      E(e1, "gml:pos", text="13665717.664936949 5713820.738373496") # NOTE: this is top-left
      E(e, "gml:offsetVector", text="9.554628535647032 0")
      E(e, "gml:offsetVector", text="0 -9.554628535647032")
    else:
      ds = gdal.Open(coverage.source, gdal.GA_ReadOnly)
      geotransform = ds.GetGeoTransform()

      e = E(sDomain, "gml:RectifiedGrid", {"dimension": "2"})
      e1 = E(e, "gml:limits")
      e1 = E(e1, "gml:GridEnvelope")
      E(e1, "gml:low", text="0 0")
      E(e1, "gml:high", text="{0} {1}".format(ds.RasterXSize - 1, ds.RasterYSize - 1))

      E(e, "gml:axisName", text="x")
      E(e, "gml:axisName", text="y")
      e1 = E(e, "gml:origin")

      # center of top-left corner pixel. Is this correct?
      E(e1, "gml:pos", text="{0} {1}".format(geotransform[0] + geotransform[1] / 2, geotransform[3] + geotransform[5] / 2))
      E(e, "gml:offsetVector", text="{0} 0".format(geotransform[1]))
      E(e, "gml:offsetVector", text="0 {0}".format(geotransform[5]))

    e = E(offering, "rangeSet")
    e = E(e, "RangeSet")
    E(e, "name", text="RangeSet1")
    E(e, "label", text="RangeSet1")

    e = E(offering, "supportedCRSs")
    E(e, "requestResponseCRSs", text="EPSG:" + str(coverage.epsg_code))

    e = E(offering, "supportedFormats")
    E(e, "formats", text="GeoTIFF")

    e = E(offering, "supportedInterpolations", {"default": "bilinear"})
    E(e, "interpolationMethod", text="nearest neighbor")
    E(e, "interpolationMethod", text="bilinear")

  return doc

if __name__ == "__main__":
  print coverageDescription().document().toprettyxml("  ", "\n", "utf-8")
