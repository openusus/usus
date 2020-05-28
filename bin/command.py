#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#
# Command-Host Script prints a HTML Formular to exec a command at a host 
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



def getDists():
  dists=[]
  if form.has_key( 'distfamily' ):
    if 'all' == form.getvalue( 'distfamily' ): 
       dists = getConfig.DISTFAMILIES.keys()
  else: 
    if form.has_key( 'dists' ):
      #if form
      value = form.getvalue( 'dists' )
      if type( value ) is type( [] ):
        dists=value
      else:        
        dists.append( value )
  return dists
    

def getResult(  dists ):
  print '<h3>' + str( dists ) + '</h3>'
  result=''
  if form.has_key( 'acommand' ):
    acommand = form.getvalue('acommand') 
    getConfig.logObj( acommand, 0, "acommand" ) 
    # print '<h2>', acommand, '</h2>' 
    dbconn = getConfig.openMySQLConnection()
    try:
    
      for dist in dists: # getConfig.DISTFAMILIES.keys():
        result += '<h2>' + dist + '</h2>'
        for pingable in getConfig.getPingablesList( getConfig.getAllEnabledOfDist( dbconn, dist ) ):
          result += '<h3>' + pingable + '</h3>\n'
          
          result += '<code>\n'
          for line in getConfig.getAsyncSubprocessValueList( pingable, acommand, False, getConfig.getDatafolder( 'custom' )  ):
            result += unicode( str( line ), errors='ignore' ) + '<br>\n'
          result += '</code>\n'
          
          #result += str(  + '<br>'
          #result += '' 
    #ColNamesTable =  HTML.Table( header_row=['ColumnNames'])
    #columnlist = getConfig.getColumnList( dbconn )
  
    #ColNamesTable.rows.append( list( columnlist ) )
  
    #print str( ColNamesTable )
    except:
          et, ev, et = sys.exc_info()
          print et, ": ", ev
          print et
  
  #print HTML.table( getConfig.selectData( dbconn, getConfig.HOSTS , "*", query  ) )
  
    dbconn.close
  return result


print "Content-type: text/html; charset=utf-8\n\n"
  
form = cgi.FieldStorage()

#if form.has_key('query'):
acommand = form.getvalue( 'acommand', "ls -l ~" )
#else:
  # query = '* from Hosts'; 
#  query = "where DistributionFamily='debian'";

result=''

dists=getDists() 

print "<!-- " # Suppress useless pssh STDOUT via  HTML Comment String :-) Hack

result=getResult( dists )

print " -->"


COMMAND_DATA={
            "FORMACTION": 'command.py',
            "PRE":'#>',
            "POST": '',
            "VALUE": acommand,
            "RESULT": result
            }
if getConfig.isAdmin(  getConfig.getLoginName() ):
  COMMAND_DATA['MESSAGE'] = "You are in Administrative Group: '<b>" + getConfig.LDAPADMINGROUP + "</b>'"
  print getConfig.loadTemplateReplaceData( getConfig.COMMAND_FORM_TEMPLATE, COMMAND_DATA )
else:
    print '<h2>You are <font color="red">not</font> in Administrative Group: '+ "'" + getConfig.LDAPADMINGROUP + "'</h2>"
  
# printResult()