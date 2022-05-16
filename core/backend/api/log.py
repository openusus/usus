#!/usr/bin/env python3
import json
import datetime
import cherrypy

#from bin.getConfig import USERS, USER_LOGINNAME, USER_LASTLOGIN
from core.backend.database.mysql.Connector import openMySQLConnection, selectData, executeMySQLQuery, \
    executeMySQLArgsQuery
# from core.backend.database.mysql.Connector import  createMySQLUsersTable
# from bin.getConfig import getServerName
# from bin.getConfig import executeQueryFetchAll
# from bin.getConfig import getAllRegisteredHosts
from core.backend.config.default import LOG

from core.utils.json import DateTimeEncoder

dbconn = openMySQLConnection()

@cherrypy.expose
class Log(object):

    @cherrypy.tools.accept(media='application/json')
    def GET(self):
        #dbconn = openMySQLConnection()

        Logs = selectData(dbconn, LOG, '*')
        #Users = selectData(dbconn, USERS, 'loginname, ownergroup, firstlogin')
        # Users = selectData(dbconn, USERS, 'firstlogin')
        # print (str(Hosts))
        # test = ['hallo', {'a': 1}]
        # return cherrypy.session['mystring']
        # return bytes(json.JSONEncoder().encode({'Users': Users}), encoding='utf-8')
        return bytes(json.dumps({'Logs': Logs}, cls=DateTimeEncoder), encoding='utf-8')