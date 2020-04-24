#!/usr/bin/env python
# -*- coding: utf-8 -*-



import commands
import string
import sys
import os
import os.path
import pwd
import socket
import platform
import csv
import itertools
import urllib
import cgi
import cgitb



from datetime import date, timedelta


basepath = os.path.join( os.path.dirname( os.path.realpath( __file__ ) ), '..' )
sys.path.append( os.path.join( basepath, "lib" ) )
sys.path.append( os.path.join( basepath, "parallel-ssh" ) )
sys.path.append( os.path.join( basepath, "parallel-ssh", 'bin' ) )

#print sys.path
from datetime_modulo import datetime 
#sys.path.append( os.getcwd() )
#sys.path.append( os.path.join( os.getcwd(), "lib" ) )
#sys.path.append( os.path.join( os.getcwd(), "..", "lib" ) )
#sys.path.append( os.path.join( os.getcwd(), "bin" ) )

import pssh # import * #_DEFAULT_TIMEOUT # do_pssh#
from psshlib import psshutil
from markup import oneliner as ol

from update import applyUpdate

import HTML
import markup
import lsusversion

import getConfig
from getConfig import DISTRIBUTIONFAMILY, DEBIAN, REDHAT, SUSE, SOLARIS, ENABLED, AUTOUPDATE, _UPGRADE, _UPDATE, _CHECK,\
  dblogObj,  urlprefix, whereConnection, lsusversion, MIN_ROW, MAX_ROW
                # 'Enbld' 
htmltablekeys = [ '#', '[-]','Family', 'Active',  AUTOUPDATE.capitalize(), 'Query and Details', 'Perform Update', 'Perform Upgrade', 'Owner-Email', 'Owner-Group','# Updates', 'Last Check Time', 'Last Update Time',  'Kernel-Release', 'Hostname',  ]
sqltablekeysdict = { 
                         '#': "None", 
                         '[-]': "None",
                    'Family': 'DistributionFamily', 
                    'Active':'enabled', 
                     AUTOUPDATE.capitalize(): AUTOUPDATE, 
                     'Query and Details':'Connection', 
                     'Perform Update':'None', 
                     'Perform Upgrade':'None', 
                     'Owner-Email':'owneremail', 
                     'Owner-Group':'ownergroup',
                     '# Updates':'Updates', 
                     'Last Check Time':'ScanTime', 
                     'Last Update Time':'LastUpdate',  
                     'Kernel-Release':'KernelRelease', 
                     'Hostname':'Hostname', 
                     'Unlock':'LockDate', 
                     'Delete':'None' }



admin_htmltablekeys = [ 'Unlock', 'Delete' ]
hashsign = ['#']
# 'Kernel-Version', 'Uptime',

# print '<hr>'           
form = cgi.FieldStorage()


def getTableHeader( isAdmin ):
    if isAdmin:      
      header_row = HTML.TableRow( htmltablekeys + admin_htmltablekeys + hashsign , header = True )
    else:      
      header_row = HTML.TableRow( htmltablekeys + hashsign, header = True )
    return header_row
  

def buildSortLink( aLinkText ):
  result = markup.page()
  result.add('<nobr>')
  result.add( '<b>' + aLinkText + '</b>' )
  columnName = sqltablekeysdict[ aLinkText ]
  
  if columnName != 'None':
    
    result.a( ol.img( src = '../res/images/up.png', width= '15' ), href = 'buildtable.py?' + urllib.urlencode( { 'col': sqltablekeysdict[ aLinkText ] , 'dir': ' asc' } ) )
    result.a( ol.img( src = '../res/images/down.png', width = '15' ), href = 'buildtable.py?' + urllib.urlencode( { 'col': sqltablekeysdict[ aLinkText ], 'dir': ' desc' } ) )
  result.add('<nobr>')
  return result



def getSortableTableHeader( isAdmin ):
  if isAdmin:
    colNames = htmltablekeys + admin_htmltablekeys + hashsign
  else:
    colNames = htmltablekeys + hashsign
    
  cells = []
  for colName in colNames:
    cell = HTML.TableCell( buildSortLink( colName ) )
    cells.append( cell )
  
  return HTML.TableRow( cells, header = True )
  
  



def buildpackagedetailsurl( aConnection, distfamily, urlPrefix='' ):
    connection = string.split( aConnection, "@" )
    username = connection[0]
    hostname = connection[1]    
    result = '<a href="' + urlPrefix + 'gethostdata.py?hostname=' + hostname + '&username=' + username + '&' + DISTRIBUTIONFAMILY + '=' + distfamily + '">' + aConnection + '</a>'
    return result



def buildupdateurl( aConnection, distfamily ):  
   return getConfig.buildButtonForm( aConnection, distfamily, 'doupdate',  "upDate", _UPDATE, 'gethostdata.py' )
  
def buildupgradeurl( aConnection, distfamily ):
  return getConfig.buildButtonForm( aConnection, distfamily, 'doupgrade',  "upgRade", _UPGRADE, 'gethostdata.py' )
  
def builddeleteform( aConnection, distfamily ):
  return getConfig.buildButtonForm( aConnection, distfamily, 'dodelete',  'delete', 'delete', 'gethostdata.py' )

def buildunlockform( dbconn, aConnection, distfamily ):  
  info = '<div title="' + getConfig.getLockInfoOfConnection( dbconn, aConnection ) + '">'
  _info = '</div>'
  return info + getConfig.buildButtonForm( aConnection, distfamily, 'dounlock',  'unlock', 'unlock', 'gethostdata.py' ) + _info


def buildCheckbox( aConnection, aFlag, aValue, edit = True ):
  connection = string.split( aConnection, "@" )
  username = connection[0]
  hostname = connection[1]
  if aFlag:
    checked = ' checked'
  else:
    checked= ''
   
  action="toggle.py"
  
  if edit:
    disable =''
  else:
    disable = ' disabled="disabled"'
   
  form='<form id="' + 'form.' + aConnection + '.' + aValue + '" name="' + aValue + '" action="' + action + '" method="get" target="' + getConfig.LSUS_CONTENT_AREA + '">'  
  checkbox = '<input type="checkbox" id="' + aConnection + '.' + aValue + '" value="' + aValue + '" name="' + aConnection + '.' + aValue + '.box' \
    + '" onchange="dochange( ' + "'" + aConnection + "'" + ', ' + "'" + aValue + "'" + ' )"' \
    + checked + disable + '>'
  submitflag='<input type="hidden" id="' + aConnection + ':' + aValue + ':flag' + '" name="' + aConnection + ':' + aValue + ':flag' + '" value="' + 'undefined">'  
  return form + submitflag + checkbox + aValue.capitalize() + '</form>'
    
 



 
    
def buildEditUrl( ahostConnection, owner, edit = True, group='', showUser=True ):
  if edit:
    connection = string.split( ahostConnection, "@" )
    username = connection[0]
    hostname = connection[1] 
    #owner =''
    if owner == None or owner.strip() == '':
      owner = 'none'    
    if group == None or group.strip() == '':     
      group = 'none'
    result = '<a href="gethostdata.py?hostname=' + hostname + '&username=' + username + '&' + getConfig.OWNEREMAIL + '=' + owner + '&' + getConfig.OWNERGROUP + '=' + group + '">'
    if showUser:
      result = result + owner + '</a>'
    else:
      result = result + group + '</a>' #+ owner + '</a>' + '&nbsp;<font size="1em">(' + group + ')</font>''' 
  else:
    if showUser:
      result = owner
    else: 
      result = group  
  return result


def getHostProperies( ahostConnection, edit = True ):
    result = []
    
    dbconn=getConfig.openMySQLConnection()
    
    distfamily = getConfig.selectWhereData( dbconn, getConfig.HOSTS, DISTRIBUTIONFAMILY, getConfig.whereConnection( ahostConnection ) )
    
    result.append( getConfig.buildimageurl( distfamily ) )
     
    isEnabled = getConfig.isEnabledConnection( dbconn, ahostConnection ) 
        
    result.append( buildCheckbox( ahostConnection, isEnabled, ENABLED, edit ) )
    
    result.append( buildCheckbox( ahostConnection, getConfig.isAutoupdateConnection( dbconn, ahostConnection ), AUTOUPDATE, edit ) )
    if edit:
      result.append( buildpackagedetailsurl( ahostConnection, distfamily ) )
      if isEnabled:
        result.append( buildupdateurl( ahostConnection, distfamily ) )   
        result.append( buildupgradeurl( ahostConnection, distfamily ) )
      else:
        result.append( '<font size="1em">' + ahostConnection + '</font>' )
        result.append( '<font size="1em">' + ahostConnection + '</font>' )
    else:
      result.append(  ahostConnection )
      result.append( '<font size="1em">' + 'N/A' + '</font>' )
      result.append( '<font size="1em">' + 'N/A' + '</font>' )
      
    owner = getConfig.selectWhereData( dbconn, getConfig.HOSTS, getConfig.OWNEREMAIL, getConfig.whereConnection( ahostConnection ) )
    ownergroup = getConfig.selectWhereData( dbconn, getConfig.HOSTS, getConfig.OWNERGROUP, getConfig.whereConnection( ahostConnection ) )
    
    if owner!=None and owner !='':
      result.append( buildEditUrl( ahostConnection, owner, edit, ownergroup, True ) )
    else:
      result.append('No Owner!')
      
    #if ownergroup!=None and ownergroup !='':
    result.append( buildEditUrl( ahostConnection, owner, edit, ownergroup, False ) )
    #else:
    #  result.append('')
    
    for key in getConfig.sqlkeys:
        data = getConfig.selectWhereData( dbconn, getConfig.HOSTS, key, getConfig.whereConnection(ahostConnection) )
        
        #if key == DISTRIBUTIONFAMILY:
        #  result.append( getConfig.buildimageurl( data ) )
          
        #else:
        result.append( data )
        
    if getConfig.isAdmin( getConfig.getLoginName() ):
      if getConfig.isLockedConnection( dbconn, ahostConnection):
        result.append( buildunlockform( dbconn, ahostConnection, 'any' ) )
      else:
        result.append( '<div align="center">&middot;</div>' )
      result.append( builddeleteform( ahostConnection,'any' ) )
    
    dbconn.close()
    
    return result
  
  



def createHostsTable():
    print "Create table .."
    dbconn=getConfig.openMySQLConnection()
    getConfig.createMySQLHostsTable( dbconn, "Hosts" )
    dbconn.close()



###
# For the User Mail
#
def getTimeCell( lastUpdate, action='update', triggers=[2,10] ): #dbconn, connection ):
  week = timedelta( weeks = 1 )
  now=datetime.now()
  dateformat='%Y-%m-%d %H:%M:%S'
  
  lastupdate = datetime.strptime( str(lastUpdate), dateformat )
  weeks = -int( ( lastupdate - now ).total_seconds() / week.total_seconds() ) 
  
  result = None# HTML.TableCell( str( lastUpdate), bgcolor='green' )#''
  attrs={}
  if weeks == triggers[0]:
    attrs['title'] = 'Warn: The last '+action+' was performed ' + str( weeks )  + ' week ago.\n\nPlease check and apply manually if applicable.\n'  
    result= HTML.TableCell( str( lastUpdate),  bgcolor='yellow', attribs=attrs )  
    #result += ''
  
  elif weeks > triggers[0] and weeks < triggers[1]: 
    attrs['title'] = 'Warn: The last '+action+' was performed ' + str(weeks)  + ' weeks ago.\n\nPlease check and apply manually if applicable.\n'  
    result= HTML.TableCell( str( lastUpdate ),  bgcolor='orange', attribs=attrs )#, attribs=attrs )
    #result += ''
  elif  weeks > triggers[1]: 
    attrs['title'] = 'Critical: The last '+action+' was performed ' + str(weeks)  + ' weeks ago!!\n\nPlease check and apply immediately!\n' 
    result= HTML.TableCell( str(lastUpdate),  bgcolor='red', attribs=attrs )#, attribs=attrs )  
#    += ''
  
  
  #if result == '':
  #  result += 'Found ' + str( updatecount ) + ' updates. Last update was at ' + str( lastUpdate ) + '.' 
  return result


def getUpdateCountCell( updatecount, triggers=[50,250] ): #dbconn, connection ):

  #week = timedelta( weeks = 1 )
  #now=datetime.now()
  #dateformat='%Y-%m-%d %H:%M:%S'
  
#  lastupdate = datetime.strptime( str(lastUpdate), dateformat )
#  weeks = -int( ( lastupdate - now ).total_seconds() / week.total_seconds() ) 
  
  result = None #HTML.TableCell( str(updatecount), bgcolor='green' )
  
  
  # countLevel = updatecount // 50
  attrs={}  
  if updatecount > triggers[1]:
    attrs['title'] = 'Warn: The amount of ' + str(updatecount)  + ' updates has exceeded the critical count!!! Please update immediately.'
    #result = 'Critical: The amount of ' + str(updatecount)  + ' updates has exceeded the critical count!\n\nPlease update immediately!!\n'
    return HTML.TableCell( str(updatecount), bgcolor='red', attribs=attrs ) # + '.\n\n\n'
    
  elif updatecount > triggers[0] and updatecount < triggers[1]:  
    attrs['title'] = 'Warn: The amount of ' + str(updatecount)  + ' updates nearly exceeds the critical count!'
    
   # result = 'Warn: The amount of ' + str(updatecount)  + ' updates nearly exceeds the critical count!\n\nPlease check and apply manually if applicable.\n'
    return HTML.TableCell( str(updatecount), bgcolor='orange', attribs=attrs ) # + '.\n\n\n'
  elif updatecount > triggers[0] // 2:
    attrs['title'] = 'Info: Please check and apply manually if applicable.'
    return HTML.TableCell( str(updatecount), bgcolor='yellow', attribs=attrs ) # + '.\n\n\n' 
  
    
 # if result == '':
#    result += 'Found ' + str( updatecount ) + ' updates. Last update was at ' + str( lastUpdate ) + '.' 
  return result




## Old Style without pssh!
def insertOld():
    print "Starting insert at", datetime.today()
    devmailbody="<html><body>" + "Starting insert at: " + str( datetime.today() )+ '<br>On:' + socket.getfqdn() + ', ' + commands.getoutput('hostname -I') 

    # TODO: replace last email address param by the LSUS Admins Email address
    # TODO: !
    # TODO: !
    # TODO: !

    getConfig.mail( devmailbody + "</body></html>" , getConfig.lsusversion.FULL_PRODUCT+' '+ getConfig.lsusversion.VERSION+" - Dev Report", 'marc.pahnke@gmx.de' )
        
    updateday = date.today().isoweekday() == 4 
    devmailbody += "<br>Today is patch day:" + str( updateday )
    createHostsTable()
    
    dbconn=getConfig.openMySQLConnection()
    connections={}
    connections[ DEBIAN ] = []
    connections[   SUSE ] = []
    connections[ REDHAT ] = []
    updatecommands={}
    updatecommands[ DEBIAN ] = 'export DEBIAN_FRONTEND=noninteractive && sudo apt-get -q -y -V $1 -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade'
    updatecommands[ SUSE   ] = 'sudo zypper --non-interactive --no-gpg-checks --gpg-auto-import-keys patch'
    updatecommands[ REDHAT ] = '`which sudo` `which yum` -yt update'
                  
    for connection in getConfig.getAllRegisteredHosts( None ):
      
                 
      #getConfig.insertHost( dbconn, host )
      if getConfig.isEnabledConnection( dbconn, connection ):
        hostname = string.split( connection, "@" )[1]  
        
        #hostname = connection[1]
        pingresult = getConfig.checkPing( hostname )
        
        if pingresult[0] != 0:            
          getConfig.dblogObj( dbconn, "Ping of " + connection + ' failed.' , pingresult[0], pingresult[1] )          
          
          print "Ping of " + connection + ' failed.'           
          #continue
        else:
          
        
        
          """TODO: Check ssh """
        
          
          dist = getConfig.detectDistro( connection )
      
          ### getConfig.insertHostIntoHosts( dbconn, connection )
          ### getConfig.updateConnection( dbconn, connection, dist, stage=getConfig.NONE, web=False )#, 1, 1, 'marc.pahnke@gmx.de' )
          ### getConfig.insertPackageNamesIntoHostPackages( dbconn, connection, dist )
    
          doautoupdate = getConfig.isAutoupdateConnection( dbconn, connection )          
          
          if 1:#updateday: # 1=Monday, Today is Thursday :-) 
            if 1: #doautoupdate: 
              
              connections[ dist ].append( connection ) 
              # print dists[ dist ]
               
              print "adding Host:", connection   
              ### updateresultList = [ 'Update Result' ] + getConfig.doUpdate( dbconn, connection, dist, False )
      
        print connections
              
      else:
        print "Skipped disabled: ", connection
        
    for dist in connections.keys(): # read all dists.
      
      print dist, updatecommands[ dist ], connections[ dist ]
      getConfig.execPssh( updatecommands[ dist ], connections[ dist ] )
    """ Mail"""
    
    #businessUsers = getConfig.selectData(dbconn, getConfig.HOSTS, "DISTINCT " + getConfig.OWNEREMAIL )
    
    #print businessUsers
    ### if updateday or date.today().isoweekday()==1:
      ### sendBulkMail( dbconn )
    
    dbconn.close()
    
    # "INSERT INTO employees "
    #    "(first_name, last_name, hire_date, gender, birth_date) "
    #           "VALUES (%s, %s, %s, %s, %s)")

    getConfig.mail( devmailbody+"</body></html>", getConfig.lsusversion.FULL_PRODUCT+' '+ getConfig.lsusversion.VERSION+" - Dev Report", 'marc.pahnke@gmx.de' )

    print 'done.'
    



#
#
#    
def insert():
  print "Starting Update at", datetime.today()
  
  updateday = date.today().isoweekday() == 4  
  
  devmailbody="<html><body>" + "Starting update at: " + getConfig.tstamp + '<br>On:' + socket.getfqdn() + ', ' + commands.getoutput('hostname -I') + ' within ' + __name__ 
  
  # Heartbeat ;-)
  if updateday or date.today().isoweekday() == 1:
    getConfig.mail( devmailbody + "</body></html>" , "Starting " + getConfig.lsusversion.FULL_PRODUCT+' '+ getConfig.lsusversion.VERSION + " - Dev Report", 'marc.pahnke@gmx.de' )
    
  dbconn=getConfig.openMySQLConnection()
  

  
  
  updatableConnectionsDict={}
  pingables={}
  
  

      
# """LOOP over ALL Enabled and Pingables!"""
  ###for dist in getConfig.DISTFAMILIES.keys():
    ###for host in getConfig.getAllEnabledOfDist( dbconn, dist ): 
      ###if getConfig.checkPingConnection( str( host ) ) == 0:   
        ###getConfig.updateConnection( dbconn, str( host ), dist, stage=getConfig.NONE, web=False )#, 1, 1, 'marc.pahnke@gmx.de' )
        ###getConfig.insertPackageNamesIntoHostPackages( dbconn, str( host ), dist )
  for dist in getConfig.DISTFAMILIES.keys():
    
    print dist, '\n'
    sys.stdout.flush()
    #try: 
    enabledHostsPerDistList = getConfig.getAllEnabledOfDist( dbconn, dist )
    
    pingableHostsPerDistList = getConfig.getPingablesListAndHandleDead( dbconn, enabledHostsPerDistList )
    
    getConfig.doPsshUpdateConnectionsPerDist( dbconn, pingableHostsPerDistList, dist )
    
    getConfig.doPsshInsertPackagesPerDist( dbconn, pingableHostsPerDistList, dist )
      
    devmailbody += '<br><br>Checked ' + str( dist ) + ': ' + str( getConfig.asciiremapSimpleHTML_LI( pingableHostsPerDistList ) )
    #except:
    #  getConfig.handleException( __name__ )
    
   
  #
  # Update the RedHat Patches count  
  for connection in getConfig.getPingablesList( getConfig.getAllEnabledOfDist( dbconn, REDHAT ) ): 
    
    #try:  
    updateCount = str( len( getConfig.getREDHATPatches( connection ) ) )
    print REDHAT, updateCount, 'updates @', connection  
    getConfig.updateData( dbconn, getConfig.HOSTS, getConfig.UPDATES , str( len( getConfig.getREDHATPatches( connection ) ) ), whereConnection( connection ) )
    #except: 
    #  getConfig.handleException( __name__ )
  

  if updateday:
    
    for dist in getConfig.DISTFAMILIES.keys():
    
      print dist, '\n'
      sys.stdout.flush()
    
      updatableConnectionsDict[ dist ] = getConfig.getUpdatablesForDist( dbconn, dist ) 
    
      pingables[ dist ] = getConfig.getPingablesList( updatableConnectionsDict[ dist ], True )
      
      getConfig.lockConnections( dbconn, pingables[ dist ], getConfig.getLoginName(), os.environ.get( "REMOTE_ADDR", "127.0.0.1")  )
      # DOIN UPDATE HERE
      getConfig.insertUpgradeDatas( dbconn, getConfig.getPsshResultDictList( getConfig.updatecommand[ dist ], pingables[ dist ], getConfig.getDatafolder( 'DoUpdates' ), web=False ) )
      
      getConfig.unlockConnections( dbconn, pingables[ dist ], getConfig.getLoginName(), os.environ.get( "REMOTE_ADDR", "127.0.0.1") )
        
      devmailbody += '<br><br>Updated ' + str( dist ) + ': ' + str( getConfig.asciiremapSimpleHTML_LI( pingables[ dist ] ) )
  
  
    ##      
    # Update Fields and Number of available Updates
    ##
    for dist in getConfig.DISTFAMILIES.keys():
    
      print dist, '\n'
      sys.stdout.flush()
 
      enabledHostsPerDistList = getConfig.getAllEnabledOfDist( dbconn, dist )
    
      pingableHostsPerDistList = getConfig.getPingablesList( enabledHostsPerDistList )
    
      getConfig.doPsshUpdateConnectionsPerDist( dbconn, pingableHostsPerDistList, dist )
    
      getConfig.doPsshInsertPackagesPerDist( dbconn, pingableHostsPerDistList, dist )
      
      
      
      devmailbody += '<br><br>Checked ' + str( dist ) + ': ' + str( getConfig.asciiremapSimpleHTML_LI( pingableHostsPerDistList ) )

  # Update the RedHat Patches count  
    for connection in getConfig.getPingablesList( getConfig.getAllEnabledOfDist( dbconn, REDHAT ) ):  
      print REDHAT, '\n', connection
      try:    
        getConfig.updateData( dbconn, getConfig.HOSTS, getConfig.UPDATES , str( len( getConfig.getREDHATPatches( connection ) ) ), whereConnection( connection ) )
      except: 
        getConfig.handleException( __name__ )
  ## print updatableConnectionsDict
  
  
  ###############
  ### SEND All available Updates to the devel-admin
  ##############
  
  allUpdates={}
  for dist in getConfig.DISTFAMILIES.keys():
    
    updatesDict = getConfig.getUpdatesAvailableDict( dbconn, getConfig.getPingablesList( getConfig.getAllEnabledOfDistOrdered( dbconn, dist, "Order by 'Updates'" ) ) )
    allUpdates = dict( allUpdates.items()  +  updatesDict.items() )
    
  from operator import itemgetter
  for sortedVal in sorted( allUpdates.items(), key=itemgetter(1), reverse=True ):      
    
    devmailbody += '<br><br>' + str( sortedVal[1] )  + '  Updates available @ ' + getConfig.getDistOfConnection( dbconn, str( sortedVal[0] ) ) + ' ' + str( sortedVal[0] )
    
  
  if updateday or date.today().isoweekday() == 1:  # Monday = 1, Sunday = 7
      sendBulkMail( dbconn )
  
  dbconn.close()
  
  devmailbody += "<br>Today is patch day:" + str( updateday )
  getConfig.mail( devmailbody + "</body></html>", getConfig.lsusversion.FULL_PRODUCT+' '+ getConfig.lsusversion.VERSION+" - Dev Report", 'marc.pahnke@gmx.de' )

  print 'done.'



  


#
# Sure operation to get at least one heartbeat on the screen
# 
def sure_go():
  # 1. ensure config files / test DB, LDAP etc jump to setup otherwise 
  # 2. test if login name contains Domain Separator 
  loginName =  getConfig.getLoginName()
  if getConfig.isAdmin( loginName ):
    admin='<font color="red"><strong>You are Admin.</strong></font>'
  else:
    admin=''
  
  
  
  cn= getConfig.openMySQLConnection()
  getConfig.createMySQLUsersTable(cn, getConfig.USERS)
  cn.close()
  getConfig.insertUser( loginName )
  
  # print "has User", loginName, getConfig.hasUser( loginName )
  rwview = False
  
  
  # getConfig.hasUser( loginName )
     # .getEditMode()
  #else:
   
    
  #form=cgi.FieldStorage()
  #if form.has_key( 'RW_VIEW_CHECKED' ):
  #    rwview = form.getvalue( 'RW_VIEW_CHECKED' ) 
      #print 'rwview0', rwview
      #getConfig.insertUser( loginName )
      #getConfig.setUserRWMode( loginName, rwview )
  #print 'rwview1', rwview
  #if getConfig.hasUser( loginName ): #True:getConfig.ge # usertable.hasUser() ):
  rwview = getConfig.getUserRWMode( loginName )# .getEditMode()
    #etConfig.hasUser( loginName )  
    #print "Mode", loginName, ':',rwview, '.'   
  # print 'rwview2', rwview
   
  if rwview:
    RW_VIEW_CHECKED = 'checked="checked"'
  else:
    RW_VIEW_CHECKED = ''  
    
  if form.has_key( MIN_ROW ):
      newMinRow = form.getvalue( MIN_ROW )
      getConfig.setUserValue( loginName, MIN_ROW, newMinRow )  
    
  if form.has_key( MAX_ROW ):
      newMaxRow = form.getvalue( MAX_ROW )
      getConfig.setUserValue( loginName, MAX_ROW, newMaxRow )    
    
  minrow = getConfig.getUserValue( loginName, MIN_ROW )
  maxrow = getConfig.getUserValue( loginName, MAX_ROW )
  
  if minrow == None:
    minrow  = 0
    
  if maxrow == None:
    maxrow  = 25           
              
              
  aKVDict = {
               'LSUS_FULL_PRODUCT': lsusversion.FULL_PRODUCT,
               
               'LSUS_VERSION':  lsusversion.VERSION,
               'IS_ADMIN': admin,
               'USERNAME': getConfig.getUserName(),
               'REMOTEIP': os.environ.get( "REMOTE_ADDR", "N/A" ),
               'RW_VIEW_CHECKED' : RW_VIEW_CHECKED,
               MIN_ROW: str( minrow ),
               MAX_ROW: str( maxrow )
            }

  print getConfig.loadTemplateReplaceData( getConfig.TEMPLATE_MAIN_TABLE, aKVDict )
  
  getConfig.log( loginName, 0, 'user logged in' )
  getConfig.log( getConfig.isAdmin( loginName ), 1, 'user is admin' )
  
  
  
  print '<hr>'
  sys.stdout.flush()
  
  
  print '<table border="1" id="display-table">'
  print str( getSortableTableHeader( getConfig.isAdmin( loginName ) ) )
  sys.stdout.flush()
  return rwview

  
def go( edit ):
    # table = HTML.Table(header_row=getTableHeader())
    
    
    #print commands.getoutput('id')
    rowCount = 0
    
    # direction = form.getvalue('dir', 'down')
    
    loginName =  getConfig.getLoginName()
    #print getConfig.getLdapGroups(loginName, '<br>')
    
    if form.has_key( 'col' ):
      newCol = form.getvalue( 'col' )
      getConfig.setUserSortCol( loginName, newCol )
      
    if form.has_key( 'dir' ):
      newDir = form.getvalue( 'dir' )
      getConfig.setUserSortDir( loginName, newDir )
      
      

    
    
    if edit: ## Just show the Systems assigned to the User or its Group
      registeredHosts = getConfig.getAllRegisteredHosts( loginName ) #, order = form.getvalue('col', getConfig.UPDATES ), direction = form.getvalue('dir', ' desc') )
      #registeredHosts = getConfig.getAllRegisteredHosts( loginName, order = form.getvalue('col', getConfig.UPDATES ), direction = form.getvalue('dir', ' desc') )
      
    else: # The ReadOnly (Manager View) should show all Systems 
      
      registeredHosts = getConfig.getAllRegisteredHosts( None ) #, order = form.getvalue('col', getConfig.UPDATES ), direction = form.getvalue('dir', ' desc') )
      
    for host in registeredHosts:
        
        #if not getConfig.isAdmin( loginName ):
        #  continue
        if edit:
        
          if getConfig.isNotOwner( host, loginName ):
          # print 'isNotOwner( host, loginName)',  host, loginName, '<br>'
            if not getConfig.isAdmin( loginName ):
              continue
          # else:
            
            
        #if hostConnection
        # print host
        # hostProperies = getHostProperies( host )
        Cells = []

        rowCount += 1        
        # running = 0
        cellcolor = 'green'
        
        # if edit:
        numbercell = HTML.TableCell( str( rowCount ) )
        
        Cells.append( numbercell )
        
        Cells.append( getConfig.buildSelectForm( host ) )
        
        for hostPropery in getHostProperies( host, edit ):
            aCell = HTML.TableCell( str( hostPropery ) )
            Cells.append( aCell )

        Cells.append( numbercell )
        
        #else:
        #  for hostPropery in getROHostProperies( host ):
        #    aCell = HTML.TableCell( str( hostPropery ) )
        #    Cells.append( aCell )
                    
                    
                    
                      
                    
            

        if rowCount % 2:
            rowcolor = 'lightgray'
        else:
            rowcolor = 'white'
            
          
      
        
        aRow = HTML.TableRow( Cells, bgcolor=rowcolor )
        
        print str( aRow )
            
        sys.stdout.flush()
            
    

def buildSystemRow( enabled, connection, family, lastUpdate, noUpdates, scantime ):
  result = []   
  if enabled:
    result.append( HTML.TableCell( 'Yes', bgcolor='darkgreen' ) )
    result.append( buildpackagedetailsurl( connection, family, urlprefix ) )  
          
  else:
    result.append( HTML.TableCell( 'No', bgcolor='gray' ) )
    result.append( connection )
  
  timecell=getTimeCell( lastUpdate )  
  if timecell == None: # Just show RedLines
    result.append( HTML.TableCell( str(lastUpdate), bgcolor='darkgreen' ) )
  else:
    result.append( timecell )
    
  countcell=getUpdateCountCell( noUpdates )  
  if countcell == None: 
    result.append( HTML.TableCell( str(noUpdates), bgcolor='darkgreen' ) )
  else:
    result.append( countcell )    
    
  scanCell = getTimeCell( str(scantime), 'check', [4,15] ) 
  if scanCell == None: 
    result.append( HTML.TableCell( scantime, bgcolor='darkgreen' ) )
  else:
    result.append( scanCell )
    
  #print connection, 'timecell',  timecell, 'count', countcell, 'scancell', scanCell
  if (timecell == None) and (countcell == None) and (scanCell == None):
    return None # Just show RedLines # Show alerts only
  
  return result 


def getLegend():
  result=''
  result += str( HTML.TableRow( [ HTML.TableCell( 'Alert', bgcolor='red' ), HTML.TableCell( 'No update since 10 weeks or the count of available updates is over 250' ) ] ) )
  result += str( HTML.TableRow( [ HTML.TableCell( 'Critical', bgcolor='orange' ), HTML.TableCell( 'The last update has been performed at least 2 weeks ago or the count of available updates is above 50' ) ] ) )
  result += str( HTML.TableRow( [ HTML.TableCell( 'Warn', bgcolor='yellow' ), HTML.TableCell( 'Last update was two weeks ago or the count of available updates is above 25' ) ] ) )
  #result += str( HTML.TableRow( [ HTML.TableCell( 'Info', bgcolor='green' ), HTML.TableCell( 'Last update was within the time period of one week or count of available updates is below 50' ) ] ) )
  return result        


def sendBulkMail( dbconn, subjectprefix='' ):  
  reportPrefix="<h2>Weekly " +getConfig.lsusversion.FULL_PRODUCT+' '+ getConfig.lsusversion.VERSION+ " up to date report</h2>All systems which are assigned to you: "
  headerrow=[ 'Enabled', 'Package Details', 'Last Update', 'Number Updates', 'Last Check' ]
   
  for user in getConfig.getBusinessUsers( dbconn ):
    print user#lastUpdate
  # if 1:
    # user='marc.pahnke@gmx.de
    rowCount=0   
    whereClause = "WHERE " + getConfig.OWNEREMAIL + " ='" + user + "'"
    systems=[]  
    
    rawsystems =  getConfig.selectData( dbconn, getConfig.HOSTS, 'enabled, Connection, LastUpdate, Updates, ' + getConfig.DISTRIBUTIONFAMILY + ', ' + getConfig.SCANTIME , whereClause )
    
    for rawsystem in rawsystems:
      
      enabled    = rawsystem[0]
      connection = rawsystem[1] 
      family     = rawsystem[4]
      lastUpdate = rawsystem[2]
      noUpdates  = rawsystem[3]
      scantime   = rawsystem[5]    
      
      system = buildSystemRow( enabled , connection, family, lastUpdate, noUpdates, scantime )
      
      if rowCount % 2:
        rowcolor = 'lightgray'
      else:
        rowcolor = 'white'        
        
      if system != None: # Dont Insert Green-Systems
        systems.append( HTML.TableRow( system, bgcolor=rowcolor ) )
        rowCount+=1
    
    if rowCount == 0:
      continue # Skip sending empty Mails
      
    report = reportPrefix + user + '<br><table border="0">' 
    report+=str( HTML.TableRow( headerrow,  header=True ) )
    for row in systems:
      report+=str( row )
    report+='</table>'
    
    report+=str( "Legend:<br><table>" + getLegend() + "</table>" )
    
    mailsubject = subjectprefix + '>>> Report of ' + getConfig.lsusversion.FULL_PRODUCT+' '+ getConfig.lsusversion.VERSION + ' * UpdateData of SystemUpdate of ' +  user + ' @ ' + platform.node() + '  <<<'
    getConfig.mail( report , mailsubject ) #, user )
    print "Send Mail to: ", user


def doRedHat():
  print 'doing REDHAT'
#
def doSuse():
  print 'doing SUSE'
  
def doDebian():
  print 'doing DEBIAN'

def test():
  print buildSortLink('Xtra')

def test2():
  
  dbconn=getConfig.openMySQLConnection()
  #sendBulkMail(dbconn, '# JUST for test - please ignore: ')
  devmailbody=''
  for dist in getConfig.DISTFAMILIES.keys():
    #for dist in getConfig.DISTFAMILIES.keys():
    
    updatesDict= getConfig.getUpdatesAvailableDict( dbconn, getConfig.getPingablesList( getConfig.getAllEnabledOfDistOrdered( dbconn, dist, "Order by 'Updates'" ) ) )

    #updatesDict= getConfig.getUpdatesAvailableDict( dbconn, getConfig.getPingablesList( getConfig.getUpdatablesForDist( dbconn, dist ) ) )
    from operator import itemgetter
    for sortedVal in sorted( updatesDict.items(), key=itemgetter(1), reverse=True ):
      #print sortedVal[0],  sortedVal[1]
    
    #for host in updatesDict.keys():
      
      
      devmailbody += '<br><br><b>' + dist + '</b> ' + str( sortedVal[0] ) + ' has ' + str( sortedVal[1] ) +  ' updates'
  
  dbconn.close()
  getConfig.mail( '<html><body>' + devmailbody + "</body></html>", 'Test of ' + getConfig.lsusversion.FULL_PRODUCT+' '+ getConfig.lsusversion.VERSION+" - Dev Report", 'marc.pahnke@gmx.de' )
#  
#
def testWeg():
  
  method={}
  method[REDHAT] = 'doRedHat()'
  method[SUSE]   = 'doSuse()'
  method[DEBIAN] = 'doDebian()'
  
  ### for dist in getConfig.DISTFAMILIES.keys():
    ### print  dist
    #sys.stdout.flush()
    ### exec method[ dist ] 
    #sys.stdout.flush()
  dbconn=getConfig.openMySQLConnection()
  #=============================================================================
  # for dist in getConfig.DISTFAMILIES.keys():
  #   enabledHostsPerDistList = getConfig.getAllEnabledOfDist( dbconn, dist )
  #   
  #   pingableHostsPerDistList = getConfig.getPingablesList( enabledHostsPerDistList )
  #   
  #   print pingableHostsPerDistList
  # 
  # print "X"  
  # nonPings = getConfig.getNotPingableList( ['lsusadmin@localhost'] )
  # print nonPings
  # stat, mess = getConfig.getPingOutput('localhost')
  #   
  # print "stat", stat, "mess", mess
  #=============================================================================
  
  updatableConnectionsDict={}
  
  for dist in getConfig.DISTFAMILIES.keys():
  # dist = DEBIAN  
    updatableConnectionsDict[ dist ] = getConfig.getUpdatablesForDist( dbconn, dist ) 
    
    updatableConnectionsDict[ dist ] = getConfig.getPingablesList( updatableConnectionsDict[ dist ] )
    
    getConfig.doPsshInsertPackagesPerDist( dbconn, updatableConnectionsDict[ dist ], dist )
  
  #print getConfig.getFileContentList('/home/lsusadmin/my_proj/openLSUS/lsus/data/packages/lsusadmin@localhost.local.net')
    
    # doPsshInsertPackagesPerDist
    # doPsshInsertPackagesPerDist
    #getConfig.doPsshUpdateConnectionsPerDist( dbconn, updatableConnectionsDict[ dist ], dist )
    
    #if dist == REDHAT: ## TODO: supress double call // Yum Needs an redundant Extra handling
    #   for host in  updatableConnectionsDict[ dist ]:
    
  
          #result[ "Updates" ] = str( len( getREDHATPatches( host ) ) )
    
  # print updatableConnectionsDict# [ dist ]
  
  
  
  ### for dist in getConfig.DISTFAMILIES.keys():
    ### for key in getConfig.sqlfordist[ dist ].keys():
      ### print dist, key, getConfig.sqlfordist[ dist ][ key ]
  
    #for connection in updatableConnectionsDict[ dist ]:
    #  if getConfig.checkPingConnection( connection ) > 0:
    #    print dist, 'remove not pingable',  connection 
    #    updatableConnectionsDict[ dist ].remove( connection )
        
        
    
    
  dbconn.close() 
# Dumps all registered Hosts, as csv is important for the enable, disable flags, the owner, and groups
# 
def dump():
  
  result=''
      
  
  #print getConfig.getColumnList( dbconn )
  selection='Connection,  enabled, autoupdate, owneraccount, ownergroup, owneremail, ScanTime, LastUpdate'
  result += selection + '\n'
  
  dbconn=getConfig.openMySQLConnection()
  for connection in getConfig.getAllRegisteredHosts( None ):
    #print connection
    
    
    x = getConfig.selectData( dbconn, getConfig.HOSTS , selection, whereConnection( connection ) )
    
    
    x = list( itertools.chain.from_iterable( x ) )
    #Connection, enabled, autoupdate, owneraccount, ownergroup, owneremail
    # result=''
    for y in x:
      result += str( y ) + ',' 
    result = result.rstrip(',') + '\n'
  
  if len( sys.argv ) > 2 :
    dumpfile = open( sys.argv[2], "w" )
    dumpfile.write(result)  
  else:
    print result
  # print '>', sys.argv[2], '<' 
 
  dbconn.close()
  


#
#
#
def reload():
    if len( sys.argv ) > 2 :
      
      dbconn=getConfig.openMySQLConnection() 
      print 'create Hosts Table...'
      getConfig.createMySQLHostsTable(dbconn, getConfig.HOSTS)
      print 'done.\n Create Packages Table...'
      getConfig.createMySQLPackagesTable(dbconn, getConfig.PACKAGES)
      print 'done.'
      with open(sys.argv[2], 'rb' ) as csvfile:
      
        hostreader=csv.reader( csvfile, delimiter = ',' )
        hostreader.next()
        
        for row in hostreader:
          
          # Connection,  enabled, autoupdate, owneraccount, ownergroup, owneremail'
          # lsusadmin@localhost.local.net,1,1,pancake,operators,marc.pahnke@gmx.de
          
          connection =  row[0]
          Enabled    =  int( row[1])
          doAutoUpdate = int( row[2] )
          ownerAccount = row[3]
          ownergroup = row[4]
          ownerEMail = row[5] 
          ScanTime   = row[6]
          LastUpdate = row[7]
          dist = getConfig.detectDistro( connection )
          if( dist==getConfig.DEBIAN ):
            getConfig.installAptShowVersions( connection )
          print 'reload connection', connection
          getConfig.insertHostIntoHosts( dbconn, connection )
          
          getConfig.updateConnection( dbconn, connection, dist, Enabled, doAutoUpdate, ownerEMail, getConfig.INITIAL )
          getConfig.updateData( dbconn, getConfig.HOSTS,  getConfig.OWNERACCOUNT, ownerAccount, getConfig.whereConnection( connection ) )
          getConfig.updateData( dbconn, getConfig.HOSTS,  getConfig.OWNERGROUP, ownergroup, getConfig.whereConnection( connection ) )
          
          getConfig.updateData( dbconn, getConfig.HOSTS,  getConfig.SCANTIME, ScanTime, getConfig.whereConnection( connection ) )
          getConfig.updateData( dbconn, getConfig.HOSTS,  getConfig.LASTUPDATE, LastUpdate, getConfig.whereConnection( connection ) )
          
          print 'reading packages of', connection
          getConfig.insertPackageNamesIntoHostPackages( dbconn, connection, dist )
        print 'done.\ncommiting data...'
        
        #dbconn=getConfig.openMySQLConnection()
        dbconn.commit()
        print 'done.'
        dbconn.close()
        print 'db closed.'
          


#
#
#
def testReload():
  # for each line from given file, do a register host.
  
  
  if len( sys.argv ) > 2 :
    opts, args = getConfig.defaultParse()# pssh.parse_args() 
    opts.outdir='./data'
    #print opts
    
    with open(sys.argv[2], 'rb' ) as csvfile:
      #dumpdata = getConfig.getFileContent( sys.argv[2] )
      hostreader=csv.reader( csvfile, delimiter = ',' )
      
      # Skip the Header Line 
      hostreader.next()
      hosts=[]
      
      command='uptime'
       
      for row in hostreader:
        #print ', '.join( row )
        # print row[0]
        
        
        dist = getConfig.detectDistro( row[0] )
        
        if dist == getConfig.SUSE:
          hosts.extend( psshutil.parse_host_string( row[0], default_user=opts.user ) )
          command='sudo env LANG=en_US zypper -n lp | grep needed | wc -l'
      #print hosts
      
    
    
    pssh.do_pssh(hosts, command, opts)  
      
    #csv.reader()
    
    #print dumpdata
#
# The Main 



#
if __name__ == '__main__':
    
    if ( len( sys.argv ) >= 2 ) and ( sys.argv[1] == "insert" ):
      insert()  
      
    elif ( len( sys.argv ) >= 2 ) and ( sys.argv[1] == "update" ):
      insert()    
      
    elif ( len( sys.argv ) >= 2 ) and ( sys.argv[1] == "dump" ):
      dump()
      
    elif ( len( sys.argv ) >= 2 ) and ( sys.argv[1] == "reload" ):
      reload()
      
    elif ( len( sys.argv ) >= 2 ) and ( sys.argv[1] == "table" ):
      createHostsTable()
      
    elif ( len( sys.argv ) >= 2 ) and ( sys.argv[1] == "test" ):
      test2()
      #test2
    elif ( len( sys.argv ) >= 2 ) and ( sys.argv[1] == "none" ):
      
      applyUpdate()
      
      print 'None :-)'
      
    elif ( len( sys.argv ) >= 2 ) and ( sys.argv[1] == "packs" ):
      getConfig.getDebianPatches( sys.argv[2] )
    else: 
      
      print "Content-type: text/html; charset=utf-8\n"
      cgitb.enable()
      #print "Update?"
      applyUpdate() 
      
      edit = sure_go() 
      #try: 
         
      go( edit )   
        
        #print "TAB</table>"
        
      
      #except:
      #  etype, evalue, etb = sys.exc_info()
        # evalue = etype( "Cannot exec: go() %s" % evalue )
          
      #  print etype, evalue, etb
    


