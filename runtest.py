#!/usr/bin/env python3

from core.backend.config.default import getBaseDir

from core.backend.database.mysql.Connector import createMySQLHostsTable
from core.backend.database.mysql.Connector import openMySQLConnection,openMySQLConnection, createMySQLHostsTable
from core.backend.database.mysql.Connector import openMySQLConnection, createMySQLUsersTable, createMySQLLogTable, dblogObj
# import requests


if __name__ == '__main__':



    db = openMySQLConnection()

    createMySQLLogTable(db)

    basedir = getBaseDir()

    dblogObj( db, basedir, 0, 'basedir' )

    createMySQLUsersTable(db)


    import requests
    # resp = requests.get('http://127.0.0.1:8888/user')
    # print('resp=', resp.text)
    # print('resp["Users"][0][1]=', resp.json()['Users'][0][1])
    # USERSARR = resp.json()['Users']
    # login=1
    # last=3
    # for user in USERSARR:
    #     print('resp["Users"].login last', user[login],  user[last])

    for count in range(5, 70):
        #if count % 1000 == 0:
        resp = requests.post('http://127.0.0.1:8888/user', json={'loginname': 'testlogin_' + str(count), 'commit':'true' })
        #else:
        # resp = requests.post('http://127.0.0.1:8888/user', json={'loginname': 'testlogin_' + str(count) })
        #print('resp=', resp.json() )
        dblogObj( db, resp.json(), 0, 'resp: http://127.0.0.1:8888/user' )

