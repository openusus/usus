#!/usr/bin/env python3

import random
import string
import json

import cherrypy


@cherrypy.expose
class StringGeneratorWebService(object):

    @cherrypy.tools.accept(media='application/json')
    def GET(self):
        test = ['hallo', {'a': 1}]
        # return cherrypy.session['mystring']
        return bytes( json.JSONEncoder().encode(test), encoding='utf-8') # cherrypy.session['mystring']

    def POST(self, length=8):
        some_string = ''.join(random.sample(string.hexdigits, int(length)))
        cherrypy.session['mystring'] = some_string
        return some_string

    def PUT(self, another_string):
        cherrypy.session['mystring'] = another_string

    def DELETE(self):
        cherrypy.session.pop('mystring', None)


if __name__ == '__main__':
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'application/json')],

        }
    }
    from core.backend.api.host import Host
    cherrypy.tree.mount(Host(), '/host', conf )
    cherrypy.config.update({'server.socket_port': 8888})
    cherrypy.quickstart(StringGeneratorWebService(), '/', conf)