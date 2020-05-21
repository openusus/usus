#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import of Entire Core Modules
import os
import os.path
import sys
import string
import commands
import time
import smtplib
import zlib
import shlex
import pwd
import itertools
import socket
import base64

import ConfigParser

##
# Import part of core Modules
from subprocess import Popen, PIPE, STDOUT
from datetime import date, datetime, timedelta
from email.MIMEText import MIMEText

from pythonzenity import Entry
#from xml.dom.minidom import parse, parseString, Element, Node, NamedNodeMap

# Database connector
import mysql.connector
from mysql.connector import errorcode

# own Modules
import lsusversion
from types import NoneType



basepath = os.path.join( os.path.dirname( os.path.realpath( __file__ ) ), '..' )
sys.path.append( os.path.join( basepath, "lib" ) )
sys.path.append( os.path.join( basepath, "parallel-ssh" ) )
sys.path.append( os.path.join( basepath, "parallel-ssh", 'bin' ) )

import pssh

from psshlib import psshutil
from psshlib.manager import Manager, FatalError
from psshlib.task import Task
from psshlib.cli import common_defaults

from webtask import WebTask

#from psshlib.cli import common_parser, common_defaults
PSSH_TIMEOUT = 18000 # 3 hours Update Time per system should be more than enough! 10800 = 3600 * 3 = (60*60) * 3 

DATAFOLDERNAME = 'data'

CFGKEYLDAPHOST='ldaphost'
CFGKEYLDAPBIND='ldapbind'
CFGKEYLDAPNAME='ldapname'
CFGKEYLDAPPWFILE='ldappass'

CFGDIRNAME='conf'
CFGFILENAME='lsus.cfg'
LDAPCFGFILENAME='lsus.ldap.cfg'

CFGSECTLDAP='ldapconnection'
CFGSECTDB='databaseconnection'
CFGKEYDBNAME='database'
CFGKEYDBUSER='username'
CFGKEYDBHOST='hostname'
CFGKEYDBPASS='password'
 
B64='base64' 
  
LDAPADMINGROUP  = 'LDAPADMINGROUP'
urlprefix      = 'https://linux-updateserver.my.lan.local/lsus/'
DNS_DOMAIN     = 'my.lan.local'
DEFAULT_DOMAIN = 'openlsus.org'

# TODO: Set during initial setup.
LDAP_AUTH_SERVER = 'ldap_ad_server.my.lan.local'
LDAP_BIND_BASEDN = 'DC=my,DC=lan,DC=local'
LDAP_USER_NAME   = 'ldap_auth_user_name'
LDAP_PASSWD_FILE = '/home/lsusupdateuser/.hidden.credential.t'

SMTP_MAIL_FROM    = "vtsystemadministration@opentext.com"
SMTP_MAIL_REPLYTO = "vtsystemadministration@opentext.com"
SMTP_MAIL_SERVER = "webmail-eu.opentext.com" # a smtp server whcih allows the user below to send email w/o authentication.
SMTP_MAIL_FROM_ADDRESS = "marc.pahnke@opentext.com" # must be able to send email via SMTP_MAIL_SERVER w/o authentication - i.e. from kind of internal address

UNKNOWN_LSUS_USER = 'Unknown_LSUS_User'
LSUSADMIN = LSUS_ADMIN = DEBUG_EMAIL_ADDRESS = 'marc.pahnke@gmx.de'


HOSTS = """Hosts"""
HOSTS_TABLE = 'Hosts'
PACKAGES = 'Packages'
USERS = 'Users'
LSUS_CONTENT_AREA = "lsus-content-area"
WHICH = 'which'

APT_SHOW_VERSIONS = 'apt-show-versions'
# REG_HOSTCONF="conf/registered.servers.list.conf"

# DB CONSTANTS


# USERS Table
USER_LOGINNAME  = 'loginname'
USER_RWMODE     = 'rwmode'  
USER_LASTLOGIN  = 'lastlogin' 
USER_FIRSTLOGIN = 'firstlogin'

SORTCOL='sortcol'
SORTDIR='sortdir'
MIN_ROW='MIN_ROW'
MAX_ROW='MAX_ROW'


## DB COLUM NAMES
CONNECTION  = "Connection"
AUTOUPDATE  = "autoupdate"
INFORMOWNER = "informowner"
OWNEREMAIL  = "owneremail"
OWNERACCOUNT= "owneraccount"
OWNERGROUP  = "ownergroup"
DOMAIN      = 'domain'
ENABLED     = "enabled"
UPDATES     = 'Updates'
SCANTIME    = 'ScanTime'
LASTUPDATE  = 'LastUpdate'
KERNELRELEASE ='KernelRelease'
HOSTNAME = 'Hostname'

PINGFAILCOUNT  = 'PingfailCount'
PINGFAILREASON = 'PingfailReason'
LASTPINGDATE   = 'LastPingDate'

MAX_PINGFAILCOUNT_BEFORE_DISABLE = 10

# LOG DB COLUMNS
LOG       = 'LOG'
IPADDRESS = "Ipaddress"
USERID    = "Userid"
USERNAME  = "Username"
TIMESTAMP = "Timestamp"
ACTION    = "Action"
STATUS    = "Status"
DATA      = "Data"

_UPGRADE='upgrade'
_UPDATE='update'
_CHECK='check'

INITIAL=1
UPDATE=-1
NONE=None

LOCKDATE  = "LockDate"
LOCKOWNER = "LockOwner"
LOCKHOST  = "LockHost"

REDHAT  = 'redhat'
RED_HAT = 'red hat'
ORACLE  = 'oracle'
CENTOS  = 'centos'
FEDORA  = 'fedora'
SUSE    = 'suse'
DEBIAN  = 'debian'
UBUNTU  = 'ubuntu'
MINT    = 'mint'
JESSIE  = 'jessie'
SID     = 'sid'
STRETCH = 'stretch'
SUNOS   = 'sunos'
SOLARIS = 'solaris'



REDHATS  = [ REDHAT, CENTOS, RED_HAT, ORACLE, FEDORA ]
SUSES    = [ SUSE ]
DEBIANS  = [ DEBIAN, UBUNTU, MINT, JESSIE, SID, STRETCH ]
SOLARIS_ = [ SOLARIS ]

DISTFAMILIES = {
       SOLARIS: SOLARIS_,
       REDHAT: REDHATS,
       SUSE: SUSES,
       DEBIAN :DEBIANS
       
       }

DISTRIBUTIONFAMILY='DistributionFamily'
# 'ScanTime', 'LastUpdate',  'KernelRelease', 'Hostname'
sqlkeys = [ UPDATES, SCANTIME, LASTUPDATE, KERNELRELEASE, HOSTNAME   ] #, 'LastCheckTime' ] # , 'UpdateDetails',  'Perform Update' ]

tstamp = str( datetime.today() )
# 'KernelVersion', 'Uptime',

sqlinsertcommands = {                     
                      "Hostname": "hostname",
                      "KernelRelease": "uname -r",
                      "KernelVersion": "uname -v",
                      "Uptime": "uptime | cut --characters=-63",
                      # "Boottime": "uptime -s",
                      "Updates": "sudo apt-get -qq -s -y upgrade | grep -i ^Inst | wc -l"
                     }

sqlinsertcommands_suse = {                     
                      "Hostname": "hostname",
                      "KernelRelease": "uname -r",
                      "KernelVersion": "uname -v",
                      "Uptime": "uptime | cut --characters=-63",
                      # "Boottime": "uptime -s",
                      # "Updates": "sudo env LANG=en_US zypper -v -A -n pchk|grep 'patches needed' |cut -d ' ' -f 1"
                      "Updates": "sudo env LANG=en_US zypper -n lp | grep needed | wc -l"
                     }

sqlinsertcommands_redhat = {                     
                      "Hostname": "hostname",
                      "KernelRelease": "uname -r",
                      "KernelVersion": "uname -v",
                      "Uptime": "uptime | cut --characters=-63",
                      # "Boottime": "uptime -s",
                      "Updates": "echo 1" # "sudo apt-get -qq -s -y dist-upgrade | grep -i -c ^Inst"
                     }

sqlinsertcommands_solaris = {                     
                      "Hostname": "hostname",
                      "KernelRelease": "uname -r",
                      "KernelVersion": "uname -v",
                      "Uptime": "uptime | cut -d , -f 1",
                      # "Boottime": "uptime -sd",
                      "Updates": "env LANG=C pkg update -n --accept | grep  -i 'Packages to update:' | head -1 | cut -d : -f 2" # "sudo apt-get -qq -s -y dist-upgrade | grep -i -c ^Inst"
                     }


sqlfordist={}
sqlfordist[ DEBIAN  ] = sqlinsertcommands
sqlfordist[ SUSE    ] = sqlinsertcommands_suse
sqlfordist[ REDHAT  ] = sqlinsertcommands_redhat
sqlfordist[ SOLARIS ] = sqlinsertcommands_solaris

updatecommand={}
updatecommand[ DEBIAN  ] = 'export DEBIAN_FRONTEND=noninteractive && sudo apt-get -q -y -V $1 -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade && echo "done at ' + tstamp + '"'
updatecommand[ SUSE    ] = 'sudo zypper --non-interactive --no-gpg-checks --gpg-auto-import-keys patch && echo -n "done at" && date && echo ""'
updatecommand[ SOLARIS ] = '`which sudo` `which pkg` update && echo -n "done at" && date && echo ""'
updatecommand[ REDHAT  ] = '`which sudo` `which yum` -yt update && echo -n "done at" && date && echo ""'
  

upgradecommand={}
upgradecommand[ DEBIAN  ] = 'export DEBIAN_FRONTEND=noninteractive && sudo apt-get -q -y -V $1 -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" dist-upgrade'
upgradecommand[ SUSE    ] = "sudo zypper --non-interactive --no-gpg-checks --gpg-auto-import-keys update"
upgradecommand[ SOLARIS ] = '`which sudo` `which pkg` update && echo -n "done at" && date && echo ""'
upgradecommand[ REDHAT  ] = "`which sudo` `which yum` -yt update"


listpackagesCommand = {}
listpackagesCommand[ DEBIAN  ] = 'apt-show-versions'
listpackagesCommand[ SUSE    ] = 'env LANG=en_US zypper -n lp'
listpackagesCommand[ REDHAT  ] = 'env LANG=en_US yum -yt check-update ; test $? -eq 100 -o $? -eq 0'
listpackagesCommand[ SOLARIS ] = 'env LANG=C pkg list'

#
# Template Constants
#
QUERY_FORM_TEMPLATE      = 'html/templates/query.form.html'
COMMAND_FORM_TEMPLATE    = 'html/templates/command.form.html'
REGISTER_FORM_TEMPLATE   = 'html/templates/register.form.html'
TEMPLATE_MAIN_TABLE      = 'html/templates/main.table.control.form.html'
SETTINGS_FORM_TEMPLATE   = 'html/templates/settings.form.html'

SETUP_TEMPLATE           = 'html/templates/setup.html'
SETUP_DB_FORM_TEMPLATE   = 'html/templates/setup.db.form.html'
SETUP_LDAP_FORM_TEMPLATE = 'html/templates/setup.ldap.form.html'

LSUSUPDATEUSER = 'lsusupdateuser'

runningProcs = {}


def where( KEY, VAL ):
  return ' WHERE ' + KEY + "='" + VAL + "'"


def whereConnection( connection ):  
  return where( CONNECTION, connection ) 


def whereDist( dist ): 
  return where( DISTRIBUTIONFAMILY, dist )



def getVersion():
    return lsusversion.VERSION

def getFullProduct():
    return lsusversion.FULL_PRODUCT

def getCommandStatusValue( hostConnection, aCommand, verbose = False ):
    command = 'sudo -u ' + LSUSUPDATEUSER  + ' ssh ' + hostConnection + ' "' + aCommand + '"' #"sudo -u svtaskschedule ssh '" + hostConnection + ' "' + aCommand + '"'
    if verbose != False:
      print command
      print command
    return commands.getstatusoutput( command )

def whichExists( aConnection, command ):
    return getCommandStatusValue( aConnection, 'env ' + WHICH + ' ' + command )[0] == 0

def filePathExists( aConnection, whichPath, command, verbose = False ):
    result = getCommandStatusValue( aConnection, whichPath + ' ' + command, verbose )
    
    if verbose != False:    
      print result, aConnection, whichPath, command
      
    sys.stdout.flush()
    return result[0] == 0

def getWhichPath( aConnection, command ):
   return getCommandValue( aConnection, 'env ' + WHICH + ' ' + command )



def getFilePath( aConnection, whichPath, command ):
  return getCommandValue( aConnection, whichPath + ' ' + command )


  
def detectDistro( aConnection, verbose = False ):
  resultFamily="unknown"
  result={}
  # result[ 'dist' ] = 'u n k n o w n' ....stretch with '' to supress false positives as suse-user@debian at redhat hosts ;-)
  result[ 'unknown' ] = 'unknown (could not detect at "' + string.join( list( aConnection ),' ' ) + '" )'
  #print "aConnection", aConnection
  
  uname = getCommandValue( aConnection, 'uname' )
  
  if verbose != False:
    print uname
  
  uname_r = getCommandValue( aConnection, 'uname' + ' -r' )
  
  if verbose != False:
    print uname_r
    
  if uname.lower() == 'hp-ux':
    raise Exception( "Non supported os", uname )
  
  if uname.lower() == 'aix':
    raise Exception( "Non supported os", uname )
  
  if uname.lower() == 'sunos' and uname_r == '5.10':
    raise Exception( "Non supported os", str( uname ) + ' ' + str( uname_r ) )
  
  if uname.lower() == 'sunos' and uname_r == '5.9':
    raise Exception( "Non supported os", str( uname ) + ' ' + str( uname_r ) )
  
  if uname.lower() == 'sunos' and uname_r == '5.8':
    raise Exception( "Non supported os", str( uname ) + ' ' + str( uname_r ) )
  
  if whichExists( aConnection, WHICH  ):  
    if verbose != False:
      print "which exists"
    whichPath = getWhichPath( aConnection, WHICH )
    #print "whichPath:", whichPath
    if filePathExists( aConnection, whichPath, "lsb_release", verbose ):
      if verbose != False:
        print "lsb_release exists"
      lsbPath=getFilePath( aConnection, whichPath, "lsb_release" )
      distData=string.split( getCommandValue( aConnection, lsbPath + ' -a' ), '\n' )
      for line in distData:
        dataset = string.split( line, ':' )
        if len( dataset ) > 1:
          ### print  dataset[ 0 ],  dataset[ 1 ]
          result[ str( dataset[ 0 ] ) ] = string.strip( str( dataset[ 1 ] ) ) # i.e 'Distributor ID' = 'Ubuntu'
      lsbDist = findDistFamily( result, verbose )
      if lsbDist != '':
          return lsbDist
          
    else:
      # try: force cat /etc/release        
      status, output = getCommandStatusValue( aConnection, "cat /etc/*release*" ) # | grep -i release | grep -iE 'centos|redhat'" )
      if status == 0:
        result[ '/etc/release' ] = output
      else:
        result[ 'unknown' ] = 'unknown: (cat /etc/*release* could not executed at "' + aConnection  + '" ) cause: ' + string.join( list( str( output ) ), ' ' )  
  else: # which doesnt exist         
    result[ 'unknown' ] = 'unknown (which could not found in path at "' + aConnection + '" )'
  
  if verbose != False: # Set to 1 to Debug
    print "Result with /etc/release",  result
  
  lsbDist = findDistFamily( result, verbose )
  if lsbDist != '':
    return lsbDist
    
  vstatus, voutput = getCommandStatusValue( aConnection, "cat /etc/debian_version" ) # | grep -i release | grep -iE 'centos|redhat'" )
  if vstatus == 0:
    result[ '/etc/d_e_b_i_a_n_version' ] = voutput
  else:
    result[ 'unknown' ] = 'unknown: (cat /etc/d e b i a n_version could not executed at "' + aConnection  + '" ), cause:' + string.join( list( str(voutput) ), ' ' )
  
  if verbose != False: # Set to 1 to Debug
    print "Result with /etc/debian_version",  result
      
  lsbDist = findDistFamily( result, verbose )
  if lsbDist != '':
    return lsbDist
  
  if verbose != False:
    print result
      
  return result[ 'unknown' ] # should never happen ... :)

def findDistFamily( result, verbose=False ):
    for key in result.keys():
      foundDistInValues = getDistFamily( result[ key ], verbose )
      # print "Found in", result[key], foundDistInValues
      if foundDistInValues != '':
          return foundDistInValues
      foundDistInKeys = getDistFamily( key, verbose )
      #print key, foundDistInKeys 
      if foundDistInKeys != '':
          return foundDistInKeys
    return ''
  
def getDistFamily( searchstring, verbose=False ):
  result = ''
  for family in DISTFAMILIES.keys():
    #if verbose != False:
    #  print family
    flavours= DISTFAMILIES[ family ]
    #sprint flavours
    for flavour in flavours:
      if verbose != False:
        print flavour
      #print "flavour in ?", flavour, searchstring
      if string.count( searchstring.lower(), flavour.lower() ) >=1:
        if verbose != False:
          print "Found: ", family
        result = family 
        return result
  return result
    #lsb_release
  #if string.count( lower( seachstring ), "centos" ) >=1 :
  #    return "redhat"
      
  #    pass
  
  
def isNotOwner( host, loginName ):
  dbconn = openMySQLConnection()
  
  ownergroups=getLdapGroupNamesList( loginName )
  
  [ownergroup] = selectData( dbconn, HOSTS, OWNERGROUP, whereConnection( host ) )
  [owneraccount] = selectData( dbconn, HOSTS, OWNERACCOUNT, whereConnection( host ) )
  dbconn.close()
  #print  owneraccount[0]#[0]#[0]

  if owneraccount[0] == loginName:
    return False
  for group in ownergroups:
    if group == ownergroup[0]:
      return False
  return True



def isInLdapGroup( loginName, ldapgroup ):
  for group in getLdapGroupNamesList( loginName ):
    if group == ldapgroup:
      return True
  return False
  
  
def isAdmin( loginName ):
  #TODO LDAP enable:
  return True # isInLdapGroup( loginName, LDAPADMINGROUP )



def getUsersOrderCol( dbconn, loginName, default ):
  if loginName != None:
    result = selectWhereData( dbconn, USERS, SORTCOL, where( USER_LOGINNAME, loginName ) )
  else:
    result = default
  
  if result == "" : 
    result = default 
    
  if result == None : 
    result = default
  
  return result



def getUsersOrderDir( dbconn, loginName, default ):
  if loginName != None:
    result = selectWhereData( dbconn, USERS, SORTDIR, where( USER_LOGINNAME, loginName ) )
  else:  
    result = default 
  if result == "": 
    result = default 
    
  if result == None: 
    result = default 
  
  
  return result

      

def getAllRegisteredHosts( loginName = None ): #, order=UPDATES, direction = ' desc' ):
  ## For DUMP and reload there is no User and of Course no Limit
  if loginName != None:
    limitstart = getUserValue( loginName, MIN_ROW )
    limitstop = getUserValue( loginName, MAX_ROW )
  else:
    limitstart=None
    limitstop=None
  
  if limitstart == None:
    limitstart= str( 0 )
    
  if limitstop == None:
    limitstop='4294967295'
  
  dbconn = openMySQLConnection()
  
  ordercol = getUsersOrderCol( dbconn, loginName, UPDATES )
  orderdir = getUsersOrderDir( dbconn, loginName, ' desc' )
  
  

  
  orderby = "ORDER BY `" + ordercol + "`" + orderdir
  #orderby = "ORDER BY `" + order + "`" + direction
  
  if ( int( limitstart ) >= 0 ) and ( int( limitstop ) > int( limitstart ) ):
    limit = ' LIMIT %s,%s' % ( limitstart, limitstop )
  elif int( limitstart ) >= 0:
    limit = ' LIMIT %s' % ( limitstart )
  else:
    limit = '' 
  
  if loginName==None or isAdmin( loginName ):
    where='' + orderby + limit
  else:
    where="WHERE owneraccount='" + loginName  + "'  OR ownergroup<>'' " + orderby + limit # and getgroupsContains admin 
  connections = selectData( dbconn, HOSTS, CONNECTION, where )
  dbconn.close()
  result = []
  for connection in connections:
    result.append( str( connection[0] ) ) 
  #list( hostlist ) 
    
  return result


#
#
#
def lockConnection( dbconn, connection, aRemoteUser, aRemoteAddress ):
  query = "Update " + HOSTS + \
          " SET " +  LOCKDATE + ' = %s' \
          " WHERE Connection = %s "
  args = (  datetime.now(), connection )          
  result =  executeMySQLArgsQuery( dbconn, query, args )    

  #
  # TODO: 0.11+: migrate to an one line update statement like set (date, host, owner) values ( %s, ... )
  #
  query = "Update " + HOSTS + \
          " SET " +  LOCKHOST + ' = %s' \
          " WHERE Connection = %s "
            
  args = ( aRemoteAddress, connection )
  result =  executeMySQLArgsQuery( dbconn, query, args )
  
  query = "Update " + HOSTS + \
          " SET " +  LOCKOWNER + ' = %s' \
          " WHERE Connection = %s "
            
  args = ( aRemoteUser, connection )
  result =  executeMySQLArgsQuery( dbconn, query, args )
  
  dbconn.commit()

  
def lockConnections( dbconn, connectionList, aRemoteUser, aRemoteAddress ):
  for connection in connectionList:
    lockConnection( dbconn, connection, aRemoteUser, aRemoteAddress)
  
  
def unlockConnection( dbconn, connection, aRemoteUser='', aRemoteAddress='' ):
  query = "Update " + HOSTS + \
          " SET " +  LOCKDATE + ' = %s' \
          " WHERE Connection = %s "
  args = (  None, connection )          
  result =  executeMySQLArgsQuery( dbconn, query, args )    

  query = "Update " + HOSTS + \
          " SET " +  LOCKHOST + ' = %s' \
          " WHERE Connection = %s "
            
  args = ( '', connection )
  result =  executeMySQLArgsQuery( dbconn, query, args )
  
  query = "Update " + HOSTS + \
          " SET " +  LOCKOWNER + ' = %s' \
          " WHERE Connection = %s "
            
  args = ( '', connection )
  result =  executeMySQLArgsQuery( dbconn, query, args )
  
  dbconn.commit()


def unlockConnections( dbconn, connectionList, aRemoteUser='', aRemoteAddress='' ):
  for connection in connectionList:
    unlockConnection( dbconn, connection, aRemoteUser, aRemoteAddress )


def getLockDataOfConnection( dbconn, connection, aRemoteUser='', aRemoteAddress='' ):
  # could be select user, host date from Hosts where 
  lockdate = selectWhereData( dbconn, HOSTS, LOCKDATE, whereConnection( connection ) )
  lockhost = selectWhereData( dbconn, HOSTS, LOCKHOST, whereConnection( connection ) )
  lockuser = selectWhereData( dbconn, HOSTS, LOCKOWNER, whereConnection( connection ) )
  
  return { LOCKDATE: lockdate, LOCKOWNER: lockuser, LOCKHOST: lockhost }

  
def getLockInfoOfConnection( dbconn, connection, aRemoteUser='', aRemoteAddress='' ):
  lockdata=getLockDataOfConnection( dbconn, connection, aRemoteUser, aRemoteAddress )
  lockinfo="Connection " + connection + " locked since " + str( lockdata[LOCKDATE] ) + ' from ' + lockdata[LOCKOWNER] + ' @ ' + lockdata[LOCKHOST]
  return lockinfo


def isLockedConnection( dbconn, connection ):
  result = selectWhereData( dbconn, HOSTS, LOCKDATE, "WHERE Connection='" + connection +"'" )
  return result != None


def isAutoupdateConnection( dbconn, connection ):
  return selectWhereData(dbconn, HOSTS, AUTOUPDATE, "WHERE Connection='" + connection +"'")


def setAutoupdateConnection( dbconn, connection, anAutoFlag=True ):
  query = "Update " + HOSTS + \
          " SET " +  AUTOUPDATE + ' = %s' \
          " WHERE Connection = %s "
  args = (  anAutoFlag, connection )          
  result =  executeMySQLArgsQuery( dbconn, query, args ) 
  dbconn.commit()


def setManualupdateConnection( dbconn, connection, aManualFlag=True ):
  query = "Update " + HOSTS + \
          " SET " +  AUTOUPDATE + ' = %s' \
          " WHERE Connection = %s "
  args = ( not aManualFlag, connection )          
  result =  executeMySQLArgsQuery( dbconn, query, args ) 
  dbconn.commit()


def isEnabledConnection( dbconn, connection ):
  return selectWhereData(dbconn, HOSTS, ENABLED, "WHERE Connection='" + connection +"'")
  

def setEnabledConnection( dbconn, connection, anEnableFlag=True ):
  query = "Update " + HOSTS + \
          " SET " +  ENABLED + ' = %s' \
          " WHERE Connection = %s "
  args = (  anEnableFlag, connection )          
  result =  executeMySQLArgsQuery( dbconn, query, args ) 
  dbconn.commit()
  
  
def setDisabledConnection( dbconn, connection, aDisabledFlag=True ):
  query = "Update " + HOSTS + \
          " SET " +  ENABLED + ' = %s' \
          " WHERE Connection = %s "
  args = ( not aDisabledFlag, connection )          
  result =  executeMySQLArgsQuery( dbconn, query, args )
  dbconn.commit()


def setPingFailCountConnection( dbconn, connection, aPingFailCount=0 ):
  query = "Update " + HOSTS + \
          " SET " +  PINGFAILCOUNT + ' = %s' \
          " WHERE Connection = %s "
  args = ( aPingFailCount, connection )          
  result =  executeMySQLArgsQuery( dbconn, query, args )
  dbconn.commit()


def getPingFailCountConnection( dbconn, aConnection ):
  return selectWhereData( dbconn, HOSTS_TABLE, PINGFAILCOUNT, whereConnection( aConnection ) )


def setLastPingTimeConnection( dbconn, connection, aPingDate=time.ctime() ):
  #query = "Update " + HOSTS + \
  #        " SET `" +  LASTPINGDATE + '` = "%s"' \
  #        " WHERE Connection = %s"
  #args = ( str( aPingDate ), connection )  # str( datetime.now() )
  # TODO:
  #print args, query     
  
  query = "Update `" + HOSTS + "` SET `" +  LASTPINGDATE + '`="' + str( aPingDate ) + '" ' + whereConnection(connection)
  result =  executeMySQLQuery( dbconn, query )
    
  # result =  executeMySQLArgsQuery( dbconn, query, args )
  dbconn.commit()


def getLastPingTimeConnection( dbconn, aConnection ):
  return selectWhereData( dbconn, HOSTS_TABLE, LASTPINGDATE, whereConnection( aConnection ) )


def getUpgradeData( dbconn, connection ):
  result = ""
  rawdata = selectWhereData( dbconn, "Upgrades", "UpdateData", "WHERE Connection='" + connection +"'" )#.decode( 'base64' )
  result = zlib.decompress( rawdata ) 
  return result


def hasUpgradeData( dbconn, connection ):
  result = ""
  rawdata = selectWhereData( dbconn, "Upgrades", "LastUpdate", "WHERE Connection='" + connection + "'" )#.decode( 'base64' )
     
  return rawdata != None



def insertUpgradeData( dbconn, connection, rawdata ):  
  
  createMySQLUpgradeTable( dbconn )
  
  query = "INSERT INTO Upgrades (Connection) VALUES ( '" + connection + "' ) ON DUPLICATE KEY UPDATE LastUpdate='" +     str( datetime.now() ) + "'" #.date()  
  result =  executeMySQLQuery( dbconn, query )
  
  where = "WHERE Connection='" + connection +"'"
  
  
  if isinstance( rawdata, list ):
    plainstring=''  
    for line in rawdata:
      plainstring += line + '\n'
    rawdata=plainstring
    
  updatedata = zlib.compress( rawdata )
  
  
     
  query = "Update Upgrades " \
        "SET UpdateData = %s " \
        "WHERE Connection= %s "
  args = (updatedata, connection)
  result =  executeMySQLArgsQuery( dbconn, query, args )
  
  query = "Update `" + 'Upgrades' + "` SET `" +  'LastUpdate' + '`="' + str( datetime.now() ) + '" ' + where
  result =  executeMySQLQuery( dbconn, query )
  
  dbconn.commit()
  
  # dblogObj( dbconn, rawdata, 1, 'insertUpgradeData-raw' )
  # dblogObj( dbconn, updatedata, 1, 'insertUpgradeData-compressed' )

  return len(updatedata)



def insertUpgradeDatas( dbconn, dataDict={} ):
  for connection in dataDict.keys():
    insertUpgradeData( dbconn, connection, dataDict[connection] )
    updateData( dbconn, HOSTS, LASTUPDATE, str( datetime.now() ), whereConnection( connection ) )



def dbdolog( dbconn, anIpaddress='127.0.0.1', anUserid=0, anUsername='N/A', anAction='None', aStatus=0, aData='None', aTimestamp = datetime.now() ):
  query = "INSERT INTO " + LOG + \
          '(' + IPADDRESS + ', ' + USERID + ', ' + USERNAME + ', ' + ACTION + ', ' + STATUS + ', ' + DATA + ', ' + TIMESTAMP + ')' \
          "VALUES (%s, %s, %s, %s, %s, %s, %s)"
          
  args = ( anIpaddress, anUserid, anUsername, anAction, aStatus, aData, aTimestamp )          
  result =  executeMySQLArgsQuery( dbconn, query, args )
  dbconn.commit()
  

def dolog( anIpaddress='127.0.0.1', anUserid=0, anUsername='N/A', anAction='None', aStatus=0, aData='None', aTimestamp = datetime.now() ):
  dbconn=openMySQLConnection()
  dbdolog( dbconn, anIpaddress, anUserid, anUsername, anAction, aStatus, aData, aTimestamp )
  dbconn.close()


  
def dblogObj( dbconn, anObject, aStatus=0, aData="N/A", aTimestamp = datetime.now() ):
  Ipaddress = os.environ.get( "REMOTE_ADDR", "N/A" )
  Username  = os.environ.get( 'REMOTE_USER', UNKNOWN_LSUS_USER )
  ## if running outside BROWSER Session UserID = UID of Current PID
  if Username == UNKNOWN_LSUS_USER:
    Userid = os.getuid()
    Username = pwd.getpwuid( Userid ).pw_name
  else:
    Userid = pwd.getpwnam( Username ).pw_uid
  Action=str( anObject )
  dbdolog( dbconn, Ipaddress, Userid, Username, Action, aStatus, aData, aTimestamp )
  
def logObj( anObject, aStatus=0, aData="N/A", aTimestamp = datetime.now() ):
  dbconn=openMySQLConnection()
  dblogObj( dbconn, anObject, aStatus, aData, aTimestamp )
  dbconn.close()
  
def log( anObject, aStatus=0, aData="N/A", aTimestamp = datetime.now() ):
  logObj( anObject, aStatus, aData, aTimestamp )  



def executeMySQLArgsQuery( cn, query, args ): 
  result=None  
  
  cursor=cn.cursor()
  
  #print "Query", query 
  cursor.execute( query, args )
  if cursor.with_rows:
    result=result.rowcount
  else:
    result = 0
  #print "1", result
  cursor.close()
  #print "2", result
  #cn.close()
  
  #  print "r:", result.rowcount
  return result
  
def executeMySQLQuery( cn, query ): 
  result=0 #None  
  
  cursor=cn.cursor()
  # 
  cursor.execute( query )
  if cursor.with_rows:
    result=result.rowcount
  else:
    result = 0
  #print "1", result
  cursor.close()
  #print "2", result
  #cn.close()
  
  #  print "r:", result.rowcount
  return result


def deleteTableData( cn, table, where ):
  query = "Delete from `" + table + "`" + where
  result =  executeMySQLQuery( cn, query )
  cn.commit()  
  return result
  
#
#
def updateData( cn, table,  key, value, where ):
  result = 0 #""
  query='# FAIL' 
  try:
    query = "Update `" + table + "` SET `" +  key + '`="' + value + '" ' + where
  except:
    print "Update query failed with table:", table, ', key:', key, ', value:', value, ', where:', where, '.' 
  #print query

  # TODO:
  # TODO: 0.11+ : make usage of  query with args or with string split / list map join
  try:
  # print result
    result = executeMySQLQuery( cn, query )
  #
    cn.commit()
  except:
    dblogObj(cn, query, -1, "Failed " + where)

    mail( "Failed query: " + str( query ) + ' ' + where, "!!!LSUS Failure - see log", DEBUG_EMAIL_ADDRESS )
  
  return result 

def updateDatas( dbconn, table, key, values ):
  for host in values.keys():
    updateData( dbconn, table, key, values[ host ], whereConnection( host ) ) 
    
  

def selectWhereData( cn, table, key, where ):
    query = "SELECT `" + key + "` FROM `" + table + "` " + where
    cursor=cn.cursor()
    cursor.execute( query ) # 
    #result=[]#None
    onefetched = cursor.fetchone()
    if onefetched is not None:
      result = onefetched[0]
    else:
      result = None
    #for value in cursor:
        # result.append((value))
        #result = "{}".format( str( value ) )
    # result = executeMySQLQuery( cn, query )
    #print query + "=" + str( result )
    cursor.close()
    return result #cursor.fetchone()[0] #result #[0] )# cursor




def getConnectionsOfDist( cn, dist = DEBIAN ):
  # list( itertools.chain.from_iterable( x )
  return list( itertools.chain.from_iterable( executeQueryFetchAll( cn, 'SELECT ' + CONNECTION + ' FROM ' + HOSTS + whereDist( dist ) ) ) )

def getUpdatablesForDist( cn, dist = DEBIAN ):
  qry='SELECT ' + CONNECTION + ' FROM ' + HOSTS + whereDist( dist ) + ' AND ' + ENABLED + "='1' " + ' AND ' + AUTOUPDATE + "='1'"
  return list( itertools.chain.from_iterable( executeQueryFetchAll( cn, qry ) ) )
  
def getAllEnabledOfDist( cn, dist=DEBIAN ):
  qry='SELECT ' + CONNECTION + ' FROM ' + HOSTS + whereDist( dist ) + ' AND ' + ENABLED + "='1'"
  return list( itertools.chain.from_iterable( executeQueryFetchAll( cn, qry ) ) )

def getAllEnabledOfDistOrdered( cn, dist=DEBIAN, orderby='' ):
  qry='SELECT ' + CONNECTION + ' FROM ' + HOSTS + whereDist( dist ) + ' AND ' + ENABLED + "='1' " + orderby
  return list( itertools.chain.from_iterable( executeQueryFetchAll( cn, qry ) ) )

def executeQueryFetchAll( cn, query ):
  #result=[]
  cursor=cn.cursor()
  cursor.execute( query ) # 
  return cursor.fetchall()

def selectData( cn, table, key, clause="", DEBUG=False ):
    query = "SELECT " + key + " FROM `" + table + "` " + clause
    
    # dbdolog(dbconn, anIpaddress, anUserid, anUsername, anAction, aStatus, aData, aTimestamp)
    #print '<code>', query, '</code>'
    #log( query, 's' )
    
    cursor=cn.cursor()
    result=[]
    try:
      cursor.execute( query ) #
      result = cursor.fetchall()#[1]
      status = 0
    except:
      status = 1
      (x,y,z)=sys.exc_info()
      # dblogObj( cn, (x,y,z), aStatus=status, aData="sys.exc_info()" )
      result.append( ( str( x ).replace( '<', '&lt;' ).replace( '>', '&gt;' ), y, str( z ).replace( '<', '&lt;' ).replace( '>', '&gt;' ) ) )
      #result.append( string.replace( str( x ), '<', '&lt;' ).replace('>', '&gt;').join('') )
      #result.append(   )
      #result.append( ev )
      #result.append( ts )
      
    if DEBUG:   
      dblogObj( cn, query, aStatus=status, aData="DEBUG: getConfigselectData" )
    #if cursor.with_rows:
    #  print "rowcount:", cursor.rowcount
    #for value in cursor:
        # result.append((value))
        #result = "{}".format( str( value ) )
    # result = executeMySQLQuery( cn, query )
    # print '<code>', query, '</code>' #+ "=" + str( result )
    #cursor.close()
    return result #cursor.fetchone()[0] #result #[0] )# cursor

def selectAll( cn, table, key, col, value ):
    # TODO: Check if used somewhere
  cursor=cn.cursor()
 
  cursor.execute( """Select Connection From Hosts Where (Connection = %s)""",( value, ) )
  return cursor.fetchall()




def getFileContent( fullfilePath ):
    
    openedFile = open( fullfilePath )
     
    lines = openedFile.readlines()
    openedFile.close()
    result=''
    for line in  lines:
      result += string.strip( line ) + '\n'
    
    return result
  
  
def getFileContentList( fullfilePath ):
    
    openedFile = open( fullfilePath )
     
    lines = openedFile.readlines()
    openedFile.close()
    result=[]
    for line in  lines:
      result.append( string.strip( line ) ) 
    
    
    return result




def getFileContents( fullfilePrefixPath, listOfFilenames ):
  result = {} 
  for filename in listOfFilenames:
    try:   
      result[ filename ] = getFileContent( os.path.join( fullfilePrefixPath, filename )  )
    except:
      print "Error reading ", fullfilePrefixPath, filename
      handleException( str(__name__) + ' in getFileContents()'  )
  return result

  
def getFileContentsList( fullfilePrefixPath, listOfFilenames ):
  result = {} 
  for filename in listOfFilenames: 
    try: 
      result[ filename ] = getFileContentList( os.path.join( fullfilePrefixPath, filename )  )
    except:
      print "Error reading ", fullfilePrefixPath, filename
      handleException( str(__name__) + ' in getFileContentsList()' )
  return result

  
def getColumnList( cn, tableName='Hosts', schema='' ):
  if schema == '':
    schema=getDataBaseName()
  
  query = "SELECT COLUMN_NAME from INFORMATION_SCHEMA.COLUMNS where table_name='" + tableName + "' and table_schema='" + schema +"';"
  cursor=cn.cursor()
  cursor.execute( query ) # 
    
  result = list( itertools.chain.from_iterable( cursor.fetchall() ) ) #[
  #print result
  return result # list( itertools.chain.from_iterable( result ) ) #result



def getBusinessUsers(dbconn):
  result=[]
  businessUsers = selectData( dbconn, HOSTS, "DISTINCT " + OWNEREMAIL )
  for userdata in businessUsers:
    #print type( userdata )
    for (user) in userdata:
      if user != None and user != '':
        result.append( user )
  return result


#
#
#
def dropDatabase( connection, databasename ):
  query = 'drop database `' + databasename + '`'  
  return executeMySQLQuery( connection, query )


#
#
#
def createDatabase( connection, databasename, ifNotExists=False ):
  if ifNotExists:
    ifNotExists=' if not exists '
  else: 
    ifNotExists=''
  query = 'create database ' + ifNotExists + '`' + databasename + '`'  
  return executeMySQLQuery( connection, query )


#
#
#
def createMySQLUpgradeTable( cn, tableName='Upgrades' ):
    query = "CREATE TABLE IF NOT EXISTS `" + tableName + "` (" + \
    "  `Connection` varchar(64) NOT NULL," \
    "  `LastUpdate` datetime, " \
    "  `UpdateData` blob, "  \
    "  PRIMARY KEY (`Connection`)"  + \
    ") ENGINE=InnoDB" 
    #print "query: <", query , ">"
    return executeMySQLQuery( cn, query )
  
def createMySQLPackagesTable( cn, tableName="Packages" ):
   # "CREATE TABLE `" + tableName + "` (`name` varchar(40) NOT NULL) Engine=InnoDB" ) 
    query = "CREATE TABLE IF NOT EXISTS `" + tableName + "` (" + \
    "  `Connection` varchar(64) NOT NULL," \
    "  `Name` varchar(128) NOT NULL," + \
    "  `Version` varchar(64)," + \
    "  `Architecture` varchar(48)," + \
    "  `Description` TEXT," + \
    "  `Status` varchar(128)," +  \
    "  `Distribution` varchar(128)," + \
    "  PRIMARY KEY (`Connection`,`Name` )"  \
    ") ENGINE=InnoDB" 
    #print "query: <", query , ">"
    
    #" INDEX ( `Connection`, `Name` )" + \
    return executeMySQLQuery( cn, query )


def createMySQLLogTable( cn, tableName = LOG ):
  query = "CREATE TABLE IF NOT EXISTS `" + tableName + "` (" + \
    "  `Id` MEDIUMINT NOT NULL AUTO_INCREMENT," + \
    "  `Ipaddress` varchar(40) NOT NULL," + \
    "  `Userid` BIGINT UNSIGNED," + \
    "  `Username` varchar(32)," + \
    "  `Timestamp` varchar(32)," + \
    "  `Action` TEXT," +  \
    "  `Status` INTEGER," + \
    "  `Data` TEXT," + \
    "  PRIMARY KEY (`Id`)" \
    ") ENGINE=InnoDB" 
    #print "query: <", query , ">"
  return executeMySQLQuery( cn, query )



def createMySQLUsersTable( cn, tableName = USERS ):
  query = "CREATE TABLE IF NOT EXISTS `" + tableName + "` (" + \
    "  `loginname` varchar(64) NOT NULL, " + \
    "  `rwmode` bool, " + \
    "  `firstlogin` datetime, "    + \
    "  `lastlogin` datetime, "    + \
    "  `ownergroup` varchar(60), " + \
    "  `updatetime` datetime, " + \
    "  `checktime` datetime, " + \
    "  `sortcol` varchar(32), " + \
    "  `sortdir` varchar(6), " + \
    "  `MIN_ROW` integer unsigned null, " + \
    "  `MAX_ROW` integer unsigned null, " + \
    "  PRIMARY KEY (`loginname`)" + \
    ") ENGINE=InnoDB"
  #print "query: !!", query , "!!"
  return executeMySQLQuery( cn, query )


def createMySQLHostsTable( cn, tableName= HOSTS_TABLE ):
  executeMySQLQuery( cn, # "CREATE TABLE `" + tableName + "` (`name` varchar(40) NOT NULL) Engine=InnoDB" ) 
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
    ") ENGINE=InnoDB" )
  
  ## TODO: Insert last ping data fields
  ## TODO:
  ## TODO: see update to apply.update_to 0.9.py
   
  
  
#    AUTOUPDATE="autoupdate"
#    INFORMOWNER="informowner"
#    OWNEREMAIL="owneremail"
#    ENABLED = "enabled"
  
  # 'Connection', 'Hostname', 'Kernel-Release', 'Kernel-Version', 'Uptime', 'Boottime', '# Updates', 'Last Check Time'
  # lsusupdateuser@testhost, 'testhost', 3.13.0-49-generic,
  # 81-Ubuntu SMP Tue Mar 24 19:29:48 UTC 2015, # 64
  # up 22 weeks, 4 days, 21 hours, 59 minutes, # 64
  # 2015-03-26 14:32:19

# TODO: 

def getServerName():
  if socket.gethostname().find('.')>=0:
    name=socket.gethostname()
  else:
    name=socket.gethostbyaddr(socket.gethostname())[0]    
  return name
  

def getUsersList():
  cn = openMySQLConnection()
  loginNames = selectData( cn, USERS, USER_LOGINNAME, '' )
  cn.close()
  return loginNames

def getUser( loginname ):
  cn = openMySQLConnection()
  userData = selectData( cn, USERS, '*', 'where ' + USER_LOGINNAME + ' = ' + loginname  )
  cn.close()
  return userData

def hasUser(  loginname ):
  return getUser != None

def getUserValue( loginname, aDateFieldName  ):
  cn = openMySQLConnection()
  userdate= selectWhereData( cn, USERS, aDateFieldName, 'WHERE ' + USER_LOGINNAME + ' = "' + loginname + '"' )
  cn.close()
  return userdate

def getUserLastLogin( loginname ):
  return getUserValue( loginname, USER_LASTLOGIN )

def getUserFirstLogin( loginname ):
  return getUserValue( loginname, USER_FIRSTLOGIN )

def getUserRWMode( loginname ):
  return getUserValue( loginname, USER_RWMODE )

def setUserValue( loginname, KEY, value ):  
  dbconn = openMySQLConnection()
  query = "Update " + USERS + \
          " SET " + KEY + ' = %s' \
          " WHERE " +  USER_LOGINNAME +  " = %s "
  args = ( value, loginname )
  executeMySQLArgsQuery( dbconn, query, args ) 
  dbconn.commit()

def setUserRWMode( loginname, mode ):
  setUserValue( loginname, USER_RWMODE, mode ) 
  
def setUserSortCol(  loginname, val ):
  setUserValue( loginname, SORTCOL, val )
  
def setUserSortDir(  loginname, val ):
  setUserValue( loginname, SORTDIR, val )
  


  
def insertUserInDB( dbconn, loginname ):
  #cn = openMySQLConnection()
  query = 'INSERT INTO ' + USERS + '(' + USER_LOGINNAME + ',rwmode,firstlogin ) VALUES ( "' + loginname + '", false,"'+ str( datetime.now() ) +'" ) ON DUPLICATE KEY UPDATE ' + USER_LASTLOGIN + "='"  +     str( datetime.now() ) + "'"
  result =  executeMySQLQuery( dbconn, query )
  dbconn.commit() 
  
  query = "Update " + USERS + \
          " SET " +  USER_LASTLOGIN + ' = %s' \
          " WHERE " +  USER_LOGINNAME +  " = %s "
  args = ( str( datetime.now() ), loginname )          
  executeMySQLArgsQuery( dbconn, query, args )
  
   
  dbconn.commit() 
  dbconn.close()
  return result

def insertUser( loginname ):
    return insertUserInDB( openMySQLConnection(), loginname )


def loadTemplateReplaceData( aTemplateName, aKVDict={} ):
  #result=''
  template=loadTemplate(aTemplateName)
  
  for key in aKVDict.keys():
    template=template.replace( '${' + key + '}', aKVDict[ key ] )
    
  
  return template
  

def loadTemplate( aTemplateName ):
  result=''
  template = open( os.path.join( getBaseDir(), aTemplateName ) )
  listoflines=template.readlines()
  template.close()  
  for line in listoflines:
    result += line
  return result



def getBaseDir():
  binpath=os.path.dirname( os.path.realpath( __file__ ) )
  return os.path.realpath( os.path.join( binpath, ".." ) )



def getDatafolder( namedSubfolder=None, DEBUG=False ):
  result=""
  
  if namedSubfolder:
    result = os.path.join( getBaseDir(), DATAFOLDERNAME, namedSubfolder )
  else:
    result = os.path.join( getBaseDir(), DATAFOLDERNAME )
  
  if DEBUG:
      print "getDatafolder() returns: >", result, '<'      
  return result


def getDatafolderOld( datafoldername = DATAFOLDERNAME ):
  return os.path.join( getBaseDir(), datafoldername )
  #return getNamedDataFolder( datafoldername, None )


###
# Gets the default config dir
###
def getConfDir():
  # binpath=os.path.dirname( os.path.realpath( __file__ ) )  
  return os.path.realpath( os.path.join( getBaseDir(), CFGDIRNAME ) )


###
# Gets the full configuration-file pathname
###
def getConfigFilePath():
  return os.path.join( getConfDir(), CFGFILENAME )


###
# Gets the full configuration-file pathname
###
def getLdapConfigFilePath():
  return os.path.join( getConfDir(), LDAPCFGFILENAME )


def getLdapCfg():  
  config=ConfigParser.ConfigParser()
  config.read( getLdapConfigFilePath() )  
  host = config.get( CFGSECTLDAP, CFGKEYLDAPHOST ).decode( B64 )
  bind = config.get( CFGSECTLDAP, CFGKEYLDAPBIND ).decode( B64 )
  name = config.get( CFGSECTLDAP, CFGKEYLDAPNAME ).decode( B64 )
  passfile = config.get( CFGSECTLDAP, CFGKEYLDAPPWFILE ).decode( B64 )
  # NON Existing Key throws an exception!
  # dummy = config.get( CFGSECTDB, CFGKEYDBUSER+'_x' ) thr  
  return { CFGKEYLDAPHOST: host, CFGKEYLDAPBIND: bind, CFGKEYLDAPNAME: name, CFGKEYLDAPPWFILE: passfile  }


###
# Write the (initial) database config 
###


def writeLdapConfig():

  cfg = ConfigParser.RawConfigParser()
  cfg.add_section( CFGSECTLDAP )
  cfg.set( CFGSECTLDAP, CFGKEYLDAPHOST, LDAP_AUTH_SERVER.encode( B64 ) )
  cfg.set( CFGSECTLDAP, CFGKEYLDAPBIND, LDAP_BIND_BASEDN.encode( B64 ) )
  cfg.set( CFGSECTLDAP, CFGKEYLDAPNAME, LDAP_USER_NAME.encode( B64 ) )
  cfg.set( CFGSECTLDAP, CFGKEYLDAPPWFILE, LDAP_PASSWD_FILE.encode( B64 ) ) # at least not directly human readable ;-)
  cfg.add_section( '.' )
  cfg.set( '.', 'written.datetime.now', datetime.now()  )
  with open( getLdapConfigFilePath(), 'wb' ) as configfile:
    cfg.write( configfile )
  configfile.close()


def myInput( mytext, myentry_text  ):
  
  
  result = Entry( text=mytext, entry_text=myentry_text )
  return result


def getInputDatabaseConfig( config = None, host = False, user = False, passwd = False, database = False ):
  
  if config == None:
    config = getEmptyDataBaseConfig()
  
  
  if host == True:
    config[ CFGKEYDBHOST ]  = myInput( "host $> ", config[ CFGKEYDBHOST ] )
  if user == True:
    config[ CFGKEYDBUSER ]  = myInput( "user $> ",  config[ CFGKEYDBUSER ] )
  if passwd == True:
    config[ CFGKEYDBPASS ]  = myInput( "pass $> ", config[ CFGKEYDBPASS ] )
  if database == True:
    config[ CFGKEYDBNAME ]  = myInput( "database $> ",  config[ CFGKEYDBNAME ])
  
  return config
  
  


###
# Write the (initial) database config 
###
def writeDBConfig():
  cfg = ConfigParser.RawConfigParser()
  cfg.add_section( CFGSECTDB )
  cfg.set( CFGSECTDB, CFGKEYDBHOST, 'mysqlserver.my.lan.local' )
  cfg.set( CFGSECTDB, CFGKEYDBNAME, 'lsus' )
  cfg.set( CFGSECTDB, CFGKEYDBUSER, 'lsusdba' )
  cfg.set( CFGSECTDB, CFGKEYDBPASS, 'lsusdba1'.encode( B64 ) ) # at least not dicrectly human readable ;-)
  cfg.add_section( '.' )
  cfg.set( '.', 'written.datetime.now', datetime.now()  )
  with open( getConfigFilePath(), 'wb' ) as configfile:
    cfg.write( configfile )
  configfile.close()


###
# Write the given  database config 
###
def writeDBConfig( dbconfig ):
  cfg = ConfigParser.RawConfigParser()
  cfg.add_section( CFGSECTDB )
  
  
  cfg.set( CFGSECTDB, CFGKEYDBHOST, dbconfig[CFGKEYDBHOST] )
  cfg.set( CFGSECTDB, CFGKEYDBNAME, dbconfig[CFGKEYDBNAME] )
  cfg.set( CFGSECTDB, CFGKEYDBUSER, dbconfig[CFGKEYDBUSER] )
  cfg.set( CFGSECTDB, CFGKEYDBPASS, dbconfig[CFGKEYDBPASS].encode( B64 ) ) # at least not dicrectly human readable ;-)
  cfg.add_section( '.' )
  cfg.set( '.', 'written.datetime.now', datetime.now()  )
  with open( getConfigFilePath(), 'wb' ) as configfile:
    cfg.write( configfile )
  configfile.close()
  




def getEmptyDataBaseConfig( DEBUG=False ):
  result = {
            CFGKEYDBHOST: None, 
            CFGKEYDBNAME: None, 
            CFGKEYDBUSER: None, 
            CFGKEYDBPASS: None            
            }
  if DEBUG:
    print 'getEmptyDataBaseConfig()', '\n', result
  
  return result


 
def createDatabaseConfig( dbhost, dbuser, dbpass, dbname=None, DEBUG=False ):
  result = getEmptyDataBaseConfig()
  
  result[CFGKEYDBHOST] = dbhost
  result[CFGKEYDBNAME] = dbname
  result[CFGKEYDBUSER] = dbuser
  result[CFGKEYDBPASS] = dbpass # base64.b64decode( dbpass ) 
  #x=utf # decode( B64 )
  
  if DEBUG:
    print createDatabaseConfig(),'\n', result
     
  return result 
 
 

def getLocalDatabaseConfig(  dbuser='lsusdba', dbpass='lsusdba1', dbname='lsus', DEBUG=False ):
    return createDatabaseConfig( 'localhost',  dbuser, dbpass, dbname, DEBUG )
  
###
#
###
def getDataDaseConfig( DEBUG=False ):  
  result = getEmptyDataBaseConfig( DEBUG )
  
  config=ConfigParser.ConfigParser()
  config.read( getConfigFilePath() )  
  result[CFGKEYDBHOST] = config.get( CFGSECTDB, CFGKEYDBHOST )
  result[CFGKEYDBNAME] = config.get( CFGSECTDB, CFGKEYDBNAME )
  result[CFGKEYDBUSER] = config.get( CFGSECTDB, CFGKEYDBUSER )
  result[CFGKEYDBPASS] = config.get( CFGSECTDB, CFGKEYDBPASS ).decode( B64 )
  # NON Existing Key throws an exception!
  # dummy = config.get( CFGSECTDB, CFGKEYDBUSER+'_x' ) thr
  
   #{ CFGKEYDBHOST: host, CFGKEYDBNAME: db, CFGKEYDBUSER: user, CFGKEYDBPASS: passwd  }
  if DEBUG:
    print result
    
  return result


def getDataBaseName():
  # connConfig = 
  return getDataDaseConfig()[CFGKEYDBNAME]

    
def openMySQLConnection(  ):
    #global DBCON
    conn=None
    
    connConfig = getDataDaseConfig()
    
    try:
      conn=mysql.connector.connect( user=connConfig[CFGKEYDBUSER], password=connConfig[CFGKEYDBPASS], host=connConfig[CFGKEYDBHOST], database=connConfig[CFGKEYDBNAME] )  
      #print conn, conn.is_connected()
    except mysql.connector.Error as err:
      if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print( "Something is wrong with your user name or password" )
      elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print( "Database does not exist" )
      else:
        print( 'MysqlError:' )
        print( err )
        
      print ' while trying to connect to database', connConfig[CFGKEYDBNAME], 'at', connConfig[CFGKEYDBHOST]
    except:
           #except:

      etype, evalue, etb = sys.exc_info()

      #evalue = etype("Cannot openMySQLConnection: %s" % evalue)
          
      #print etype, evalue, etb
    #  print conn, conn.is_connected()
    #  conn.close()
    return conn

def getMysqlError():
  return mysql.connector.Error


def checkSSH( anUser, aHost ):
  return checkSSHConnection(  anUser + '@' + aHost )


def jsprintdocln( ahtmlString ):
  print '<script type="text/javascript">document.writeln( "' +   ahtmlString + '" )</script>'
  #print ahtmlString
    

def checkSSHConnection( aConnection ):
  
  """ Check if a batch ssh connection can be established: 
  ssh -o BatchMode=yes $asshconnection pwd 
  """
  
  #result = commands.getstatusoutput( 'sudo -u ' + LSUSUPDATEUSER + ' ssh -o BatchMode=yes "' + anUser +'@' + aHost + '" "' + "echo -n 'successful established ssh with ' && whoami" + '"'  )
  
  ### ! result = commands.getstatusoutput( 'sudo -u ' + LSUSUPDATEUSER + ' ssh -o BatchMode=yes "' + anUser +'@' + aHost + '" "' + "echo -n \`whoami\` && echo -n @ && hostname" + '"'  )
  
  result = commands.getstatusoutput( 'sudo -u ' + LSUSUPDATEUSER + ' ssh -o BatchMode=yes -o StrictHostKeyChecking=no "' + aConnection + '" "' + "pwd" + '"'  )
  #jsprint( 'document.writeln( "" )' )
  jsprintdocln ('<ul><li>ssh check result: <b>' + str( result ) + '</b></li>') 
  sys.stdout.flush()
  return result


def testSudoConnection( aConnection, detailed=False  ):
  
  sudocommand="sudo -n -l env"
  if detailed:
    sudocommand="sudo -n -l"
  cmd = 'sudo -u ' + LSUSUPDATEUSER + ' ssh -o BatchMode=yes -o StrictHostKeyChecking=no -tt ' + aConnection + ' "' + sudocommand + '"'
  
  return commands.getstatusoutput( cmd )
  
  
  
   #print getCommandStatusValue( ' -o BatchMode=yes -o StrictHostKeyChecking=no ' + aConnection, "sudo -n -l env" )


def testsudo( username, hostname, detailed=False ):
  return testSudoConnection( username + '@' + hostname )


def checkPing( ahostname ):
  result, txt = commands.getstatusoutput( "ping -c 1 " + ahostname )
  #print  ahostname, result
  #print txt
  return result

def getPingOutput( ahostname ):
  result, txt = commands.getstatusoutput( "ping -c 1 " + ahostname )
  #print  ahostname, result
  #print txt
  return result, txt

def checkPingConnection( aConnection ):
  connection = string.split( aConnection, "@" )
  # username = connection[0]
  hostname = connection[1]
  result, txt = getPingOutput( hostname ) 
  return result, txt 


def getPingablesList( aConnectionList, verbose=False ):
  result = []
  for connection in aConnectionList:
    res, txt = checkPingConnection( connection ) 
    if res == 0:
      
      result.append( connection )
    else:
      if verbose:
        print 'Skipped Non-pingable: ', connection,  txt
        sys.stdout.flush()
      
  return result


def getPingablesListAndHandleDead( dbconn, aConnectionList, verbose=False ):
  result = []
  
  temptime = {}
  
  for connection in aConnectionList:
    res, txt = checkPingConnection( connection ) 
    if res == 0:
      
      result.append( connection )
      #
      #
      # if pigfailcount > 0

      setPingFailCountConnection( dbconn, connection ) #aPingFailCount)
      setLastPingTimeConnection( dbconn, connection, datetime.now() ) #, time.ctimeaPingDate)
      setPingFailReasonConnection( dbconn, connection, '' )
      # 

      
    else:
      handleDeadHostConnection( dbconn, connection, res, txt, verbose )     
  return result



def getNotPingableList( aConnectionList ):
  result = []
  for connection in aConnectionList:
    res, txt = checkPingConnection( connection )
    if res > 0:
      result.append( connection )
  return result


def handleDeadHostConnection( dbconn, aConnection, result, txt, verbose=False ):
  if verbose:
    print 'Skipped not pingable', aConnection
    sys.stdout.flush()
  #connection = string.split( aConnection, "@" )
  #username = connection[0]
  #hostname = aConnection[1]
  #return handleDeadHost( dbconn, hostname, result, txt, verbose )
  pingfailcount =  getPingFailCountConnection( dbconn, aConnection )
  #selectWhereData
  pingfailreason = getPingFailReasonConnection( dbconn, aConnection )
  
  # (x)=pingfailcount[0]
  print 'pingfailcount[0]', pingfailcount, "'"#  pingfailcount[0] , aConnection
  #print x
  
  # sys.exit( 222)
  if pingfailcount == None or pingfailcount == NoneType :
    pingfailcount = 0
           
  pingfailcount = int( pingfailcount )
  
  # Increment 
  pingfailcount  += 1
  
  setPingFailCountConnection( dbconn, aConnection, pingfailcount )# aPingFailCount)updateData(dbconn, HOSTS_TABLE, PINGFAILCOUNT, str( pingfailcount ), whereConnection( aConnection ) )
  
  if pingfailcount == 1:
    
    setPingFailReasonConnection( dbconn, aConnection, txt )
    
  else:
    
    setPingFailReasonConnection( dbconn, aConnection, txt + '+, ' +  pingfailreason )
    
  if pingfailcount > MAX_PINGFAILCOUNT_BEFORE_DISABLE:
    setDisabledConnection( dbconn, aConnection )
    # updateData(dbconn, HOSTS_TABLE, ENABLED, False, whereConnection( aConnection ) )
    body    = "REASON: " + txt + '+, ' +  pingfailreason + ' - Last successful Ping: ' + str( getLastPingTimeConnection(dbconn, aConnection) )  
    Subject = "LSUS Server '" + getServerName()  + "' has been DISABLED HOST: '" + aConnection + "' because pingfail count was greater than MAX_PINGFAILCOUNT of " + MAX_PINGFAILCOUNT_BEFORE_DISABLE
    toList   = LSUS_ADMIN
    
    mail( body, Subject, toList )
      
    #TODO: inform user, admin, etc
    #Set enabled to false

#
#
#
#def handleDeadHost( dbconn, ahostname, result, txt, verbose=False ):
  # TODO:
  
 
  
  #1. GetPingFailCount.
  #2. 
  
  #reason = txt
    
def setPingFailReasonConnection( dbconn, aConnection, txt ):

  updateData( dbconn, HOSTS_TABLE, PINGFAILREASON, txt, whereConnection( aConnection ) ) 
  
def getPingFailReasonConnection( dbconn, aConnection ):
  return selectWhereData( dbconn, HOSTS_TABLE, PINGFAILREASON, whereConnection( aConnection ) )
  

def getCommandValue( hostConnection, aCommand, DEBUG=False, Status=False ):
    command='sudo -u '+ LSUSUPDATEUSER + ' ssh ' + hostConnection + ' "' + aCommand + '"'
    
    logObj( command )
    
    if Status == False:
      result=commands.getoutput( command )
    else:
      (status,result) =commands.getstatusoutput( command )
    
    if DEBUG:
      if Status == False:
        print "getCommandValue() :", hostConnection, aCommand, command, "result: >", result, '&lt;<br><br><br>'
        sys.stdout.flush()
      else:
        print "getCommandValue() :", hostConnection, aCommand, command, "status, result: >", status, ',', result, '&lt;<br><br><br>'
        
    if Status == False:
      return result
    else:
      return result, status 
  
  
  

def getTTyCommandValue( hostConnection, aCommand ):
    return commands.getoutput( 'sudo -u '+ LSUSUPDATEUSER + ' ssh -tt ' + hostConnection + ' "' + aCommand + '"' )

def defaultParse():
  parser = pssh.option_parser()  
  defaults = common_defaults( timeout = PSSH_TIMEOUT )
  parser.set_defaults(**defaults)
  opts, args = parser.parse_args()
  return opts, args




  


def sudo_pssh( hosts, cmdline, opts, web=True ):
    if opts.outdir and not os.path.exists( opts.outdir ):
        os.makedirs(opts.outdir)
    if opts.errdir and not os.path.exists( opts.errdir ):
        os.makedirs(opts.errdir)
    if opts.send_input:
        stdin = sys.stdin.read()
    else:
        stdin = None
    manager = Manager(opts)
    for host, port, user in hosts:
        cmd = [ '/usr/bin/sudo', '-u', LSUSUPDATEUSER, 'ssh', '-tt', host, '-o', 'NumberOfPasswordPrompts=1',
                '-o', 'SendEnv=PSSH_NODENUM PSSH_HOST']
        if opts.options:
            for opt in opts.options:
                cmd += ['-o', opt]
        if user:
            cmd += ['-l', user]
        if port:
            cmd += ['-p', port]
        if opts.extra:
            cmd.extend(opts.extra)
        if cmdline:
            cmd.append(cmdline)
        if web == True:
          t = WebTask( host, port, user, cmd, opts, stdin )
        else:
          t = Task( host, port, user, cmd, opts, stdin )
        manager.add_task(t)
    try:
        statuses = manager.run()        
    except FatalError:
        return 1 ### sys.exit(1)

    for status in statuses:
      if status < 0:
        # At least one process was killed.
        return 3 ### sys.exit(3)
    # The any builtin was introduced in Python 2.5 (so we can't use it yet):
    #elif any(x==255 for x in statuses):
    for status in statuses:
        if status == 255:
            return 4 ### sys.exit(4)
    for status in statuses:
        if status != 0:
            return 5 ### sys.exit(5)
          
    return statuses


  


def execPssh( command, connectionsList, sudo = False, dataFolder = 'data', web=True ):
  
  opts, args = defaultParse()# pssh.parse_args() 
  opts.outdir = dataFolder
  opts.print_out = web
  
  hosts=[]
  for connection in connectionsList:
    hosts.extend( psshutil.parse_host_string( str( connection ), default_user=opts.user ) )    
  
  
  if len( hosts ) > 0:
    if sudo == True:
      
      sudo_pssh( hosts, command, opts, web )
      
    else:      
      pssh.do_pssh( hosts, command, opts ) 
  
  return 

def getPsshResultDict( command, connectionList, dataFolderName, web=True ):  
  execPssh( command, connectionList, True, dataFolderName, web )
  return getFileContents( dataFolderName, connectionList )


def getPsshResultDictList( command, connectionList, dataFolderName, web=True ):  
  if not web:
    print "Executing command:", command
  execPssh( command, connectionList, True, dataFolderName, web )
  result = getFileContentsList( dataFolderName, connectionList )
  return result  




def getAsyncSubprocessValueList( hostConnection, aCommand, web, datafoldername, DEBUG=False ):
  
  
  singleHost=[ hostConnection ]
  
  
  #singleHost.append( hostConnection )
  if DEBUG:
    print "Starting PSSH with >", aCommand, singleHost, True, datafoldername, web, '<'
  
  execPssh( aCommand, singleHost, True, datafoldername, web )  # updatecommands[ dist ], connections[ dist ]
  
  
  # sudo_pssh( hosts, cmdline, opts ):
  
  datafileName = os.path.join( datafoldername, str( hostConnection ) )
  
  if os.path.exists( datafileName ):
  
    rawdata = getFileContentList( datafileName )
    
  else:
     print 'getAsyncSubprocessValueList() datafileName ',  datafileName, 'does not exist!!'
     return None
  
  return rawdata 

def getSubprocessValue( aCommandLine, web = True ):
  # global runningProcs
   
  #commandline=  [ '-u', LSUSUPDATEUSER, 'ssh -tt ' + hostConnection + ' \"' + aCommand + '\"' ]
  result = []
  #print str(commandline)
  if web:
    print shlex.split( aCommandLine )
  proc = Popen( shlex.split(  aCommandLine ), stdout = PIPE, stderr = STDOUT, bufsize = 4096 )
  
  retcode=0
  #runningProcs[ str( commandline) ] = proc
  #u7nstdout = proc.communicate()[0]
  
  while   True:
    retcode = proc.poll()
    #print 'proc', proc.stdout# , u7nstdout
    #f = open()
    #.r
    try:
      raw = proc.stdout.readline()
      buff = str( raw ).strip()
      result.append( buff )
      if web:
        print buff, '<br>'
      sys.stdout.flush()
      
      time.sleep(.1)
    except:
      
      break
    
    
    #print u7nstdout, u7nstderr
    #retcode = proc.poll()
    if retcode is not None: # Process finished.
      #del runningProcs[ str(commandline) ]
      #u7nstdout, u7nstderr = proc.communicate()
      #result.append(u7nstdout)
      #result.append(u7nstderr)
      
      #del proc
      
      break
    #else:
      
      #print '.'
      
      #time.sleep(.1)
      
    #result.append(u7nstdout)
      #continue
  
  if retcode != 0:
    """Error handling."""
    #result.append(stdout)
    handle_results(proc.stdout, proc.stderr)
    
  #print result    
  return result

def getAsyncSubprocessValueOld( hostConnection, aCommand, web = True ):
  return getSubprocessValue( '/usr/bin/sudo -u ' + LSUSUPDATEUSER + ' ssh -tt ' + hostConnection + ' \"' + aCommand + '\"' )


def handle_results(arg1, arg2):
  print "Return Code != 0: results:", arg1, arg2 
  raise Exception( arg1, arg2 )


def installAptShowVersions( ahostConnection ):  
  # install necessary apt-show version    
  if whichExists( ahostConnection, WHICH  ):  
    whichPath = getWhichPath( ahostConnection, WHICH )
    if not filePathExists( ahostConnection, whichPath , "apt-show-versions"):
      print "<li>Trying to install required <b>apt-show-version</b><br>Check datafolder/apt-show-versions/ " + ahostConnection + " - logfile and install manually, if this has been failed.</li><br>"
      installCommand="sudo apt-get update && sudo apt-get -y install apt-show-versions"
      getAsyncSubprocessValueList( ahostConnection, installCommand, True, getDatafolder('apt-show-versions') )



def getAptShowVersionsVersionOld( ahostConnection ):   
    results = string.split( getCommandValue( ahostConnection, "apt-show-versions -h|head -1" ), " " )
    version = string.join( string.split( results[1], '.' )[1:], '.' ) # [v, 0, 20, 1 ]   
    return version



def getAptShowVersionsVersion( ahostConnection, DEBUG=False ):
  
  if DEBUG:
    print 'DEBUG getAptShowVersionsVersion for ',  ahostConnection
  VersionString = getAsyncSubprocessValueList( ahostConnection, 'apt-show-versions -h|head -1', False, getDatafolder( APT_SHOW_VERSIONS, DEBUG ), DEBUG ) # [0]
  if DEBUG:
    print 'DEBUG getAptShowVersionsVersion got ',  VersionString
  
  #print 'VersionString ', VersionString, "'", ahostConnection, string.join( string.split( VersionString[1], '.' )[1:], '.' )
  # TODO: make this easier i.e with cut -d -f 1 and maybe regex / check the usage of the result | call of this method
  VersionString = VersionString[0]
  if DEBUG:
    print 'DEBUG getAptShowVersionsVersion idx 0 ',  VersionString
  
  version = string.join( string.split( VersionString[1], '.' )[1:], '.' )
  #rint "'", version, "'"

  if string.strip(version ) == '':
    version = string.split( string.join( string.split( VersionString, '.' )[1:], '.' ) )[0]
  
  #print 'VV', version
  return version #string.join( string.split( VersionString[1], '.' )[1:], '.' ) # [v, 0, 20, 1 ] 
  
   
  

      
def insertHostIntoHosts( dbconn, host ):    
    query = "INSERT INTO Hosts (Connection) VALUES ( '" + host + "' ) ON DUPLICATE KEY UPDATE ScanTime='" +     str( datetime.now() ) + "'" #.date() 
    executeMySQLQuery( dbconn, query )
    dbconn.commit()
    
def deleteHostFromHosts( dbconn, host ):
    query = "Delete from Hosts " + whereConnection( host ) # (Connection) VALUES ( '" + host + "' ) ON DUPLICATE KEY UPDATE ScanTime='" +     str( datetime.now() ) + "'" #.date() 
    # TODO: LOG query, either here or in the executeMySQLQuery() method
    executeMySQLQuery( dbconn, query )
    dbconn.commit()
    
def deleteHostFromPackages( dbconn, host ):
    query = "Delete from " + PACKAGES + ' ' + whereConnection( host )
    # TODO: LOG query, either here or in the executeMySQLQuery() method
    executeMySQLQuery( dbconn, query )
    dbconn.commit()

    
def insertPackageNamesIntoHostPackages( dbconn, connection, family, DEBUG=False ):
  if family == DEBIAN:    
    insertDebianPackageIntoPackages( dbconn, connection, getDebianPatches( connection, DEBUG ), DEBUG )
    
  elif family == SUSE:
    insertSUSEPackageIntoPackages( dbconn, connection, getSUSEPatches( connection ) )
    
  elif family == REDHAT:
    if DEBUG:
      print "DEBUG!! insertPackageNamesIntoHostPackages of RedHat: ", connection
    patches = getREDHATPatches( connection )
    if DEBUG:
      print "Found RedHat Patches on connection: ", connection, patches
    insertREDHATPackageIntoPackages( dbconn, connection, patches )      



def getDebianPatches( host, DEBUG=False ):
    
    rawresults = string.split( getCommandValue( host, "apt-show-versions", DEBUG ), '\n' )
    
    # result = string.split( getCommandValue( ahostConnection, "apt-show-versions -b | cut -d / -f 1" ), '\n' )
    
    #print result #getCommandValue( ahostConnection, "apt-show-versions -b | cut -d : -f 1" )
    return rawresults # result # getCommandValue( ahostConnection, "apt-show-versions -b | cut -d : -f 1" )

    
def insertDebianPackageIntoPackages( dbconn, host, patchesList, DEBUG=False ):
      
      try:
        aptshowVersionVersion = getAptShowVersionsVersion( host, DEBUG )
      except:
        ## ASSUME 0.22
        aptshowVersionVersion='0.22'
      
      hostquery=''
      
      for packagedata in patchesList: #getDebianPatches( host ):
        try:
          # SAMPLE:
          #  xul-ext-ubufox:all/trusty-security 3.0-0ubuntu0.14.04.1 upgradeable to 3.1-0ubuntu0.14.04.1
          #  xz-utils:amd64/trusty 5.1.1alpha+20120614-2ubuntu2 uptodate
          
          ##  zerofree:amd64/trusty 1.0.2-1ubuntu1 uptodate
          ##  zlib1g:amd64/trusty 1:1.2.8.dfsg-1ubuntu1 uptodate
          
          # print packagedata, len( packagedata )
          
          datalist = string.split( packagedata ) # [get, all, white, spaces]
          distsplit = string.split( datalist[ 0 ], "/" )  #  [ xz-utils:amd64, trusty ]
          archsplit = string.split( distsplit[ 0 ], ":" ) # [ xz-utils, amd64 ]
          try:
            arch = archsplit[1]
          except:
            arch ="n/a"
          try:
            dist = distsplit[1]
          except:  
            dist = "n/a"            
         # updateClause = " ON DUPLICATE KEY UPDATE Architecture=VALUES( `" + arch + "` ), age=VALUES(age)" datalist[1]
          if aptshowVersionVersion < '0.21': # Handle old Versions of apt-show-versions
            updateClause = " ON DUPLICATE KEY UPDATE Architecture='" + arch + "', Status='" + datalist[1] + "', Version='" + string.join( datalist[2:] ) + "', Distribution='" + dist + "'"                
            hostquery = "INSERT INTO `Packages` ( Connection, Name, Architecture, Status, Version, Distribution ) VALUES ( '" + host + "', '" + distsplit[0] + "', '" + arch + "', '" + datalist[1] + "', '" + string.join( datalist[2:] ) + "', '" + dist + "' )" + updateClause  
          else: # for latest apt-show-version
            updateClause = " ON DUPLICATE KEY UPDATE Architecture='" + arch + "', Version='" + datalist[1] + "', Status='" + string.join( datalist[2:] ) + "', Distribution='" + dist + "'"            
            hostquery = "INSERT INTO `Packages` ( Connection, Name, Architecture, Version, Status, Distribution ) VALUES ( '" + host + "', '" + distsplit[0] + "', '" + arch + "', '" + datalist[1] + "', '" + string.join( datalist[2:] ) + "', '" + dist + "' )" + updateClause

          # TODO: LOG Query. See deleteHostFromPackages() above

          executeMySQLQuery( dbconn, hostquery )
        
        except:
          print "Error in:", host, aptshowVersionVersion, packagedata, len(datalist), datalist, distsplit, len(distsplit) , archsplit, len(archsplit)
          #print hostquery
          etype, evalue, etb = sys.exc_info()
          evalue = etype("Cannot insert debian : %s" % evalue )
          
          print etype, evalue, etb

      
      dbconn.commit()
      

def getSUSEPatches( host ):
    result = []
    rawdata = string.split( getCommandValue( host, 'env LANG=en_US zypper -n lp' ), '\n')
    
    for line in rawdata:
      if line.count('|') >= 2 and line.count( 'Repository' ) == 0 and line.count( 'Name' ) == 0 and line.count( 'Category' ) == 0: 
          result.append( line.strip() )    
    
    
    return result



def insertSUSEPackageIntoPackages( dbconn, host, patchesList ):
  
    print patchesList
      
    for patch in patchesList: # getSUSEPatches( host ):
      #print patch      
      try:
        rawPatchData = string.split( patch, '|' ) # 'openSUSE-13.1-Update | openSUSE-2015-98  | 1       | security    | needed | Security update for patch'
      
        patchname = string.strip( rawPatchData[ 1 ] )
        version = string.strip( rawPatchData[ 2 ] )
        repos  = string.strip( rawPatchData[ 0 ] )
        status = string.strip( rawPatchData[ 4 ] )
        if len(rawPatchData) >= 6:
          desc = string.replace( string.strip( rawPatchData[ 5 ] ), "'", '' )
        else:
          desc=''
        category = string.strip( rawPatchData[ 3 ] )
      
        updateClause = " ON DUPLICATE KEY UPDATE Architecture='" + category + "', Version='" + version + "', Status='" + status + "', Distribution='" + repos + "', Description='" + desc + "'"
      
        hostquery = "INSERT INTO `Packages` ( Connection, Name, Architecture, Version, Status, Distribution, Description ) VALUES ( '" \
        + host + "', '" + patchname + "', '" + category + "', '" + version + "', '" + status + "', '" + repos + "', '" + desc + "' )" + updateClause
        executeMySQLQuery( dbconn, hostquery )
      except:      
        etype, evalue, etb = sys.exc_info()
        evalue = etype("Cannot insert suse : %s" % evalue)
          
        print etype, evalue, etb
    dbconn.commit()    



def getREDHATPatches( connection ):
    result=[]                                                                                   # yum check-update returns 100 even if there is not update
    rawdata = string.split( getCommandValue( connection, 'env LANG=en_US yum -yt check-update ; test $? -eq 100 -o $? -eq 0' ), '\n')
    
    yumspacelinefound=False
    
    #linescount = len( rawdata )
    #idx = 0
    
    for line in rawdata:
      line = string.strip( line )
      if yumspacelinefound == False:
        if line !=  '':
          #print "XXX", line
          continue
      if line == '':
        yumspacelinefound = True
        continue
        
      if string.strip( line ) == "Obsoleting Packages":
          break
      
      #print "!> ", line 
      result.append( line ) 
            
    return result    
    

def insertREDHATPackageIntoPackages( dbconn, host, patchesList ):
    updateClause = ""
    hostquery = ""
    for patch in patchesList: ### getREDHATPatches( host ):
      #if string.strip( patch ) == "Obsoleting Packages":
      #    break
      try:
        rawPatchData = string.split( patch )
        name = string.strip( rawPatchData[0] )
        try:
          version = string.strip( rawPatchData[1] )
        except:
          version = ""
        try:
          repos = string.strip( rawPatchData[2]  )
        except:
          repos = ""
        
        updateClause = " ON DUPLICATE KEY UPDATE Version='" + version + "', Distribution='" + repos + "'"
        
        hostquery = "INSERT INTO `Packages` ( Connection, Name, Version, Distribution ) VALUES ( '" \
        + host + "', '" + name + "', '" + version + "', '" + repos + "' )" + updateClause
        executeMySQLQuery( dbconn, hostquery )
      except:      
        print "Error in insertREDHATPackageIntoPackages: ", host, rawPatchData
        print hostquery, '\n\n'
        print patch, '\n\n'
        print ''
        print rawPatchData, '\n\n'
        print patchesList
        print '\n', patch, '\n'
        etype, evalue, etb = sys.exc_info()
        evalue = etype("Cannot insert redhat : %s" % evalue)
          
        print etype, evalue, etb
        try:
          dbconn.commit()
        except:
          etype, evalue, etb = sys.exc_info()
          evalue = etype("Cannot commit redhat data : %s" % evalue)
    dbconn.commit()    


def insertPackages( dbconn, HostPackagesDict, dist ):
  #HostPackagesDict = {}
  
  for host in HostPackagesDict.keys():
    # insertPackages 
    if dist == DEBIAN:
      insertDebianPackageIntoPackages( dbconn, host,  HostPackagesDict[ host ] )
    elif dist == SUSE:
      insertSUSEPackageIntoPackages( dbconn, host,  getSUSEPatches( host ) )
    elif dist == REDHAT:
      insertREDHATPackageIntoPackages( dbconn, host, getREDHATPatches( host ) ) 


def doPsshInsertPackagesPerDist( dbconn, pingableHostsPerDistList, dist ):

  ## sudo env LANG=en_US zypper refresh > /dev/null 2>&1 && zypper -n lp
  print 'Executing: ', listpackagesCommand[ dist ]
  
  resultDict = getPsshResultDictList( listpackagesCommand[ dist ], pingableHostsPerDistList, getDatafolder( 'packages' ), web=False )  
  
  insertPackages( dbconn, resultDict, dist )
  
  
  # print resultDict
  ### TODO: resultDict = getPsshResultDict(  command, pingableHostsPerDistList, getDatafolder( key ), web=False )


def buildimageurl( distfamilyImageName ):

    result = '<img style="vertical-align: middle;" src="../res/images/' + distfamilyImageName + '.png"> ' + distfamilyImageName
    
    return result


##
# Build and returns a Selectbox HTML Form Fragment for the given HostConnection
#  
def buildSelectForm( aConnection ):
  #
  connection = string.split( aConnection, "@" )
  username = connection[0]
  hostname = connection[1]
  
  FormName = 'selection'
  ActionPath = 'action.py'
   
  form='<form id="' + 'form.' + aConnection + '.' + FormName + '" name="' + FormName + '" action="' + ActionPath + '" method="get" target="' + LSUS_CONTENT_AREA + '">'   
  _form='</form>'   # " + getUserName() + " 
  
  # confirmationtext="' " + getUserName( capitalize=True, Jscript=True ) + ": Would you like to " + ActionToConfirmText + " " + aConnection +  " ?'"
  # hiddenaction='<input type="hidden" name="action" value="' + ActionValue + '">'
  
  input = '<input type="checkbox" id="'+ aConnection + '">'
  
  result = form + input + _form
  
  return result


def getHostProperiesDict( host, distroFamily, updatetime=None ):
    result = {}
    
    # """ syscommands={} """    
    result[ "Connection" ]   = host    
    result[ SCANTIME ] =  str( datetime.now() )
    
    
    
    #if upgradeConnection == False: # Means Initial Value
    #  result[ LASTUPDATE ] = str( datetime.fromtimestamp(0) )
    #else: # After a real APT-GET dist-upgrade was made put in the current timestamp
    if updatetime != None:
    #  updatetime = datetime.now()  
      result[ LASTUPDATE ] = str( updatetime )
    
    
    result[ DISTRIBUTIONFAMILY ] = distroFamily
    
    distdict = sqlfordist[ distroFamily ] 
    
    for command in distdict.keys():
        
        result[ command ] = getCommandValue( host, distdict[ command ] )
        
        
    if distroFamily == REDHAT: ## TODO: supress double call // Yum Needs an redundant Extra handling
       result[ "Updates" ] = str( len( getREDHATPatches( host ) ) )
    #result[ "Hostname" ]      = getConfig.getCommandValue( ahostConnection, "hostname" ) 
    #result[ "KernelRelease" ] = getConfig.getCommandValue( ahostConnection, "uname -r" ) 
    #result[ "KernelVersion" ] = getConfig.getCommandValue( ahostConnection, "uname -v" ) 
    #result[ "Uptime" ]   = getConfig.getCommandValue( ahostConnection, "uptime -p" ) 
    #result[ "Boottime" ] = getConfig.getCommandValue( ahostConnection, "uptime -s" ) 
    #result[ "Updates" ]  = getConfig.getCommandValue( ahostConnection, "sudo apt-get -qq -s -y dist-upgrade | grep -i -c ^Inst" )
    
    return result
      
def updateConnection( dbconn, host, DistroFamily, isEnabled=1, isAutoUpdate=1, ownerEMail=None, stage=UPDATE, web=True ):
    result = []
   
    # lastUpdateTimeInDB = selectWhereData( dbconn, HOSTS, LASTUPDATE, whereClause )
    if stage==NONE:
      lastUpdateTimeInDB = NONE
    elif stage == INITIAL:
      lastUpdateTimeInDB = datetime.fromtimestamp(0)
    else:
      lastUpdateTimeInDB=datetime.now()
    #print "lastUpdateTimeInDB", str( int( lastUpdateTimeInDB ) ) 
    hostProperies = getHostProperiesDict( host, DistroFamily, lastUpdateTimeInDB )      
    if stage == INITIAL: # Set Initial Values 
      updateData( dbconn, HOSTS,  ENABLED, str( int( bool( isEnabled ))), whereConnection( host ) )
      updateData( dbconn, HOSTS,  AUTOUPDATE, str( int( bool( isAutoUpdate ))), whereConnection( host ) )
    
    if ownerEMail != None:
      updateData( dbconn, HOSTS,  OWNEREMAIL, ownerEMail, whereConnection( host ) )
        
    for hostPropery in hostProperies.keys():
        
        result.append( updateData( dbconn, HOSTS,  hostPropery, hostProperies[ hostPropery ], whereConnection( host ) ) )
        if stage == None:
          if web == False:
            if hostPropery == 'Updates':
              print 'On', DistroFamily, host, hostProperies[ hostPropery ], "Updates are available"
              
        
    return result   
  
  
  
def doPsshUpdateConnectionsPerDist( dbconn, pingableHostsPerDistList, dist ):
  # for host in pingableHostsPerDistList:
  for key in sqlfordist[ dist ].keys():
    command = sqlfordist[ dist ][ key ]
    #for key in getConfig.sqlfordist[ dist ].keys():
    # print dist, key, command # sqlfordist[ dist ][ key ]
    print "Executing:", command 
    resultDict = getPsshResultDict(  command, pingableHostsPerDistList, getDatafolder( key ), web=False )
    
     
    updateDatas( dbconn, HOSTS, key, resultDict )
    
    # result[ SCANTIME ] =  str( datetime.now() )
  for host in pingableHostsPerDistList:
    
      #updateDatas( dbconn, HOSTS, SCANTIME, resultDict )
    print 'Setting ', SCANTIME, 'of', host
    updateData( dbconn, HOSTS,  SCANTIME, str( datetime.now() ), whereConnection( host ) )


####
#  Gets a Dictionary with the Updates(-Available) Field with the Host as Key 
#         readed from the Database HOSTS table
#####
def getUpdatesAvailableDict( dbconn, hosts ):  
  updatesDict={}
  for host in hosts:
    updatesDict[ host ] = selectWhereData( dbconn, HOSTS, UPDATES, whereConnection( host ) + ' order by ' + UPDATES )    
  return updatesDict

##
# Get the DistributionFamily for the given Connection
##
def getDistOfConnection( dbconn, aConnection ):
  return selectWhereData( dbconn, HOSTS, DISTRIBUTIONFAMILY, whereConnection( aConnection ) )



####    
# Sends a Mail with given Body and Subject -> toList
#### 
def mail( body = "Test", Subject = "TestSubject", toList = LSUS_ADMIN ):
  cc = LSUS_ADMIN
  msg = MIMEText( body, 'html' )
  msg['Subject'] = Subject
  msg['From'] = SMTP_MAIL_FROM
  msg['To'] = toList
  #msg['CC'] = cc
  msg['Reply-To'] = SMTP_MAIL_REPLYTO
  smtp = smtplib.SMTP( SMTP_MAIL_SERVER )
  fromMail = SMTP_MAIL_FROM_ADDRESS
  
  smtp.sendmail( fromMail, toList, msg.as_string(), )
  
  smtp.close()


def getRemoteAddress():
  return os.environ.get( "REMOTE_ADDR", "N/A" )

def getLoginName(): 
  userlogin=os.environ.get( 'REMOTE_USER', UNKNOWN_LSUS_USER)
  
  if string.count( userlogin, '\\' ) > 0: # DISMISS AD DOMAIN PREFIX
    #os.environ.
    userlogin = string.split(userlogin, '\\')[1]
  
  return userlogin


def getUserName( capitalize=False, Jscript=False ):
  username = getLoginName() 
  
  #TODO: LDAP enable
  return username
    
  if username == UNKNOWN_LSUS_USER:
    return "unknown"
  else:
    if Jscript==False:
  
      return "'" + getLdapDisplayName( username ) + "' (" + username + ')' 
    else:
      return getLdapDisplayName( username ) + " (" + username + ')' 
  #  fullname =  pwd.getpwnam( username ).pw_gecos
  #  if fullname!='':
  #    return "'" + fullname + "' (" + username + ')'
  #  else:
  #    if capitalize:
  #      return username.capitalize()
  #    else:
  #      return username




  
def getLdapUserAttribs( sAMAccountName, Filter=''  ):
  #host=LDAPHOST
  #bind=LDAPBIND
  #name=LDAPNAME
  #pwfl=LDAPPASS 
  
  ldapcfg=getLdapCfg()
  #
  # Cut the AD Domain away...
  if sAMAccountName.count('\\')>0:
    sAMAccountName=sAMAccountName.split( '\\' )[1]    
  
  command = "ldapsearch -o ldif-wrap=no -x -h " + ldapcfg[CFGKEYLDAPHOST] + " -b '" + ldapcfg[CFGKEYLDAPBIND] + "' -s sub -D '" + ldapcfg[CFGKEYLDAPNAME] + "' -y " + ldapcfg[CFGKEYLDAPPWFILE] + " '(&(objectclass=User)(samAccountName=" + sAMAccountName + "))'" + Filter
  #log( command , 0, 'ldapsearch') #print 'command: ', command
  return commands.getoutput( command )

def getLdapUserAttr( sAMAccountName, attrib ):
  Filter =  ' ' + attrib + "|grep " + attrib +": |sed -e 's/"+ attrib +"://g'" 
  return getLdapUserAttribs( sAMAccountName, Filter )

def getLdapDisplayName( sAMAccountName ):  
  return string.strip( getLdapUserAttr( sAMAccountName, 'name' ) ) 
  
def getLdapMailAddress( sAMAccountName ):
  return string.strip( getLdapUserAttr( sAMAccountName, 'mail' ) )

def getLdapGroups( sAMAccountName, separator='\n' ):
  return string.join( getLdapGroupNamesList( sAMAccountName ), separator )

def getLdapGroupNamesList( sAMAccountName ):
  result=[]
  for groupLine in getLdapGroupsList( sAMAccountName ):
    for groupToken in string.split(groupLine, ','):
      kv = string.split( groupToken, '=' )
      if len( kv ) == 2 and kv[ 0 ] == 'CN':
        result.append( kv [ 1 ] )
  return result 

def getLdapGroupsList( sAMAccountName ):
  result=[]
  groups=getLdapUserAttr( sAMAccountName, 'memberOf' )
  for line in string.split( groups, '\n' ):
    result.append( string.strip( line ) )
  return result


def buildButtonForm( aConnection, distfamily, ActionValue, ActionToConfirmText, FormName, ActionPath ):
  connection = string.split( aConnection, "@" )
  username = connection[0]
  hostname = connection[1]
   
  form='<form id="' + 'form.' + aConnection + '.' + FormName + '" name="' + FormName + '" action="' + ActionPath + '" method="get" target="' + LSUS_CONTENT_AREA + '">'   
  _form='</form>'   # " + getUserName() + " 
  confirmationtext="' " + getUserName( capitalize=True, Jscript=True ) + ": Would you like to " + ActionToConfirmText + " " + aConnection +  " ?'"
  hiddenaction='<input type="hidden" name="action" value="' + ActionValue + '">'
  hiddendist='<input type="hidden" name="' + DISTRIBUTIONFAMILY + '" value="' + distfamily + '">'  # action="doupgrade">
  hiddenuser='<input type="hidden" name="hostname" value="' + hostname + '">'
  hiddenhost='<input type="hidden" name="username" value="' + username + '">'
  button='<button type="button" onclick="if( confirm( '+  confirmationtext + ' ) ) form.submit();" name="upgrade" value="'+ aConnection + '">' + ActionValue + '</button>'      
 
  result= form + hiddenaction + hiddendist + hiddenuser + hiddenhost +  button + _form
    
  return result

def buildOwnerEmailInputForm( username, hostname, owneremail ):
  form='\n<form id="' + 'form.' + username+'@'+hostname + '.' + OWNEREMAIL + '" name="' + OWNEREMAIL + '" action="' + 'gethostdata.py' + '" method="get" target="' + LSUS_CONTENT_AREA + '">\n'   
  _form='</form>\n'   # " + getUserName() + " 
  # confirmationtext="' " + getUserName( capitalize=True ) + ": Would you like to change " + OWNEREMAIL + " of " + username+'@'+hostname +  " ?'"
  hiddenaction = '  <input type="hidden" id="action" name="action" value="' + OWNEREMAIL + '">\n'  
  hiddenuser   = '  <input type="hidden" id="hostname" name="hostname" value="' + hostname + '">\n'
  hiddenhost   = '  <input type="hidden" id="username" name="username" value="' + username + '">\n'
  hiddencurrentuser='  <input type="hidden" id="currentuser" name="currentuser" value="' + getUserName( capitalize=True ) + '">\n'
  hiddenoldEmail ='  <input type="hidden" id="' + OWNEREMAIL + '_old' + '" name="' + OWNEREMAIL + '_old' + '" value="' + owneremail + '">\n'
  
  input=' <label>New EMail: <input type="email" id="' + OWNEREMAIL + '" name="' + OWNEREMAIL + '" value="' + owneremail + '"></label>\n'
  
  button=' <button type="button" onclick="confirmAndCommitAddressChange()" name="upgrade" value="'+ 'aConnection' + '">' + 'Submit' + '</button>\n'      
  reset=' <button type="reset">Reset</button>\n'

  result= form + hiddenaction + hiddenuser + hiddenhost +hiddencurrentuser + hiddenoldEmail + input + button + '&nbsp;' + reset + _form
    
  return result

# Creates and returns an option list of the LDAP users groups, the user is in, to be able construct a selection area
def getownergrouplist( loginName ):
  itsgrouplist = getLdapGroupNamesList( loginName )     
  ownergrouplist=''
  for group in itsgrouplist:
    ownergrouplist += '<option value="' + group + '">'
  return ownergrouplist

def getOwnerGroupDatalist( loginName, datalistid ):
  return '<datalist id="' + datalistid + '">' + getownergrouplist( loginName ) + '</datalist>'
      

def buildOwnergroupInputForm( username, hostname, group ):
  form='\n<form id="' + 'form.' + username+'@'+hostname + '.' + OWNERGROUP + '" name="' + OWNERGROUP + '" action="' + 'gethostdata.py' + '" method="get" target="' + LSUS_CONTENT_AREA + '">\n'   
  _form='</form>\n'   # " + getUserName() + " 
  # confirmationtext="' " + getUserName( capitalize=True ) + ": Would you like to change " + OWNEREMAIL + " of " + username+'@'+hostname +  " ?'"
  hiddenaction = '  <input type="hidden" id="groupaction" name="action" value="' + OWNERGROUP + '">\n'  
  hiddenuser   = '  <input type="hidden" id="hostname" name="hostname" value="' + hostname + '">\n'
  hiddenhost   = '  <input type="hidden" id="username" name="username" value="' + username + '">\n'
  hiddencurrentuser='  <input type="hidden" id="currentuser" name="currentuser" value="' + getUserName( capitalize=True ) + '">\n'
  hiddenoldEmail ='  <input type="hidden" id="' + OWNERGROUP + '_old' + '" name="' + OWNERGROUP + '_old' + '" value="' + group + '">\n'
  
  inputfield=' <label>New Group: <input type="search" list="ownergroups" id="' + OWNERGROUP + '" name="' + OWNERGROUP + '" value="' + group + '">' + getOwnerGroupDatalist(  getLoginName(), 'ownergroups') + '</label>\n'
  
  
  button=' <button type="button" onclick="confirmAndCommitGroupChange()" name="upgrade" value="'+ 'aConnection' + '">' + 'Submit' + '</button>\n'      
  reset=' <button type="reset">Reset</button>\n'

  result= form + hiddenaction + hiddenuser + hiddenhost +hiddencurrentuser + hiddenoldEmail + inputfield + button + '&nbsp;' + reset + _form
    
  return result


###
# Builds a simple HTML Input Form - skeletton
#
def buildSimpleInputForm( username, hostname, owneremail ):
  result =''
  return result





def doUpgrade( dbconn, connection, distfamily ):
        if isLockedConnection( dbconn, connection ):
          lockdata=getLockDataOfConnection( dbconn, connection )
          print "<h2>Connection", connection, "is already running and locked since", lockdata[LOCKDATE], 'from', lockdata[LOCKOWNER], '@', lockdata[LOCKHOST], "</h2>" 
        else:
          
          print "<h1>Starting UPGRADE of:", connection, '</h1><br><font color="red"><b>Please wait for the Back-Link which appears below on finish!</b></font><br>'
          pingresult, txt = checkPingConnection( connection )
          dblogObj( dbconn, pingresult, pingresult, "status of ping: " + connection + " before gethostdata.doUpgrade()"  )          
          if pingresult == 0:
            print "Ping successfull, locking connection<br>"
            
            lockConnection( dbconn, connection, getLoginName(), os.environ.get( "REMOTE_ADDR", "127.0.0.1") )
            sys.stdout.flush()
            
            if 1:
              #if distfamily == REDHAT:
                rawresult = getAsyncSubprocessValueList( connection, upgradecommand[ distfamily ] , True, getDatafolder( _UPGRADE ) )
      
              #elif distfamily==SUSE:
              #  rawresult = getAsyncSubprocessValueList( connection, , True,  getDatafolder( _UPGRADE ) )
      
              #elif distfamily==DEBIAN:
              #  rawresult = getAsyncSubprocessValueList( connection, , True, getDatafolder( _UPGRADE ) )
          
            print "Wrote", insertUpgradeData( dbconn, connection, rawresult ), "bytes in database.<br>"
            print "<code>End:", distfamily, '</code><br>' 
            sys.stdout.flush() 
            updateConnection( dbconn, connection, distfamily, stage=UPDATE )
            insertPackageNamesIntoHostPackages( dbconn, connection, distfamily )
            unlockConnection( dbconn, connection )
            print "<code>Updated Database for", connection, '</code><br>'
          else:
            print "could not ping: ", connection, txt
          sys.stdout.flush() 

###
# 
# Does a apt-get upgrade, zypper patch or on redhat a yum update
# for the given connection and family
#
###
def doUpdate( dbconn, connection, distfamily, web=True ):
        rawresult = []
        if web:
          print "<h1>Starting === upDate of connection:", connection, 'Family: ', distfamily, '<br><br>Please wait for the Back-Link which appears below on finish!</h1>'
        
        
        if isLockedConnection( dbconn, connection ):
          lockdata=getLockDataOfConnection( dbconn, connection )
          if web:
            print "<h2>Connection", connection, "is already running and locked since", lockdata[LOCKDATE], 'from', lockdata[LOCKOWNER], '@', lockdata[LOCKHOST], "</h2>" 
        else:
          
          
          pingresult, txt = checkPingConnection( connection )
          dblogObj( dbconn, pingresult, pingresult, "status of ping: " + connection + " before gethostdata.doUpgrade()"  )          
          if pingresult == 0:
            if web:
              print "Ping successfull, locking database<br>"
            user=getLoginName()
            lockConnection( dbconn, connection, user, os.environ.get( "REMOTE_ADDR", "N/A") )
            sys.stdout.flush()
          
          
          
            
          
            if web:
              print "<code>Locked:", connection, '</code><br>'
              sys.stdout.flush()
            
          
            DEBUG=1
            
            
            


            
            if 1:
            
              #if distfamily == REDHAT:
              if DEBUG:
                  dblogObj( dbconn, connection + updatecommand[ distfamily ] )
              sys.stdout.flush()
              rawresult = getAsyncSubprocessValueList( connection, updatecommand[ distfamily ], web, getDatafolder( _UPDATE ) )
      
              #elif distfamily==SUSE:
             #   if DEBUG:
              #    dblogObj( dbconn, connection + " sudo zypper --non-interactive --no-gpg-checks --gpg-auto-import-keys patch" )
               # sys.stdout.flush()
              #  rawresult = getAsyncSubprocessValueList( connection, "sudo zypper --non-interactive-include-reboot-patches --non-interactive --no-gpg-checks --gpg-auto-import-keys patch", web, getDatafolder( _UPDATE ) )
      
              #elif distfamily==DEBIAN:
             #   if DEBUG:
               #   dblogObj( dbconn, connection + ' export DEBIAN_FRONTEND=noninteractive && sudo apt-get -q -y -V $1 -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade' )
               # sys.stdout.flush()
               # rawresult = getAsyncSubprocessValueList( connection, 'export DEBIAN_FRONTEND=noninteractive && sudo apt-get -q -y -V $1 -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade', web, getDatafolder( _UPDATE ) )
              
              bytes_written = insertUpgradeData( dbconn, connection, rawresult )
              if web:
                print "Wrote", bytes_written, "bytes update-info data in TO database!!<br>"
              else:
                print "Wrote", bytes_written, 'bytes update-info data'
                dblogObj( dbconn, 'do_update::insertUpgradeData( ' + str( connection ) + ')' , bytes_written, 'bytes_written' )
            if web:
              print "<code>End:", connection, '</code><br>' 
              sys.stdout.flush() 
          
            updateConnection( dbconn, connection, distfamily, stage=UPDATE )
            if web:
              print 'Checked for updates of ', connection, '<br>'
              sys.stdout.flush()
          
            insertPackageNamesIntoHostPackages( dbconn, connection, distfamily )
            if web:
              print 'Insert Packes in database', connection ,'<br>'
              sys.stdout.flush()
          
            unlockConnection( dbconn, connection )
            if web:
              print 'Unlock', connection ,'<br>'
              sys.stdout.flush()
            if web:          
              print "<code>Completed", connection, '<br>' 
              sys.stdout.flush()  
          
          else:
            if web:
              print "could not ping: ", connection, '<br>'
          
          return rawresult

def handleException( origin = '' ):
  etype, evalue, etb = sys.exc_info()
  # evalue = etype( "Cannot exec: %s" % evalue )
          
  print etype, evalue, etb, 'in:', origin


def asciiremapSimpleString( remapplist ):
  remapped = ''
  for item in remapplist:
    remapped += item.encode( 'ascii', 'ignore' ) + ', '
  
  remapped=remapped.rstrip(' ')
  remapped=remapped.rstrip(',')
  
  return remapped


def asciiremapSimpleHTML_LI( remapplist ):
  remapped = '<ol>'
  for item in remapplist:
    remapped += '<li>' + item.encode( 'ascii', 'ignore' ) + '</li>'
  
  return remapped + '</ol>'
##
#
# MAIN
#
##  
if __name__ == '__main__':

    # readDataFile()
    
    if ( len( sys.argv ) >= 2 ) and ( sys.argv[1] == "test" ):
      print getFullProduct(), getVersion()
      
      #writeDBConfig()
      #print getDataDaseConfig()
      
      
      #writeLdapConfig()
      #print getServerName()
      
      print checkSSHConnection('lsussudouser@testhost.my.lan.local')

      #print detectDistro( 'lsussudouser@testhost.my.lan.local' )

      testconfig = getInputDatabaseConfig()
      
      print "testconfig", testconfig
      
      sys.exit(0)
      
      #mail('<h1>Hallo<h1> Marc <a href="http://dev-host.local">dev-host.local</a>')
      #dolog( anAction="Hallo" )
      
      #logObj( pwd.getpwuid( os.getuid() ), aData=pwd.getpwuid( os.getuid() ).pw_gecos )
      #print detectDistro( 'lsussudouser@dev-host.local' )
      
      print "Admin?", isAdmin('pancake')
      
      dbconn=openMySQLConnection()
      #
      #
      #createMySQLPackagesTable(dbconn)
      
      createMySQLLogTable( dbconn )
      createMySQLUpgradeTable( dbconn )
      print 'done'
      
      sudoOK= testSudoConnection( 'lsussudouser@dev-host.local' )[0]
      if sudoOK==0:
        print "Yes"
      else:
        print "check sudo permission"
      
      #dblogObj( dbconn, pwd.getpwuid( os.getuid() ) )
    
      for host in getAllRegisteredHosts():
        whereClause="WHERE Connection='" + host +"'"
        print  selectWhereData( dbconn, HOSTS, LASTUPDATE, whereClause )
      #getAsyncSubprocessValue( "lsussudouser@dev-host.local", "`which sudo` `which yum` -yt update" )
      #connection = "lsussudouser@dev-host.local"
      #lockConnection( dbconn, connection, 'pancake', 'dev-host' )
         
      #print str( selectWhereData(dbconn, HOSTS, 'Updates', 'WHERE Connection="' + connection + '"') )
      
      #if isLockedConnection( dbconn, connection ):
      #  lockdata = getLockDataOfConnection( dbconn, connection )
      #  for field in lockdata.keys():
      #    print field, ':', lockdata[ field ]    
      #  unlockConnection( dbconn, connection )
      #print "1", isAutoupdateConnection(dbconn, connection)
      
      #setEnabledConnection(dbconn, connection)
      #print isLockedConnection( dbconn, connection )
      #print "B", isEnabledConnection(dbconn, connection)
      #setAutoupdateConnection(dbconn, connection, False)
      #setEnabledConnection(dbconn, connection)
      
      #print '2', isAutoupdateConnection( dbconn, connection )
      
      
      
      #if isEnabledConnection(dbconn, connection):
      #  
      #  print isEnabledConnection(dbconn, connection)
        
      #if not isEnabledConnection(dbconn, connection):
      #  setEnabledConnection(dbconn, connection)
      #  print isEnabledConnection(dbconn, connection)
      
      #print getUpgradeData( dbconn, 'lsussudouser@dev-host.local' )
      #print hasUpgradeData( dbconn, 'lsussudouser@dev-host.local' )

      dbconn.close()
      #for p in getSUSEPatches( 'lsussudouser@dev-host-suse.local' )[1:4]:
      #  print p

      
    #createMySQLHostsTable( dbconn, HOSTS )
    
    #createMySQLTable( dbconn, "pancake@dev-host.local" )
    
    #dbconn.close()
    # 
    # print getAptShowVersionsVersion( "pancake@dev-host.local" ) < "0.21"
    # print getAptShowVersionsVersion( "pancake@dev-host.local" ) < "0.21"
    #print detectDistro(    "pancake@dev-host.local" )
    
    #print getCommandValue( "pancake@dev-host-suse.local", "env LANG=en_US zypper lp | grep needed | wc -l" )
    #print detectDistro( "pancake@dev-host-suse.local" )
    #print detectDistro( "pancake@dev-host-centos.local" )

    # getDistFamily("CentOS release 5.11 (Final)")
    # print getREDHATPatches( "pancake@dev-host-centos.local"  )


    if ( len( sys.argv ) >= 2 ) and ( sys.argv[1] == "version" ):
      print getFullProduct(), getVersion()

    if ( len( sys.argv ) >= 2 ) and ( sys.argv[1] == "ping" ):
      # print sys.argv[2]
      # detectDeadHost( sys.argv[2] )
      
      print "connection", sys.argv[2]
      dbconn=openMySQLConnection()
      print time.ctime()
      x=str( datetime.now() )
      print setLastPingTimeConnection( dbconn, sys.argv[2], x )
      dbconn.close()
        
    if ( len( sys.argv ) >= 2 ) and ( sys.argv[1] == "dump" ):
      for host in getAllRegisteredHosts():
        print host
      #insert()
      
    if ( len( sys.argv ) >= 2 ) and ( sys.argv[1] == "test2" ):
      dbconn=openMySQLConnection()
      for host in getAllEnabledOfDist( dbconn, DEBIAN ):
        print getAptShowVersionsVersion( host )
      #insert()
    
    if ( len( sys.argv ) >= 2 ) and ( sys.argv[1] == "ldap" ):
      print getLdapCfg()
      print getLdapUserAttribs('pancake')
      print getLdapMailAddress( 'pancake' )

    if ( len( sys.argv ) >= 2 ) and ( sys.argv[1] == "yum" ):
      print getREDHATPatches( sys.argv[2] )


    if ( len( sys.argv ) >= 2 ) and ( sys.argv[1] == "int" ):
      print asciiremapSimpleString(['hallo','test'])

