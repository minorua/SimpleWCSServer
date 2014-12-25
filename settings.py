#!/usr/bin/env python
# -*- coding: utf-8 -*-

from coverageDefinition import BoundingBox, WCSCoverage

# ================================
#            Settings
# ================================

# Simple server
hostname = "localhost"
port = 8000
host = hostname if port == 80 else "{0}:{1}".format(hostname, port)

accessLogPath = ""            # path to access log file (empty string means access is not logged)

# WCS service
service = {"name": "SimpleWCSServer",
           "label": "Simple WCS Server",
           "fees": "NONE",
           "accessConstraints": "NONE"}

# GSI Elevation Tile coverage
userAgent = "SimpleWCSServer/beta"
cacheRoot = "./cache"   # cache directory (empty string means any fetched data is not cached)
fetchLogPath = ""       # path to fetch log file

# Coverage definitions
coverages = []
bbox_srtm_cj = BoundingBox(135.2389, 33.8063, 140.1823, 37.1918)
coverages.append(WCSCoverage("SRTM", "data/srtm_cj.tif", 4326, bbox_srtm_cj, label="SRTM DEM", description="Sample data. Central Japan of decreased-resolution SRTM3 data."))
coverages.append(WCSCoverage("SRTMSHADE", "data/srtm_cj.tif", 4326, bbox_srtm_cj, label="SRTM DEM Hillshade", description="Sample data. Central Japan of decreased-resolution SRTM3 data.", shade=True))

# http://portal.cyberjapan.jp/help/development/demtile.html
bbox_gsitile = BoundingBox(122.78, 20.4, 154.78, 45.58)
coverages.append(WCSCoverage("GSIDEM", "GSITILE", 3857, bbox_gsitile, label="GSI Elevation Tile", description=u"国土地理院の標高タイルを貼り合わせたDEMです"))
coverages.append(WCSCoverage("GSISHADE", "GSITILE", 3857, bbox_gsitile, label="GSI Elevation Tile Hillshade", description=u"国土地理院の標高タイルから作成された陰影図です", shade=True))

# add your own coverage definition here
