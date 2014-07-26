#!/usr/bin/env python
# -*- coding: utf-8 -*-

from coverageDefinition import BoundingBox, WCSCoverage

# ================================
#            Settings
# ================================

# Simple server
port = 8000
accessLogPath = ""            # path to access log file (empty string means access is not logged)

# WCS service
service = {"name": "SimpleWCSServer",
           "label": "Simple WCS Server",
           "fees": "NONE",
           "accessConstraints": "NONE"}

# GSI Elevation Tile coverage
cacheRoot = "./cache"   # cache directory (empty string means any fetched data is not cached)
fetchLogPath = ""       # path to fetch log file

# Coverage definitions
coverages = []
bbox_srtm_cj = BoundingBox(135.2389, 33.8063, 140.1823, 37.1918)
coverages.append(WCSCoverage("SRTM", "examples/srtm_cj.tif", 4326, bbox_srtm_cj, label="resampled small srtm3 data"))
coverages.append(WCSCoverage("SRTMSHADE", "examples/srtm_cj.tif", 4326, bbox_srtm_cj, label="resampled small srtm3 data", shade=True))

# http://portal.cyberjapan.jp/help/development/demtile.html
bbox_gsitile = BoundingBox(122.78, 20.4, 154.78, 45.58)
coverages.append(WCSCoverage("GSIDEM", "GSITILE", 3857, bbox_gsitile, label="GSI Elevation Tile"))
coverages.append(WCSCoverage("GSISHADE", "GSITILE", 3857, bbox_gsitile, label="GSI Elevation Tile", shade=True))

# add your own coverage definition here
