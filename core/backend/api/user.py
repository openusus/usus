#!/usr/bin/env python3
import json
import datetime
# from datetime import date, datetime
import cherrypy

#from bin.getConfig import USERS, USER_LOGINNAME, USER_LASTLOGIN
from core.backend.database.mysql.Connector import openMySQLConnection, selectData, executeMySQLQuery, \
    executeMySQLArgsQuery
# from core.backend.database.mysql.Connector import  createMySQLUsersTable
# from bin.getConfig import getServerName
# from bin.getConfig import executeQueryFetchAll
# from bin.getConfig import getAllRegisteredHosts
from core.backend.config.default import USERS, USER_LOGINNAME, USER_LASTLOGIN

# class DateTimeEncoder(JSONEncoder):
#         #Override the default method
#         def encode(self, o):
#             print('O: ',  o , file=sys.stderr)
#             if isinstance(o, (datetime.date, datetime.datetime)):
#                 print('D: ', o, file=sys.stderr)
#                 return o.isoformat()
#             return super.encode(self, o)
from core.utils.json import DateTimeEncoder

dbconn = openMySQLConnection()

@cherrypy.expose
class User(object):

    @cherrypy.tools.accept(media='application/json')
    def GET(self):
        #dbconn = openMySQLConnection()

        Users = selectData(dbconn, USERS, '*')
        #Users = selectData(dbconn, USERS, 'loginname, ownergroup, firstlogin')
        # Users = selectData(dbconn, USERS, 'firstlogin')
        # print (str(Hosts))
        # test = ['hallo', {'a': 1}]
        # return cherrypy.session['mystring']
        # return bytes(json.JSONEncoder().encode({'Users': Users}), encoding='utf-8')
        return bytes(json.dumps({'Users': Users}, cls=DateTimeEncoder), encoding='utf-8')


    @cherrypy.tools.json_in()
    def POST (self):
        global dbconn
        json_obj = cherrypy.request.json
        commit = 0
        if 'loginname' in json_obj:
            newlogin = json_obj['loginname']
        if 'commit' in json_obj:
            commit = 1
            # dbconn = openMySQLConnection()
            insertUserInDB( dbconn, newlogin, commit )
            output = { 'created': [ json_obj['loginname'], newlogin ] }
        else:
            output = json_obj
        return bytes(json.dumps({'got': output}, cls=DateTimeEncoder), encoding='utf-8' )




# from core.backend.api.user import insertUserInDB
# from core.backend.database.mysql.Connector import openMySQLConnection
# cn = openMySQLConnection()
# insertUserInDB( cn, 'marc' )
# DB.Core.User Insert
# inserts the given loginname if not exists, otherwise update the lastlogi timestamp
def insertUserInDB( dbconn, loginname, commit ):
  #cn = openMySQLConnection()
  query = 'INSERT INTO ' + USERS + '(' + USER_LOGINNAME + ',rwmode,firstlogin ) VALUES ( "' + loginname + '", false,"'+ str( datetime.datetime.now() ) +'" ) ON DUPLICATE KEY UPDATE ' + USER_LASTLOGIN + "='"  +     str( datetime.datetime.now() ) + "'"
  result =  executeMySQLQuery(dbconn, query)
  # dbconn.commit()

  query = "Update " + USERS + \
          " SET " +  USER_LASTLOGIN + ' = %s' \
          " WHERE " +  USER_LOGINNAME +  " = %s "
  args = ( str( datetime.datetime.now() ), loginname )
  executeMySQLArgsQuery(dbconn, query, args)

  if( commit == 1 ):
    dbconn.commit()
  # dbconn.close()
  return result
