#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding:utf-8
# http://en.wikipedia.org/wiki/Representational_state_transfer

import os
import sys

import tornado.ioloop
import tornado.httpserver

from tornado.web import RequestHandler
from tornado.web import HTTPError

from sslapi import getrandom, gencert, certext

import json, re, base64

def isempty(string):
  if string == '' or string == None:
    return True
  return False

class Main(RequestHandler):
  def get(self):
    self.render('index.html')

  def post(self, rid = None):

    action = self.get_argument('action', None)
    values = self.get_argument('values', None)
    if isempty(action):
      print 'post: warning: empty action'
      raise HTTPError(500)

    print action, values

    result = None
    if action == "getrandom":
      try:
        values = json.loads(values)
        keylen = values.get('keylen')
        try:
          keylen = int(keylen)
        except:
          keylen = None
      except:
        keylen = None
      if keylen > 1000 or keylen < 1:
        keylen = None
      if keylen:
        result = base64.b64encode(getrandom(keylen))
      else:
        result = base64.b64encode(getrandom())

    elif action == "gencert":
      try:
        values = json.loads(values)
        keylen = values.get('certkeylen')
        try:
          keylen = int(keylen)
        except:
          keylen = None
      except:
        print 'Failed to parse json data'
        raise HTTPError(500)

      countryName            = values.get('countryName')
      stateOrProvinceName    = values.get('stateOrProvinceName')
      localityName           = values.get('localityName')
      organizationName       = values.get('organizationName')
      organizationUnitName   = values.get('organizationUnitName')
      commonName             = values.get('commonName')
      emailAddress           = values.get('emailAddress')

      datalist = [ countryName, stateOrProvinceName, localityName,
                   organizationName, organizationUnitName, commonName, emailAddress]
      if None in datalist or '' in datalist:
        print 'Missing data:', datalist
        raise HTTPError(500)

      result = gencert(keylen, countryName, stateOrProvinceName, localityName,
                       organizationName, organizationUnitName, commonName, emailAddress)

    elif action == "certext":
      try:
        values = json.loads(values)
        text   = values.get('text')
      except:
        print 'Failed to parse json data'
        raise HTTPError(500)
      try:
        result = certext(text)
      except:
        print 'Failed to certext'
        raise HTTPError(500)

    else:
      print 'Unknown action:', action
      raise HTTPError(500)

    if not result:
      print 'Warning: No result'

    self.write({'data': result})

routes = [
  (r'/', Main),
]

settings = {
  'debug': True,
  'static_path': './pub/media',
  'static_url_prefix': '/media/',
  'template_path': './tpl'
}

if __name__=='__main__':
  app = tornado.web.Application(routes, **settings)
  http_server = tornado.httpserver.HTTPServer(app)
  http_server.listen(8000)
  print 'http://localhost:' + str(8000)
  tornado.ioloop.IOLoop.instance().start()
