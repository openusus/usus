#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#
# Query-Host Script prints a HTML Formular to query a host 
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

import HTML # TODO git commit
import getConfig
from getConfig import DISTRIBUTIONFAMILY, DEBIAN, REDHAT, SUSE, LOCKDATE, LOCKOWNER, LOCKHOST,\
  whereConnection, OWNEREMAIL


#COLUMNS= getConfig.getColumnList(cn, tableName, schema)# [ "Hostname", "Updates", "DistributionFamily", "KernelRelease", "KernelVersion", "Uptime", "ScanTime", "enabled", "autoupdate", "owneremail", "LastUpdate", "owneraccount", "ownergroup", "Connection" ]
Tables = [ 'Hosts', 'Packages', 'LOG', 'Upgrades', 'Users' ]

def getDefaultSelection( dbconn, tableName=getConfig.HOSTS ):
  selection=''
  for col in getConfig.getColumnList( dbconn, tableName ):
    selection += col + ','
  #print selection
  return string.rstrip( selection, ',') 

def getResult( tableName=getConfig.HOSTS ):
  
  result=''
  dbconn = getConfig.openMySQLConnection()
  if form.has_key('selection'):
    selection = form.getvalue('selection') 
  else:  
    selection = getDefaultSelection( dbconn, tableName )
    
  if form.has_key('query'):
    query = form.getvalue('query') 
    getConfig.logObj( query, 0, "query" ) 
  
    # zlib.decompress( rawdata )
    #rawdata = selectWhereData( dbconn, "Upgrades", "UpdateData", query )#.decode( 'base64' )
    #result = zlib.decompress( rawdata )
    if tableName=="Upgrades":
      selection = "Connection,LastUpdate"
      # TODO: Find index of "UpdateData" and replace with '' !!!!
      # than insert  selectWhereData "UpdateData" uncompressed at this indexes at the table
    
    
    try:  
      #if selection.count('UpdateData'):
      result = HTML.table( getConfig.selectData( dbconn,  tableName, ' ' + selection + ' ', query  ), header_row=string.split( selection, ',' ) )
      
    except:
      et, ev, ts = sys.exc_info()
      print et, ": ", ev
      print ts
  dbconn.close
  return result


print "Content-type: text/html; charset=utf-8\n\n"
print '<!DOCTYPE HTML>'  
form = cgi.FieldStorage()
try:
  query = form.getvalue( 'query', "where Connection not like ''" )
  
  
  doreload = form.getvalue( 'reload', 'false' )
  
  table = form.getvalue( 'table', getConfig.HOSTS )
  
  dbconn = getConfig.openMySQLConnection()
  selection = form.getvalue( 'selection', getDefaultSelection( dbconn, table ) )
  defaultselection=getDefaultSelection( dbconn, table )
  dbconn.close()
  
  
  options=''
  for option in Tables:
    if table==option: # selected:
      options += '<option value="' + option + '" selected>' + option + '</option>'
    else:
      options += '<option value="' + option + '">' + option + '</option>'
  
  # initialOptions='<option value="Hosts" >Hosts</option><option value="Packages">Packages</option>'
  if doreload == 'true':
    dbconn = getConfig.openMySQLConnection()
    selection=getDefaultSelection( dbconn, table )
    #selection=defaultselection
    query = 'where ' + string.split( selection,',')[0] + " not like ''"
    dbconn.close()
    result = "" # <code>Just Reloaded</code>"    
    
  else:
    result = getResult( table )
    
  QUERY_DATA={
            "FORMACTION": 'query.py',
            "PRE":'Select ',
            "MID": ' from ',
            "POST": '&nbsp;;',
            "VALUE": query,
            "RESULT": result,
            "SELECTION": selection,
            "DEFAULTSELECTION": defaultselection,
            "TABLE": table,            
            "OPTIONS": options,
            'TABLECOUNT': str( len( Tables ) )
            }
  
  if getConfig.isAdmin(  getConfig.getLoginName() ):
    QUERY_DATA['MESSAGE'] = "You are in Administrative Group: '<b>" + getConfig.LDAPADMINGROUP + "</b>'"
    print getConfig.loadTemplateReplaceData( getConfig.QUERY_FORM_TEMPLATE, QUERY_DATA )
  
  else:
    print '<h2>You are <font color="red">not</font> in Administrative Group: '+ "'" + getConfig.LDAPADMINGROUP + "'</h2>"
    
except:
  et, ev, tb = sys.exc_info()
  print et, ": ", ev
  print tb
  print  sys.exc_info()
  #print 'XXXX'

  
