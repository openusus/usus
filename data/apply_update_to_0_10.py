#!/usr/bin/env python2

import sys
import mysql.connector

from mysql.connector import errorcode
from getConfig import getDataDaseConfig


import getConfig


def doDatabaseUpgrade():
  
  try:
    dbconn = getConfig.openMySQLConnection()
  except mysql.connector.Error as err:
      if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print( "Something is wrong with your user name or password" )
      elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print( "Database does not exist" )
      else:
        print( 'MysqlError:' )
        print( err )
        
      print ' while trying to connect to database', getDataDaseConfig()[getConfig.CFGKEYDBNAME], 'at', getDataDaseConfig()[getConfig.CFGKEYDBHOST]
  except:
    #except: 
      etype, evalue, etb = sys.exc_info()

  #print getDataDaseConfig()
  db = getDataDaseConfig()[getConfig.CFGKEYDBNAME]
  host = getDataDaseConfig()[getConfig.CFGKEYDBHOST]
  print 'Updating database', db, 'at',  host
  #print dbconn
  qry = 'ALTER TABLE `'+ db + '`.`Users` ADD COLUMN `sortcol` varchar(32) NULL AFTER `checktime`,  ADD COLUMN `sortdir` varchar(6) NULL AFTER `sortcol`, ADD COLUMN `MIN_ROW` INTEGER UNSIGNED NULL AFTER `sortdir`, ADD COLUMN `MAX_ROW` INTEGER UNSIGNED NULL AFTER `MIN_ROW`'
  ## qry = 'ALTER TABLE `'+ db + '`.`Users` ADD COLUMN `MIN_ROW` INTEGER UNSIGNED NULL AFTER `sortdir`, ADD COLUMN `MAX_ROW` INTEGER UNSIGNED NULL AFTER `MIN_ROW`'
  # qry='drop table `test`'
  # qry='show tables'
  #qry = 'create table test( counter INT)'
  result = getConfig.executeMySQLQuery(dbconn, qry) #   executeQueryFetchAll( dbconn, qry )

  if result == 0:
    print " - successful!"
  # ProgrammingError: 1142 (42000): ALTER command denied to user '${lsusupdateuser}'@'linux-updateserver.my.lan.local' for table 'Hosts'

  dbconn.close()
  
  
  
  
  
doDatabaseUpgrade()