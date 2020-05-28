#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#
# Setup LSUS 
# Handles Input Form, Verification and Database and Table Creation.
#
'''



import os
import os.path
import sys
import string
import time
import cgi

import cgitb
import lsusversion


import commands

from datetime import date, datetime, timedelta

import mysql.connector
from mysql.connector import errorcode

sys.path.append( os.getcwd() )
sys.path.append( os.path.join( os.getcwd(), "lib" ) )
sys.path.append( os.path.join( os.getcwd(), "..", "lib" ) )
sys.path.append( os.path.join( os.getcwd(), "bin" ) )

import HTML
import getConfig
from getConfig import DISTRIBUTIONFAMILY, DEBIAN, REDHAT, SUSE, LOCKDATE, LOCKOWNER, LOCKHOST,\
  whereConnection, OWNEREMAIL, CFGKEYDBHOST,CFGKEYDBNAME,CFGKEYDBUSER,   CFGKEYDBPASS


def wprint( cli=1, *argues ):
  
  if cli:
    print argues        
  else:
    print argues, '<br>'




def getDBConnection( dbconfig, test=False ):
  dbconnection = None
  
  # print 'Y', dbconfig[ CFGKEYDBNAME ]
  try:
    if dbconfig.has_key( CFGKEYDBNAME ) and ( dbconfig.get( CFGKEYDBNAME  ) != 'None' or dbconfig.get( CFGKEYDBNAME  ) != '' ):
      
      dbconnection = mysql.connector.connect( host = dbconfig[ CFGKEYDBHOST ], user = dbconfig[ CFGKEYDBUSER ], password = dbconfig[ CFGKEYDBPASS ], database =  dbconfig[ CFGKEYDBNAME ] )
    else:
      dbconnection = mysql.connector.connect( host = dbconfig[ CFGKEYDBHOST ], user = dbconfig[ CFGKEYDBUSER ], password = dbconfig[ CFGKEYDBPASS ] )
  except mysql.connector.Error as err:
    print err.errno #  mysql.connector.Error# .message
    print err.sqlstate
    print err.msg
    print str(err)
    print 'Fix that error first, to continue.'
    if test == False:
      sys.exit(err.errno)
  except:
    
    dbconnection = None
    
  if test == True:
    return dbconnection != None
  return dbconnection



def deleteDatabase( delDB, cli=1 ):
  print "delete db", delDB
  
  raw_input( "Enter to continue. CTRL+C to cancel." )
  
  dbconfig = getConfig.createDatabaseConfig( 'otmucdbmariadb1.opentext.net', 'itdoku', 'itdoku.' )
  
  db = getDBConnection( dbconfig )
  
  getConfig.dropDatabase( db, delDB )
      
  db.close()
  
  
def askForConfigWrite():
  
  answer = raw_input( "Write config? [y|N] " ) 
  if answer == 'y': 
    return True
  else:
    return False
  

def testIfConfigWorks(  config ):
  
  result = getDBConnection( config, test = True )
  print " DBconfig works ",  result 
  
  #if result:
  #  return True #result != {}
  return result #False 


def createDBConnection( argv ):
  shallIWrite = False
  configWorks = False
  configExists = False
  
  Interactive = False

  host=''
  user=''
  passwd=''
  schema=''
  noninteractive=0

  # print  'len: ', len(argv),  'args: ', argv
  if len(argv) >= 1:
    host = argv[0]
  if len(argv) >= 2:
    host = argv[1]
  if len(argv) >= 3:
    host = argv[2]
  if len(argv) >= 4:
      host = argv[3]
  if len(argv) >= 5:
    if argv[4] == 'y':
         noninteractive=1
  config = getConfig.getDataDaseConfig()

  while True: # shallIWrite == False:
    
    
    #while True:
      
    configWorks = testIfConfigWorks( config )
        
      #print "result: ", result
    if configWorks == True:

      if noninteractive or askForConfigWrite() == True:
        
        getConfig.writeDBConfig( config )
        return
        break   
        #break





    #else:
    config = getConfig.getInputDatabaseConfig( config, host, user, passwd, schema  )
    #if configWorks == True:
    #    break
       
    print "config", config   
            
    #if askForConfigWrite() == True:
    #  break      
    
       
    
    
    
      
      



def testDBConfig( dbconfig ):
  try:
    getDBConnection( dbconfig )
    return True
  except:
    #print "no valid db config given, maybe you've to create one first."
    return False


def createDatabase( newDB, cli=1 ):
# config (file) exists?
  #db=None
  # dbconfig = getConfig.getEmptyDataBaseConfig()
  #dbconfig = getConfig.getLocalDatabaseConfig(  DEBUG=True )
  dbconfig = getConfig.getDataDaseConfig()
  
  #dbconfig = getConfig.createDatabaseConfig( 'otmucdbmariadb1.opentext.net', 'itdoku', 'itdoku.' )
  
  #dbconfig[CFGKEYDBHOST] = 'otmucdbmariadb1.opentext.net'
  #dbconfig[CFGKEYDBUSER] = 'itdoku'
  #dbconfig[CFGKEYDBPASS] = 'itdoku.'
# config check ping Server / Test Connection

  wprint( cli, 'Host', dbconfig[CFGKEYDBHOST] )
  wprint( cli, 'User', dbconfig[CFGKEYDBUSER] )
  wprint( cli, 'Pass', dbconfig[CFGKEYDBPASS] )
  wprint( cli, 'Schema', dbconfig[CFGKEYDBNAME] )

  #CFGKEYDBHOST: host, CFGKEYDBNAME: db, CFGKEYDBUSER: user, CFGKEYDBPASS: passwd
# user=connConfig[CFGKEYDBUSER], password=connConfig[CFGKEYDBPASS], host=connConfig[CFGKEYDBHOST], database=connConfig[CFGKEYDBNAME] 

  #sys.exit(0)
  if dbconfig.has_key( CFGKEYDBNAME ) and dbconfig.get( CFGKEYDBNAME  ) == 'None':
    dbconfig.pop( CFGKEYDBNAME )
  
  print "conf", dbconfig

  if 1:
      #conn=mysql.connector
      
      #try:
      db = getDBConnection( dbconfig )
        
        
      #except:
      #  print "no valid db config given, maybe you've to create one first."
      #  exit( 222 )
            
      cursor = db.cursor() 
      cursor.execute("SELECT VERSION()")
      results = cursor.fetchone()
      print "Version", results
      
          
      getConfig.createDatabase( db, newDB, True )
      
      db.close()
      
      dbconfig[ CFGKEYDBNAME ] = newDB
      
      dbnew = getDBConnection( dbconfig )
      
      if 1:
        getConfig.createMySQLLogTable( dbnew )
        getConfig.createMySQLHostsTable( dbnew )
      
        getConfig.createMySQLPackagesTable( dbnew )
        getConfig.createMySQLUpgradeTable( dbnew )
      
        getConfig.createMySQLUsersTable(  dbnew )
        
        getConfig.insertUserInDB(dbnew, 'firstlogin' )
        
        getConfig.writeDBConfig( dbconfig )
      # Check if anything at all is returned
      if results:
        return True
      else:
        return False               
  #except:  MySQLdb.Error, e:
  #  print "E:"
    #print "ERROR %d IN CONNECTION: %s" % (e.args[0], e.args[1])
  return False



#print "Content-type: text/html; charset=utf-8\n\n"
# print "Hello" 
# getConfig.CFGKEYLDAPHOST: host, CFGKEYLDAPBIND: bind, CFGKEYLDAPNAME: name, CFGKEYLDAPPWFILE: passfile
def printForm():
  
  print "Content-type: text/html; charset=utf-8\n\n"
  
  db_form   = getConfig.loadTemplateReplaceData( getConfig.SETUP_DB_FORM_TEMPLATE, getConfig.getDataDaseConfig() )
  try:
    ldap_form = getConfig.loadTemplateReplaceData( getConfig.SETUP_LDAP_FORM_TEMPLATE, getConfig.getLdapCfg() )
  except:
    ldap_form = ''

  print  getConfig.loadTemplateReplaceData( getConfig.SETUP_TEMPLATE, { 'DB_FORM': db_form, 'LDAP_FORM': ldap_form } )
#print  
#checkDatabaseConfig()



def doCLI( argv ): 
  
  if len( argv ) < 2:
    print 'wrong number of args - must be at least 2, given ', len( argv), '...(', argv, ')'
  else:
    if argv[1] == "database":
      print 'create db  ', argv[2]
      createDatabase( argv[2] )
      print 'create tables in', argv[2]
      
    if argv[1] == "connection":
      print 'create db connection with  ', argv[2:]
      createDBConnection( argv[2:] )
      print 'created connection with', argv[2:]  
      
    if argv[1] == "lsusadmin":
      print "===[lsusadmin]===="
      print "On server side a useraccount is necessary for this a ssh key "
      print "will be generated, and this key will be uploaded/appended "
      print "to each lsusclient's .ssh/authorized keys file"      
      print "the admin user is named lsusadmin by default."
      print "\n--------------\n"
      print "The lsusadmin is a local user in which context the lsus update cronjob runs."
      print "so therefore these user has just to be created as regular user on this local server."
      
      print 'os.getegid(), os.getgid()', os.getegid(), os.getgid()
      print 'os.geteuid(), os.getuid()', os.geteuid(), os.getuid()
      
     
      
    elif argv[1] == "uninstall":
      print 'delete db ', argv[2]
      deleteDatabase( argv[2] )
      print 'deleted db', argv[2]
      
    elif argv[1] == "help":
      print "Valid Command args: connection, database, lsusadmin, lsusclient, ldap, help arg"      
      print "Current args:",     argv[1:]
  


if __name__ == '__main__':
  
  if  os.environ.get( "REMOTE_ADDR", "" ) == '':    
    print lsusversion.COMPLETE
    
    if len( sys.argv ) > 1:
      doCLI( sys.argv )
    else:
      print ""
      print "no setup command given!"
    
  else:
    cgitb.enable()
    printForm()
  
  
  
else:
      
  print "Content-type: text/html; charset=utf-8\n\n"
  
  print "Should never seen! Otherwise inform marc.pahnke@gmx.de with the Info: LSUS Setup.py </main-else!>"

