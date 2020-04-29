#!/usr/bin/env python
# -*- coding: utf-8 -*-
from types import NoneType



'''
#
# Builds a Form with System Package Data 
# 
# http://linux-updateserver.my.lan.local/lsus/bin/gethostdata?username=updateuser&amp;hostname=$hostname
#
# * Check if pingable and 
# ssh $user@$Host uname -a && ssh $user@$Host hostname
#
# 1. 
#
'''

import os
import os.path
import sys
import string
import time
import cgi
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
  whereConnection, OWNEREMAIL, OWNERGROUP, _UPDATE, getDatafolder


form = cgi.FieldStorage()
username = None
hostname = None

USERNAME="username"
HOSTNAME="hostname"

def gotParams():
    
    global form, username, hostname
    
    if form.has_key( USERNAME ) and form.has_key( HOSTNAME ):

      username = form.getvalue( USERNAME )
      hostname = form.getvalue( HOSTNAME )
    
      return 1
    else:
      return 0

  
def getInputForm():
    
    #server = SERVER_NAME
    print "<h1>Not Called Right</h1>"
    print "Missing parameters like: 'bin/gethostdata?username=updateuser&amp;hostname=$hostname'"

  
def buildDoUpdateUrl( username, hostname, distfamily ):

  return getConfig.buildButtonForm( username+'@'+hostname, distfamily, 'checkupdate', 'check for update', getConfig._CHECK, 'gethostdata.py' )    
  
  
def buildHostTable():
    global form, username, hostname
    
    print '<h1>' + getConfig.getFullProduct() + ' ' + getConfig.getVersion() + '</h1>'
    
    distfamily = form.getvalue( DISTRIBUTIONFAMILY, '' )
    owneremail = form.getvalue( OWNEREMAIL, '' )
    
    if form.has_key( OWNERGROUP ):
      group = form.getvalue( OWNERGROUP )
    
     
    print '<h3><a href="buildtable.py">[ ' + 'Back ...' + ' ]</a></h3><br>'     
        
    if distfamily!='':
      
      print '<table><tr><td valign="top">Check for updates at: &nbsp;</td><td>' + buildDoUpdateUrl( username, hostname, distfamily ), '</td></tr><table><br>'
      
    #else:
      #print 'Check for updates: ', distfamily, '<br>'
      
    if owneremail!='':
      print '<font color="blue"><b>Settings for ',hostname, "</b></font><br><br>"
      
      print '<table border="0" width="100%"><tr><td valign="top" width="15%">Change Email &nbsp;</td><td>', getConfig.buildOwnerEmailInputForm( username, hostname, owneremail ), '</td></tr></table><br>'
      if group != None:
        print '<table border="0" width="100%"><tr><td valign="top" width="15%">Change Ownergroup &nbsp;</td><td>', getConfig.buildOwnergroupInputForm( username, hostname, group ), '</td></tr></table><br>'
    
    
    
    
    if distfamily!='':
      
      try:    
        dbconn = getConfig.openMySQLConnection()
        connection =   username + "@" + hostname
      
        if getConfig.hasUpgradeData( dbconn, connection  ):
          print '<h3>Jump to > <a href="#lastupdatedata">Last update/upgrade data</a> (below) </h3>'
      
        print '<br><hr>' 
        print '<h4>Patchtable<a name="patchtable"></a></h4>Updates, Patches or Packages on <font color="magenta">', distfamily,  '</font><font color="blue"><b>',hostname, "</b></font>@", str( datetime.now() )
        print HTML.table( getConfig.selectData( dbconn, 'Packages' , "Name, Version, Architecture,  Description, Status, Distribution", getConfig.whereConnection( connection ) + " Order by Status" ),\
                        header_row=[ 'Package-Name',   'Version',   'Architecture', 'Description', 'Status', 'Distribution' ]
                      )
      
        print '<br><hr><br>'
      
        if getConfig.hasUpgradeData( dbconn, connection  ):
          print '<h3><a name="lastupdatedata"></a>Last update/upgrade data</h3>'
          print '<h4><a href="#patchtable">back to PatchTable</a></h4>'
          print '<u>Last Update @ ' + str( getConfig.selectWhereData( dbconn, 'Upgrades', 'LastUpdate', getConfig.whereConnection( connection ) ) ) + '</u><br><br>'
          upgradeData = getConfig.getUpgradeData( dbconn, connection )
          for line in string.split( upgradeData, '\n' ):
            print line, '<br>' # HTML.table(  )
        
      
        dbconn.close()
      
      except:
        etype, evalue, etb = sys.exc_info()
        evalue = etype("Cannot build Host Table: %s" % evalue)
          
        print  etype, evalue, etb
        
    
        
    
    
        
        
def _doUpgrade_old( dbconn, connection, distfamily ):
        if getConfig.isLockedConnection( dbconn, connection ):
          lockdata=getConfig.getLockDataOfConnection( dbconn, connection )
          print "<h2>Connection", connection, "is already running and locked since", lockdata[LOCKDATE], 'from', lockdata[LOCKOWNER], '@', lockdata[LOCKHOST], "</h2>" 
        else:
          
          print "<h1>Starting UPGRADE of:", connection, '</h1><br><font color="red"><b>Please wait for the Back-Link which appears below on finish!</b></font><br>'
          pingresult, txt = getConfig.checkPingConnection( connection )
          getConfig.dblogObj( dbconn, pingresult, pingresult, "status of ping: " + connection + " before gethostdata.doUpgrade()"  )          
          if pingresult == 0:
            print "Ping successfull, locking database<br>"
            
            getConfig.lockConnection( dbconn, connection, getConfig.getLoginName(), os.environ.get( "REMOTE_ADDR", "127.0.0.1") )
            sys.stdout.flush()
            
            if 1:
              if distfamily == REDHAT:
                rawresult = getConfig.getAsyncSubprocessValueList( connection, "`which sudo` `which yum` -yt update", True, getConfig.getDatafolder( getConfig._UPGRADE ) )
      
              elif distfamily==SUSE:
                rawresult = getConfig.getAsyncSubprocessValueList( connection, "sudo zypper --non-interactive --no-gpg-checks --gpg-auto-import-keys update", True,  getConfig.getDatafolder( getConfig._UPGRADE ) )
      
              elif distfamily==DEBIAN:
                rawresult = getConfig.getAsyncSubprocessValueList( connection, 'export DEBIAN_FRONTEND=noninteractive && sudo apt-get -q -y -V $1 -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" dist-upgrade', True, getConfig.getDatafolder( getConfig._UPGRADE ) )
          
            print "Wrote", getConfig.insertUpgradeData( dbconn, connection, rawresult ), "bytes in database.<br>"
            print "<code>End:", distfamily, '</code><br>' 
            sys.stdout.flush() 
            getConfig.updateConnection( dbconn, connection, distfamily, stage=getConfig.UPDATE )
            getConfig.insertPackageNamesIntoHostPackages( dbconn, connection, distfamily )
            getConfig.unlockConnection( dbconn, connection )
            print "<code>Updated Database for", connection, '</code><br>'
          else:
            print "could not ping: ", connection, txt
          sys.stdout.flush()                    
            
         
def checkUpdate( dbconn, connection, distfamily ):
        if getConfig.isLockedConnection( dbconn, connection ):
          lockdata=getConfig.getLockDataOfConnection( dbconn, connection )
          print "<h2>Connection", connection, "is already running and locked since", lockdata[LOCKDATE], 'from', lockdata[LOCKOWNER], '@', lockdata[LOCKHOST], "</h2>" 
        else:
          
          print "<h1>Starting check update of:", connection, '</h1><br><font color="red"><b>Please wait for the Back-Link which appears below on finish!</b></font><br>'
          pingresult, txt = getConfig.checkPingConnection( connection )
          getConfig.dblogObj( dbconn, pingresult, pingresult, "status of ping: " + connection + " before gethostdata.checkupdate()"  )          
          if pingresult == 0:
            print "Ping successfull, locking database<br>"
            sys.stdout.flush()
            user=getConfig.getLoginName()
            getConfig.lockConnection( dbconn, connection, user, os.environ.get( "REMOTE_ADDR", "N/A") )
            print "locked.<br>"
            
            sys.stdout.flush()
            
            if 1:
              print "Checking for available updates. Please wait..<br>"
              sys.stdout.flush()
              if distfamily == REDHAT:
                fedrel, frexists = getConfig.getCommandValue( connection, 'test -f /etc/fedora-release', DEBUG=False, Status=True )
                
                if frexists == 0:
                  rawresult = getConfig.getAsyncSubprocessValueList( connection, "`which sudo` `which yum` -y check-update ; test $? -eq 100 -o $? -eq 0", True, getConfig.getDatafolder('yum.check-update') )
                else:  
                  rawresult = getConfig.getAsyncSubprocessValueList( connection, "`which sudo` `which yum` -yt check-update ; test $? -eq 100 -o $? -eq 0", True, getConfig.getDatafolder('yum.check-update') )
      
              elif distfamily==SUSE:
                rawresult = getConfig.getAsyncSubprocessValueList( connection, "sudo zypper --non-interactive-include-reboot-patches --non-interactive --no-gpg-checks --gpg-auto-import-keys lp", True, getConfig.getDatafolder('zypper.lp') )
      
              elif distfamily==DEBIAN:
                rawresult = getConfig.getAsyncSubprocessValueList( connection, 'export DEBIAN_FRONTEND=noninteractive && sudo apt-get -q -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" update', True, getConfig.getDatafolder('apt.update') )
 
            #print '<pre>'
            #print rawresult
            #print '</pre>'
            print "done.<br>"
            print "flushing packages table.<br>"
            sys.stdout.flush()
            getConfig.deleteTableData( dbconn, 'Packages', whereConnection( connection ) )
            
#            print "Wrote", getConfig.insertUpgradeData( dbconn, connection, rawresult ), "bytes in database.<br>"
            print 'done<br>'
            print 'updating host information table<br>' 
            sys.stdout.flush() 
            getConfig.updateConnection( dbconn, connection, distfamily, stage=None )
            print 'done<br>' 
            print 'fill in current packages table<br>'
            sys.stdout.flush()
            getConfig.insertPackageNamesIntoHostPackages( dbconn, connection, distfamily )
            print 'done<br>' 
            print 'unlocking system<br>'
            sys.stdout.flush()
            getConfig.unlockConnection( dbconn, connection )
            print 'done<br>'
          else:
            print "could not ping: ", connection, txt
          sys.stdout.flush()            
    
def dodelete( dbconn, connection ):   
#  if getConfig.isLockedConnection( dbconn, connection ):
    # getConfig.lockConnection( dbconn, connection, getConfig.getLoginName(), getConfig.getRemoteAddress() )
    #lockdata=getConfig.getLockDataOfConnection( dbconn, connection )
    #print "<h2>Connection", connection, "is already running and locked since", lockdata[LOCKDATE], 'from', lockdata[LOCKOWNER], '@', lockdata[LOCKHOST], "</h2>"
     
 # else:
    getConfig.deleteHostFromHosts( dbconn, connection )
    getConfig.log( 'deletedHostFromHosts', 0, connection )
    getConfig.deleteHostFromPackages( dbconn, connection )
    getConfig.log( 'deleteHostFromPackages', 0, connection )
    print '<h3>Deleted !</h3>'
'''
# UN-USED! Just for Lock/Unlock-Tests. 
'''
def dolock( dbconn, connection ):   
  if not getConfig.isLockedConnection( dbconn, connection ):
    getConfig.lockConnection( dbconn, connection, getConfig.getLoginName(), getConfig.getRemoteAddress() )
    lockdata=getConfig.getLockDataOfConnection( dbconn, connection )
    print "<h2>Connection", connection, "is already running and locked since", lockdata[LOCKDATE], 'from', lockdata[LOCKOWNER], '@', lockdata[LOCKHOST], "</h2>"
    print '<h3>First do unlock, to delete!</h3>' 
  else:
    print '<h3><font color="green">[X] Connection <i>', connection,  "</i> is already locked.</font></h3>"


def dounlock( dbconn, connection ):  
  if getConfig.isLockedConnection( dbconn, connection ):    
    print "<h2>  " + getConfig.getLockInfoOfConnection( dbconn, connection ) + " will be unlocked.</h2>"
    getConfig.unlockConnection( dbconn, connection )
    print '<h3>[X] Done.</h3>'
  else:
    print '<h3><font color="green">[ ] Connection <i>', connection,  "</i> isn't locked.</font></h3>"

    
 
 
 
 
  
    
def doAction( anAction ):
    global form, username, hostname
    rawresult = ""
    connection = username + "@" + hostname
    
    if form.has_key( DISTRIBUTIONFAMILY ):    
      distfamily = form.getvalue( DISTRIBUTIONFAMILY, 'unknown/notgiven' )
        
          
      if anAction == 'doupdate':
        dbconn =  getConfig.openMySQLConnection()
        getConfig.doUpdate( dbconn, connection, distfamily )
        dbconn.close()
        
      elif anAction == 'doupgrade':
        dbconn =  getConfig.openMySQLConnection()
        getConfig.doUpgrade( dbconn, connection, distfamily )
        dbconn.close()
        
      elif anAction == 'checkupdate':
        dbconn =  getConfig.openMySQLConnection()
        checkUpdate( dbconn, connection, distfamily )
        dbconn.close()
        
      elif anAction == 'dodelete':
        dbconn =  getConfig.openMySQLConnection()
        dodelete( dbconn, connection )
        dbconn.close()
        
      elif anAction == 'dounlock':
        dbconn =  getConfig.openMySQLConnection()
        dounlock( dbconn, connection )
        dbconn.close()
        
      else:
        print "<h1>Got unknown ActionCommand:", anAction, '</h1><br>' 
    
    elif form.has_key( OWNEREMAIL ):
      newEmail = form.getvalue( OWNEREMAIL )        
      print "New Email: ", newEmail, "<br>"
      dbconn =  getConfig.openMySQLConnection()
      getConfig.updateData( dbconn, getConfig.HOSTS, OWNEREMAIL, newEmail, getConfig.whereConnection( connection ) )          
      getConfig.dblogObj(dbconn, "changed email to " + str(newEmail) , 0, "FormData: " + str( form ) )
      dbconn.close()
      
    elif form.has_key( OWNERGROUP  ):
      newGroup = form.getvalue( OWNERGROUP )        
      print "New Group: ", newGroup, "<br>"
      dbconn =  getConfig.openMySQLConnection()
      getConfig.updateData( dbconn, getConfig.HOSTS, OWNERGROUP, newGroup, getConfig.whereConnection( connection ) )          
      getConfig.dblogObj( dbconn, "changed group to " + str(newGroup) , 0, "FormData: " + str( form ) )
      dbconn.close()  
      
    else:
      print "<h1>Could not find specifier at :", form.keys(), '</h1><br>'
      
    print '<a href="buildtable.py">' + 'zurück ...' + '</a>'   
    
def process():  
  global form, username, hostname
  print "Content-type: text/html; charset=utf-8\n\n"
  print "<html>"
  print "<head>"
  # print '<meta http-equiv="Refresh" content="60">'
  print '<meta http-equiv="expires" content="0">'  
  print '<meta http-equiv="cache-control" content="no-cache">'
  print '<meta http-equiv="pragma" content="no-cache">'
  print '<script type="text/javascript" src="../src/js/u7n.js"></script>'
  print "</head>"
  print "<body>"  
  
  # cgi.print_environ( ) #..print_environ_usage()
  
  
  if gotParams():
    if form.has_key( "action" ):
      
      anAction= form.getvalue( "action" )
      #print "Action:", anAction
      try:
        doAction( anAction )
      except:
        et, ev, et = sys.exc_info()
        print et, ": ", ev
        print et
        
    else:
      buildHostTable()
    
  else:
    getInputForm()
  
  
  #print "Form:" 
  #print form
  
  #print '<br><br><a href="#" onclick="history.back();return false;">&lt;-- BACK '+ "to School" +' </a> '  


  print "</body>"
  print "</html>"
  return 0
  
process()


  
  

