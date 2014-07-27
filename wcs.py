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

import cgi
from datetime import datetime
from wsgiref import simple_server

import settings

def access_log(environ):
  if not settings.accessLogPath:
    return
  with open(settings.accessLogPath, "a") as f:
    now = datetime.now()
    remote_addr = environ.get("REMOTE_ADDR", "-")
    request_method = environ.get("REQUEST_METHOD", "?")
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S.") + "%04d" % (now.microsecond // 1000)
    user_agent = environ.get("HTTP_USER_AGENT", "?")
    url = "http://" + settings.host + environ.get("PATH_INFO", " ") + "?" + environ.get("QUERY_STRING", " ")
    f.write('%s [%s] %s "%s %s"\n' % (remote_addr, timestamp, user_agent, request_method, url))
    #f.write(",".join([remote_addr, timestamp, user_agent, request_method, url]) + "\n")

def error_response(start_response, status, content=""):
  start_response(status, [("Content-Type", "text/plain")])
  return [content if content else status]

def application(environ, start_response):
  #if environ.get("PATH_INFO") != "/wcs.py":
  #  return error_response(start_response, "404 Not Found")

  method = environ.get("REQUEST_METHOD")
  if method != "GET":     #TODO: POST support
    return error_response(start_response, "400 Bad Request")

  # parse query
  params = {}
  for kv in cgi.parse_qsl(environ.get("QUERY_STRING")):
    params[kv[0].upper()] = kv[1]

  # access log
  access_log(environ)

  request = params.get("REQUEST")
  if request == "GetCoverage":
    from coverage import coverage
    data = coverage(params)
    if data:
      start_response("200 OK", [("Content-Type", "image/tiff")])
      return [data]
    return error_response(start_response, "400 Bad Request")    #TODO: status code

  xmldoc = None
  if request == "GetCapabilities":
    from capabilities import capabilities
    xmldoc = capabilities(params)
  elif request == "DescribeCoverage":
    from coverageDescription import coverageDescription
    xmldoc = coverageDescription(params)
  else:
    return error_response(start_response, "400 Bad Request", "REQUEST parameter is missing or wrong")

  start_response("200 OK", [("Content-Type", "text/xml")])
  return [xmldoc.document().toprettyxml("  ", "\n", "utf-8")]

if __name__=="__main__":
  server = simple_server.make_server("", settings.port, application)
  print "Serving HTTP on port {0}...".format(settings.port)
  server.serve_forever()
