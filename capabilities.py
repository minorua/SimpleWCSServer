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

from xmldocument import MyXMLDocument
import settings

def capabilities(params=None):
  if params is None:
    params = {}
  doc = MyXMLDocument()
  E = doc.append
  ET = doc.appendTree

  root = E(None, "WCS_Capabilities", {"version": "1.0.0",
                                      "xmlns": "http://www.opengis.net/wcs",
                                      "xmlns:xlink": "http://www.w3.org/1999/xlink",
                                      "xmlns:gml": "http://www.opengis.net/gml"})
  service = E(root, "Service")
  ET(service, settings.service)

  capability = E(root, "Capability")
  request = E(capability, "Request")
  rs = [E(request, "GetCapabilities"), E(request, "DescribeCoverage"), E(request, "GetCoverage")]
  for r in rs:
    e = E(E(E(r, "DCPType"), "HTTP"), "Get")
    e = E(e, "OnlineResource", {"xlink:type": "simple", "xlink:href": "http://{0}/wcs.py?".format(settings.host)})
    #TODO: Post

  contentmeta = E(root, "ContentMetadata")
  for coverage in settings.coverages:
    brief = E(contentmeta, "CoverageOfferingBrief")
    E(brief, "name", text=coverage.identifier)
    E(brief, "label", text=coverage.label)
    E(brief, "description", text=coverage.description)

    e = E(brief, "lonLatEnvelope", {"srsName": "urn:ogc:def:crs:EPSG::4326"})
    env = coverage.lonLatEnvelope
    E(e, "gml:pos", text="{0} {1}".format(env.xmin, env.ymin))
    E(e, "gml:pos", text="{0} {1}".format(env.xmax, env.ymax))

  return doc

if __name__ == "__main__":
  print capabilities().document().toprettyxml("  ", "\n", "utf-8")
