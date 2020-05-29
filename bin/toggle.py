#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
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

sys.path.append( os.getcwd() )
sys.path.append( os.path.join( os.getcwd(), "lib" ) )
sys.path.append( os.path.join( os.getcwd(), "..", "lib" ) )
sys.path.append( os.path.join( os.getcwd(), "bin" ) )

import getConfig

form = cgi.FieldStorage()

print "Content-type: text/html; charset=utf-8\n\n"
print "<html>"

for key in form.keys():
  if key.find( ':flag' )!=-1:
    # string.in key: lsususer@10.145.104.100:autoupdate:flag 0
    value = form.getvalue( key, '-1' )
    if value=='-1':
      print "<h1>Wrong: Value", value, 'was not expected. Inform Author!</h1>'
      break
    print "<h2>Set:", key, 'to', value,"</h2>"
    sys.stdout.flush()
    
    tokens = key.split( ':' )
    connection = tokens[ 0 ]
    flagname   = tokens[ 1 ]
    dbconn = getConfig.openMySQLConnection()
    whereClause="WHERE Connection='" + connection +"'"
    getConfig.updateData( dbconn, getConfig.HOSTS, flagname, value, whereClause )
    
    getConfig.dblogObj( dbconn, 'changed ' + flagname + ' to', int(value), connection ) 
    
    dbconn.close()
    print "<b>[X] done</b></br>"
    
    
    break #nothing more to do 
  
sys.stdout.flush()     
print '<a href="buildtable.py" target="lsus-content-area">...back</a>'  
sys.stdout.flush()   



#print cgi.print_environ()

print "</html>"