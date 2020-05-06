#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#
# Register-Host Script prints a HTML Formular and can be used Non-Interaktive via 
# 
# wget /curl http://linux-updateserver.my.lan.local/lsus/register?username=updateuser&amp;hostname=$hostname
#
# * Check ob pingable and 
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
import lsusversion

sys.path.append( os.getcwd() )
sys.path.append( os.path.join( os.getcwd(), "lib" ) )
sys.path.append( os.path.join( os.getcwd(), "..", "lib" ) )
sys.path.append( os.path.join( os.getcwd(), "bin" ) )

import getConfig

from getConfig import AUTOUPDATE, ENABLED, INFORMOWNER, OWNEREMAIL, LSUS_CONTENT_AREA, OWNERACCOUNT, DOMAIN,\
  OWNERGROUP

form = cgi.FieldStorage()
import cgitb
cgitb.enable()
username = None
hostname = None


USERNAME="username"
HOSTNAME="hostname"

#REGISTER_FORM="""
#"""

crappy='onclick="document.writeln("registering...")'
crap='&nbsp; &nbsp;${owneremail.label}:<input id="volatile" type="text" name="${owneremail}" title="${owneremail.title}" disabled>"'



#REGISTER_FORM=string.replace( REGISTER_FORM, '${'+USERNAME+'}', USERNAME )
#REGISTER_FORM=string.replace( REGISTER_FORM, '${'+HOSTNAME+'}', HOSTNAME )
#REGISTER_FORM=string.replace( REGISTER_FORM, '${'+AUTOUPDATE+'}', AUTOUPDATE )
#REGISTER_FORM=string.replace( REGISTER_FORM, '${'+ENABLED+'}', ENABLED )
# REGISTER_FORM=string.replace( REGISTER_FORM, '${'+OWNEREMAIL+'}', OWNEREMAIL )
#REGISTER_FORM=string.replace( REGISTER_FORM, '${'+OWNERGROUP+'}', OWNERGROUP )
#REGISTER_FORM=string.replace( REGISTER_FORM, '${'+OWNERACCOUNT+'}', OWNERACCOUNT )
# REGISTER_FORM=string.replace( REGISTER_FORM, '${'+INFORMOWNER+'}', INFORMOWNER )
#REGISTER_FORM=string.replace( REGISTER_FORM, '${'+DOMAIN+'}', DOMAIN )


def gotParams():
    
    global form, username, hostname
    
    if form.has_key( USERNAME ) and form.has_key( HOSTNAME ):
      #print "has keys" + USERNAME + " - " + HOSTNAME
      
    
      username = form.getvalue( USERNAME )
      hostname = form.getvalue( HOSTNAME )
    
      #print "<b>Hostname:</b> " + hostname + "<br>"
      #print "<b>Username:</b> " + username + "<br>"  
    
      return 1
    else:
      return 0
    
    

  
def getInputForm():
    #global REGISTER_FORM
    #server = SERVER_NAME
    loginname=getConfig.getLoginName()
    if getConfig.isAdmin( loginname ):
      admincolor = 'red'
      admintxt   = '[X] you have admin rights'
    else:
      admincolor = 'darkgreen'
      admintxt = 'regular user'
    
    scriptName = os.getenv( "SCRIPT_NAME" )
    
    data = { 
        
        'form.name'    : scriptName,
        'form.action'  : scriptName,
        'username'     : USERNAME,
        'hostname'     : HOSTNAME,
        'autoupdate'   : AUTOUPDATE,
        'enabled'      : ENABLED,
        'ownergroup'   : OWNERGROUP,
        'owneraccount' : OWNERACCOUNT,
        'domain'       : DOMAIN,
        'domain.value' : getConfig.DEFAULT_DOMAIN,
        
        'ownergroup.value'  : '',
        'owneraccount.value': loginname,
        
        'FULLPRODUCT'  : getConfig.getFullProduct(),
        'VERSION'      : getConfig.getVersion(),
        'UserName'     : getConfig.getUserName(),
        'admin.color'  : admincolor,
        'admin.txt'    : admintxt,
        
        #TODO:: LDAP: 'ownergroupdatalist': getConfig.getOwnerGroupDatalist( loginname, 'ownergrouplist' ),
        
        
         
        USERNAME    + '.title': "Enter the Username with special SUDO Permissions on the HOST.\n(How to create such a user is described below.)\nUse 'lsususer' as default name.",
        HOSTNAME    + '.title': "Enter the Hostname if posible with full qualified domain.",
        AUTOUPDATE  + '.title': "Enables Automatic Updates",
        ENABLED     + '.title': "Enables system to check for or do updates.",
        INFORMOWNER + '.title': "Inform the given User about the update process via Email",
        OWNEREMAIL  + '.title': "The Email Address of the user to inform.",
        OWNERACCOUNT+ '.title': "The User Account Name of the owner to inform",
        DOMAIN      + '.title': "Your Email-Domain (Click to change)",
        OWNERGROUP  + '.title': "The Users Group Name of the buddies for the system ( They can see this too)",
          
        USERNAME    + '.label': "Sudo Username",
        HOSTNAME    + '.label': "Hostname",
        AUTOUPDATE  + '.label': "Automatic Updates",
        ENABLED     + '.label': "Enable system",
        INFORMOWNER + '.label': "Inform Owner on Update",
        OWNEREMAIL  + '.label': "Email of the Owner",
        OWNERACCOUNT+ '.label': "Account name of the Owner",
        OWNERGROUP  + '.label': "Buddy user group"
    
        }
        
    #
    # userName= getConfig.getUserName()
    #loginname=
    #admin = ''
    
    
  #      admin='<span style="color:red;">[X] you have admin rights.</span>'
    
    #===========================================================================
    # print 'You are logged in as: <span id="REMOTE_USER" style="color:blue;">', userName , '</span>', admin
    # print '<h2 id="Message">Register Linux Host with the given <strong>Sudo</strong> User for automatic central remote controlled Updates.</h2>'
    # print "Instructions how to create such a SUDO User can be found below"
    # print '<br>'
    # print '<br>'
    # print '<a href="buildtable.py" target="lsus-content-area">' + 'back ...' + '</a>'
    # print ''
    # print '<br>'
    # print '<form name="' + script + '" action="' + script + '" method="get" target="' + LSUS_CONTENT_AREA + '">'  
    #===========================================================================
    
  
    #
           
    
             
           
    
    

    REGISTER_FORM = getConfig.loadTemplateReplaceData( getConfig.REGISTER_FORM_TEMPLATE, data )

    
    
    
    
    
    # REGISTER_FORM=string.replace( REGISTER_FORM, '${ownergroup.list}',  ownergrouplist )
                                  
    #for key in LABELS.keys():    
    #  REGISTER_FORM=string.replace( REGISTER_FORM, '${'+ key +'.label}',  LABELS[ key ] )
    #for key in TITLES.keys():    
    #  REGISTER_FORM=string.replace( REGISTER_FORM, '${'+ key +'.title'}',  TITLES[ key ] )
       
    #print REGISTER_FORM
    
    
    
    #print '<br>XX', str( int( bool( form.getvalue( INFORMOWNER, 1 ) ) ) )
    #print '<hr><hr>'
    return REGISTER_FORM

  
def register( anUsername, aHostname ):
  global form
  DEBUG=0
  VERBOSE=1
  connection = anUsername + "@" + aHostname
  
  print '<li>Connection which should be registered: <b>', connection, '</b></li>' 
  sys.stdout.flush()
  #print 1
   
  
  dist = getConfig.detectDistro( connection )
  print "<li>Family which has been detected: <b>'",  dist, "'</b></li>" 
  sys.stdout.flush()
  
  # Check for apt-show-version 
  if( dist == getConfig.DEBIAN ):
    getConfig.installAptShowVersions( connection )
  
  dbconn=getConfig.openMySQLConnection() 
  if VERBOSE:   
    print "<li>Opened Database: <b>'", dbconn.user, "@" ,dbconn.database,"@", dbconn.server_host, "'</b></li>"  
    sys.stdout.flush()
  
   
       
  result = getConfig.createMySQLPackagesTable( dbconn )
  if VERBOSE:  
    print "<li>Created MySQL Packages Table.</li>"  
    sys.stdout.flush()
    
    if DEBUG:
      print "DEBUG: >" , connection, dist, '<'
      sys.stdout.flush()
      
  result =  getConfig.insertPackageNamesIntoHostPackages( dbconn, connection, dist, DEBUG )
  
  
  if VERBOSE:  
    print "<li>Inserted package names into host packages table.</li>"
    sys.stdout.flush()
    
  result = getConfig.insertHostIntoHosts( dbconn, connection )
  if VERBOSE:  
    print "<li>Inserted host into hosts table.</li>"
    sys.stdout.flush()

  Enabled = form.getvalue( ENABLED, 1 )
  doAutoUpdate = form.getvalue( AUTOUPDATE, 1 )    
  # doInformUser = form.getvalue( INFORMOWNER, 0 )
    
  #ownerEMail=''
  ##if int( bool( doInformUser ) ):
  ownerAccount = form.getvalue( OWNERACCOUNT, '' )
  ownerDomain = form.getvalue( DOMAIN, getConfig.DEFAULT_DOMAIN )
  ownerEMail = getConfig.getLdapMailAddress( ownerAccount ) #+'@'+ownerDomain
  
  Enabled=True
  if DEBUG:
    print dbconn, connection, dist, Enabled, doAutoUpdate, ownerEMail, '<br>'
    #print form
  
  print "<li>Update Data of : <b>'",  connection, "'</b></li>" 
  getConfig.updateConnection( dbconn, connection, dist, Enabled, doAutoUpdate, ownerEMail, getConfig.INITIAL )
  sys.stdout.flush()
  getConfig.updateData( dbconn, getConfig.HOSTS,  OWNERACCOUNT, ownerAccount, getConfig.whereConnection( connection ) )
  print "<li>Inserted owner account: <b>'", ownerAccount, "'</b></li>"
  sys.stdout.flush()
  
  ownergroup = form.getvalue( OWNERGROUP, '' )
  if ownergroup != '':
    getConfig.updateData( dbconn, getConfig.HOSTS,  OWNERGROUP, ownergroup, getConfig.whereConnection( connection ) )
    print "<li>Inserted owner group: <b>'", ownergroup, "'</b></li>"
    sys.stdout.flush()
    
  if VERBOSE:
      print "<li>Closing Database: <b>'", dbconn.user, "@" ,dbconn.database,"@", dbconn.server_host, "'</b></li>"    
  dbconn.close()
  if VERBOSE:
    print "<li>Database Closed:", not dbconn.is_connected(), "</li>"
  
    sys.stdout.flush()
  
  if VERBOSE:
    print "<li>Collect Mail Info</li>"
    sys.stdout.flush()
  item=username + "@" + hostname
  sub=" has been registered"
  servername = getConfig.getServerName()
  yourname=""
  try:
    yourname = getConfig.getLdapDisplayName( ownerAccount )
  except:
    yourname = ownerAccount
    
  msg = '<h1>Hi, ' + yourname + '</h1>'  
  msg += '<h2>A Message from ' + lsusversion.FULL_PRODUCT + ' ' + lsusversion.VERSION + '</h2>'
  msg += "<ul><li><b>" + item + '</b>' + sub + '</li>' + '<li>Family: <b>'+ dist +'</b></li>' 
  msg += '<li>Registered at: <b>'+ servername +'</b></li>'
  
  msg += '<li>Go to <a href="https://'+ servername + '">https://'+ servername +'</a> to check for updates and adjust the ownergroup of the system, if necessary.</li></ul>'
  msg += '<hr><ul><li>Thank you for using ' + lsusversion.FULL_PRODUCT + '</li><li>Send bugs and suggestions to <a href="mailto:marc.pahnke@gmx.de?subject=LSUS%20'+lsusversion.VERSION+'%20issue&body=Hello,%0A%0DI%20have%20an%20issue%20with%20LSUS%20' + lsusversion.VERSION + '%0A%0D%0A%0DDetails:%20...">Marc Pahnke (marc.pahnke@gmx.de)</a></li></ul>'
  
  ''' ### if you dont expected this email '''  
  
  if VERBOSE:
    print "<li>Collected Mail Info / Sending now...</li>"    
    sys.stdout.flush()
    
  getConfig.mail( msg, "FYI: LSUSINFO! " + item + sub + ' at ' + servername + ' for owner: ' + ownerEMail, 'lsusadmin@my.lan.local' )
  
  getConfig.mail( msg, item + sub + ' at ' + servername ,ownerEMail )
  
  
  print '<li>', item + sub + ' at ' + servername, "... and mailed to", ownerEMail, "<br></li><li>done.</li></ul>"
  sys.stdout.flush()
    
  return
    
    
def process():  
  global username, hostname
    
  print "Content-type: text/html; charset=utf-8\n\n"
  
  # cgi.print_environ( ) #..print_environ_usage()
  
  
  if gotParams(): # then Register()
    pingresult = getConfig.checkPing( hostname )
    if pingresult == 0:
      # sshresult = checkSSH( username + "@" + hostname )
      """ 
      ACHTUNG Test soll  sshresult = checkSSH( username + "@" + hostname ) 
      """
      sshresult = getConfig.checkSSH( username, hostname )      
      if sshresult[0] == 0:
        
        
        
        sudoOK = getConfig.testsudo( username, hostname )#  testSudoConnection( 'pancake@dev-host.local' )[0]
        if sudoOK[ 0 ] == 0:
          print "[X] Sudo OK<br>"
        
          
          try:
          
          
            register( username, hostname )
            print '<a href="buildtable.py" target="' + LSUS_CONTENT_AREA + '">' + 'back ...' + '</a>'
            print "</body>"
            print "</html>"
            return 0      
          
          except:
            etype, evalue, etb = sys.exc_info()
            evalue = etype( "Cannot exec register: %s" % evalue)
            print "<b>" + username + "@" + hostname + '</b> could not registered.<br>'
            print etype, evalue, etb
        else:  
                  
          print "<b>Check sudo permission - Error: " + str( getConfig.testsudo( username, hostname, True ) ) + "</b><br>"
            
      else:
        print  username + "@" + hostname + " could not be registered (could not connect via ssh)<br><br>Details:", sshresult, "<br>If RedHat, check, if selinux is disabled! <br>#> selinuxenabled should return not 0<br>"
    else:
      print  username + "@" + hostname + " could not be registered (could not ping) [" + str( getConfig.getPingOutput( hostname ) ) + "] <br>"
    
  else:
    print getInputForm()
    
    return 0
  
  
  #print "Form:" 
  #print form
  
  #print '<br><br><a href="#" onclick="history.back();return false;">&lt;-- BACK '+ "to School" +' </a> '  

  print '<a href="register.frame.py" target="' + LSUS_CONTENT_AREA + '">' + 'back ...' + '</a>'
  print "</body>"
  print "</html>"
  return 0
#print "Content-type: text/html; charset=utf-8\n\n"
#print __name__
#if __name__ == '__main__':  
#  register('lsussudouser', 'testhost')
#else:  
process()


  
  

