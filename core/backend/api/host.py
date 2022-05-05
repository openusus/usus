#!/usr/bin/env python3
import json
import sys

import cherrypy

from core.backend.database.mysql.Connector import openMySQLConnection, selectData
# from bin.getConfig import getServerName
# from bin.getConfig import executeQueryFetchAll
# from bin.getConfig import getAllRegisteredHosts
from core.backend.config.default import HOSTS


@cherrypy.expose
class Host(object):

    @cherrypy.tools.accept(media='application/json')
    def GET(self):

        dbconn = openMySQLConnection()

        Hosts = selectData( dbconn, HOSTS, 'Connection, DistributionFamily, Hostname, KernelRelease,enabled,autoupdate,Uptime,Updates', 'order by Updates' )
        #print (str(Hosts))
        # test = ['hallo', {'a': 1}]
        # return cherrypy.session['mystring']
        return bytes( json.JSONEncoder().encode(Hosts), encoding='utf-8') # cherrypy.session['mystring']

    def GET(self, name_or_id=None):
        dbconn = openMySQLConnection()
        if name_or_id != None:
          query = " where Hostname = '" + name_or_id + "'"
        else:
          query = ""
        # if isinstance(name_or_id, int):
        print(query, file=sys.stderr)


        Host = selectData( dbconn, HOSTS, 'Connection, DistributionFamily, Hostname, KernelRelease,enabled,autoupdate,Uptime,Updates', query +  ' order by Updates' )

        if isinstance(Host, list) and len(Host) > 0:

          Result = Host
          return bytes(json.JSONEncoder().encode({'Host': Result, 'Connections': len(Result)}), encoding='utf-8')
        else:

          Result = {'error': 'No Host found', 'Searchedfor': name_or_id}
          return bytes(json.JSONEncoder().encode(Result), encoding='utf-8')




    ## resp = requests.post('http://127.0.0.1:8888/host', json={'p1': ['a', 'b', 1], 'p2': 'test'})

    @cherrypy.tools.json_in()
    def POST (self):
        json_obj = cherrypy.request.json
        if 'p1' in json_obj:
            output = json_obj['p1']
        else:
            output = json_obj
        return bytes(json.JSONEncoder().encode({'got': output}), encoding='utf-8' )