#!/usr/bin/env python3


# python core libs
import os
import pwd
import sys
from datetime import datetime
from configparser import ConfigParser

# import ConfigParser
import mysql.connector
from mysql.connector import errorcode

## OUR imports
from core.backend.config.default import CFGFILENAME, getConfDir, LOG, IPADDRESS, USERID, USERNAME, TIMESTAMP, ACTION, \
    STATUS, DATA, UNKNOWN_LSUS_USER, HOSTS_TABLE

CFGKEYDBNAME = 'database'
CFGKEYDBUSER = 'username'
CFGKEYDBHOST = 'hostname'
CFGKEYDBPASS = 'password'
B64 = 'base64'
CFGSECTDB = 'databaseconnection'


# DB.Core opens the Database Connection for the config got from getDataBaseConfig()
# returns the MySQL Connection Object
# from core.backend.database.mysql.Connector import openMySQLConnection
# dbconn = openMySQLConnection()

# Todo: replace exception error output by LOG2File( to file )
#    - just print "could not connect to database: check log-file"
def openMySQLConnection():
    # global DBCON
    conn = None

    connConfig = getDataBaseConfig()

    print(str(connConfig))

    Fullhost = connConfig[CFGKEYDBHOST]
    HostPort = Fullhost.split(':')
    if len(HostPort) > 1:
        myport = int(HostPort[1])

        # from __future__ import print_function
        # print("using port", myport, file=sys.stderr)
        # TODO: enable in debug mode like this
        # TODO: if ${ENV[GLOBALDEBUG]}: :-?
        #          print >> sys.stderr, "using port", myport,# "spam"
        # print , myport
    else:
        myport = 3306

    try:
        conn = mysql.connector.connect(port=myport, user=connConfig[CFGKEYDBUSER], password=connConfig[CFGKEYDBPASS],
                                       host=HostPort[0], database=connConfig[CFGKEYDBNAME])
        print(conn, conn.is_connected())
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print('MysqlError:')
            print(err)

        print(' while trying to connect to database', connConfig[CFGKEYDBNAME], 'at', connConfig[CFGKEYDBHOST])
    except:
        # except:

        etype, evalue, etb = sys.exc_info()

        # evalue = etype("Cannot openMySQLConnection: %s" % evalue)

        # print etype, evalue, etb
    #  print conn, conn.is_connected()
    #  conn.close()
    return conn


# DB.Core returns the config-Dict
# reads the ConfigFile which returned by getConfigFilePath()
# and assign its Fields to
# result[CFGKEYDBHOST]
# result[CFGKEYDBNAME]
# result[CFGKEYDBUSER]
# result[CFGKEYDBPASS]
# todo: replace error-out with write2errorlogfile && "error occurred (((reading config)))?, check logfile"
def getDataBaseConfig(DEBUG=False):
    result = getEmptyDataBaseConfig(DEBUG)

    config = ConfigParser()
    try:
        config.read(getConfigFilePath())
        result[CFGKEYDBHOST] = config.get(CFGSECTDB, CFGKEYDBHOST)
        result[CFGKEYDBNAME] = config.get(CFGSECTDB, CFGKEYDBNAME)
        result[CFGKEYDBUSER] = config.get(CFGSECTDB, CFGKEYDBUSER)
        result[CFGKEYDBPASS] = config.get(CFGSECTDB, CFGKEYDBPASS)  # .decode( B64 )
    except:
        # print( "Error reading database config " + getConfigFilePath() )
        handleException('getDataBaseConfig')
    # NON Existing Key throws an exception!
    # dummy = config.get( CFGSECTDB, CFGKEYDBUSER+'_x' ) thr

    # { CFGKEYDBHOST: host, CFGKEYDBNAME: db, CFGKEYDBUSER: user, CFGKEYDBPASS: passwd  }
    if DEBUG:
        print(result)

    return result


#
# sys util: print the exception stacktrace
# New_Name: printSysException
def handleException(origin=''):
    etype, evalue, etb = sys.exc_info()
    # evalue = etype( "Cannot exec: %s" % evalue )

    print
    etype, evalue, etb, 'in:', origin


# DB.Core.Config Creates and Returns an Empty Database Dict
# to prevents dict['key.unknown'] errors.
# if debug print result
# TODO: replace by a more robust, secure, encrypted and transparent implementation - see nextcloud?!?
#   maybe builtin store in nosql?!?
# todo: replace debug code by log2file - just print if global debug mode is true
def getEmptyDataBaseConfig(DEBUG=False):
    result = {
        CFGKEYDBHOST: None,
        CFGKEYDBNAME: None,
        CFGKEYDBUSER: None,
        CFGKEYDBPASS: None
    }
    if DEBUG:
        print('getEmptyDataBaseConfig()', '\n', result)

    return result


# Core.Config.Get.ConfigFilePathName
# Gets the full configuration-file pathname
# todo deduplicate redundant code, use builtin nosql
def getConfigFilePath():
    return os.path.join(getConfDir(), CFGFILENAME)


# DB.Core.Select Generic Select Query
# selects  key  FROM table (where clause='')
# TODO: cleanup, check param plausibility (table, column exists..?!)
#      + log to file or db
def selectData(cn, table, key, clause="", DEBUG=False):
    query = "SELECT " + key + " FROM `" + table + "` " + clause

    # dbdolog(dbconn, anIpaddress, anUserid, anUsername, anAction, aStatus, aData, aTimestamp)
    # print '<code>', query, '</code>'
    # log( query, 's' )

    cursor = cn.cursor()
    result = []
    try:
        cursor.execute(query)  #
        result = cursor.fetchall()  # [1]
        status = 0
    except:
        status = 1
        (x, y, z) = sys.exc_info()
        # dblogObj( cn, (x,y,z), aStatus=status, aData="sys.exc_info()" )
        result.append(
            (str(x).replace('<', '&lt;').replace('>', '&gt;'), y, str(z).replace('<', '&lt;').replace('>', '&gt;')))
        # result.append( string.replace( str( x ), '<', '&lt;' ).replace('>', '&gt;').join('') )
        # result.append(   )
        # result.append( ev )
        # result.append( ts )

    if DEBUG:
        dblogObj(cn, query, aStatus=status, aData="DEBUG: getConfigselectData")
    # if cursor.with_rows:
    #  print "rowcount:", cursor.rowcount
    # for value in cursor:
    # result.append((value))
    # result = "{}".format( str( value ) )
    # result = executeMySQLQuery( cn, query )
    # print '<code>', query, '</code>' #+ "=" + str( result )
    # cursor.close()
    return result  # cursor.fetchone()[0] #result #[0] )# cursor


# DB.Core.ExecSQL - Executes the given SQL Query with the given Variables for C/Python-like placeholders %1, %2
# TODO:  log to file or db -
#   AND Cleanup
def executeMySQLArgsQuery(cn, query, args):
    result = None

    cursor = cn.cursor()

    # print "Query", query
    cursor.execute(query, args)
    if cursor.with_rows:
        result = result.rowcount
    else:
        result = 0
    # print "1", result
    cursor.close()
    # print "2", result
    # cn.close()

    #  print "r:", result.rowcount
    return result


# DB.Core.LOG - Execs the Insert LOG Data in the "$LOG" Table - calls -> executeMySQLArgsQuery with SQL %s Placeholders
# TODO: log to file, then switch to db if available - AND - consolidate
def dbdolog(dbconn, anIpaddress='127.0.0.1', anUserid=0, anUsername='N/A', anAction='None', aStatus=0, aData='None',
            aTimestamp=datetime.now()):
    query = "INSERT INTO " + LOG + \
            '(' + IPADDRESS + ', ' + USERID + ', ' + USERNAME + ', ' + ACTION + ', ' + STATUS + ', ' + DATA + ', ' + TIMESTAMP + ')' \
                                                                                                                                 "VALUES (%s, %s, %s, %s, %s, %s, %s)"

    args = (anIpaddress, anUserid, anUsername, anAction, aStatus, aData, aTimestamp)
    result = executeMySQLArgsQuery(dbconn, query, args)
    dbconn.commit()


# DB.Core.LOG - logs the given objects, with the given timestamp: defaults to now()
# - Use the given dbconn
# calls --> dbdolog( dbconn, Ipaddress, Userid, Username,
#   with the current users remote IP Address and username if it can be detected via pwd.getpwnam() or ENV[] or is known
# TODO: log to file, then switch to db if available - AND - consolidate
def dblogObj(dbconn, anObject, aStatus=0, aData="N/A", aTimestamp=datetime.now()):
    Ipaddress = os.environ.get("REMOTE_ADDR", "N/A")
    Username = os.environ.get('REMOTE_USER', UNKNOWN_LSUS_USER)
    ## if running outside BROWSER Session UserID = UID of Current PID
    if Username == UNKNOWN_LSUS_USER:
        Userid = os.getuid()
        Username = pwd.getpwuid(Userid).pw_name
    else:
        Userid = pwd.getpwnam(Username).pw_uid
    Action = str(anObject)
    dbdolog(dbconn, Ipaddress, Userid, Username, Action, aStatus, aData, aTimestamp)


# DB.Core.Create HostsTable
# TODO: replace static "Strings" by constants or dict{key}=value pairs
#   to have a generic "interface"
def createMySQLHostsTable(cn, tableName=HOSTS_TABLE):
    executeMySQLQuery(cn,  # "CREATE TABLE `" + tableName + "` (`name` varchar(40) NOT NULL) Engine=InnoDB" )
                      "CREATE TABLE IF NOT EXISTS `" + tableName + "` ("
                                                                   "  `Connection` varchar(64) NOT NULL,"
                                                                   "  `DistributionFamily` varchar(32),"
                                                                   "  `Hostname` varchar(50),"
                                                                   "  `KernelRelease` varchar(32),"
                                                                   "  `KernelVersion` varchar(128),"
                                                                   "  `Uptime` varchar(128),"
                                                                   "  `Boottime` varchar(64),"
                                                                   "  `Updates` int, "
                                                                   "  `ScanTime` datetime, "
                                                                   "  `enabled`  bool, "
                                                                   "  `autoupdate` bool, "
                                                                   "  `owneremail` varchar(64), "
                                                                   "  `LastUpdate` datetime, "
                                                                   "  `owneraccount` varchar(60), "
                                                                   "  `ownergroup` varchar(60), "
                                                                   "  `LockDate` datetime, "
                                                                   "  `LockOwner` varchar(64), "
                                                                   "  `LockHost` varchar(64), "
                                                                   "  `LastPingDate` DATETIME, "
                                                                   "  `PingfailCount` INT(1), "
                                                                   "  `PingfailReason` TEXT, "

                                                                   "  PRIMARY KEY (`Connection`)"
                                                                   ") ENGINE=InnoDB")

    ## TODO: Insert last ping data fields
    ## TODO:
    ## TODO: see update to apply.update_to 0.9.py


# DB.Core.ExecSQL - Executes the given SQL Query
# TODO:  log to file or db -
#   AND Cleanup
def executeMySQLQuery(cn, query):
    result = 0  # None

    cursor = cn.cursor()
    #
    cursor.execute(query)
    if cursor.with_rows:
        result = result.rowcount
    else:
        result = 0
    # print "1", result
    cursor.close()
    # print "2", result
    # cn.close()

    #  print "r:", result.rowcount
    return result
