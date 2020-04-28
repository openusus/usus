#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#
# Settings Script prints a HTML Form to set some values
# 
#
#
'''


import os
import os.path
import sys
import string
import time
import commands

import cgi
import cgitb
cgitb.enable()


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
  whereConnection, OWNEREMAIL






print "Content-type: text/html; charset=utf-8\n\n"
  
form = cgi.FieldStorage()

rwview=False

loginName = getConfig.getLoginName()

RW_VIEW_CHECKED=''

usersMode=getConfig.getUserRWMode( loginName  )

#print 'getUserRWMode: &quot;', usersMode, '&quot;<br>'

if usersMode==1:
  initValue='true'
else:
  initValue='false'
  
if form.has_key( 'editcheckboxvalue' ):
  rwview = form.getvalue( 'editcheckboxvalue', initValue ) 


  #print 'editcheckboxvalue rwview', rwview, "usersMode",usersMode , '<br>'

  if rwview=="true":
    getConfig.setUserRWMode( loginName, True )
    RW_VIEW_CHECKED='checked="checked"'
  
  else:
    getConfig.setUserRWMode( loginName, False )
    RW_VIEW_CHECKED=''
  
else:
  if usersMode==1:
    RW_VIEW_CHECKED='checked="checked"'
  else:
    RW_VIEW_CHECKED=''






COMMAND_DATA={
              'LOGINNAME' : loginName,
              'USERNAME'  : getConfig.getUserName(),
              'lastlogin' : str( getConfig.getUserLastLogin( loginName ) ),
              'firstlogin': str( getConfig.getUserFirstLogin( loginName ) ),
              'RW_VIEW_CHECKED' : RW_VIEW_CHECKED
            }

  
print getConfig.loadTemplateReplaceData( getConfig.SETTINGS_FORM_TEMPLATE, COMMAND_DATA )

#print '<hr>'

#for key in form.keys():
#  print 'key:', key, 'value:', form.getvalue( key, 'no value given'), '<br>'
 
#print '<hr>' 
  
#cgi.print_environ() 
  
# printResult()