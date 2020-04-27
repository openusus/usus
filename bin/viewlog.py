#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#
# Query-Host Script prints a HTML Formular to query a host 
# 
# wget  http://linux-updateserver.my.lan.local/lsus/register?username=${lsusupdateuser}&amp;hostname=$hostname
#
# * Check if pingable and
# ssh ${lsusupdateuser}@$Host uname -a && ssh ${lsusupdateuser}@$Host hostname
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



print "Content-type: text/html; charset=utf-8\n\n"
print "<html>"
print "<body>"

dbconn = getConfig.openMySQLConnection()

query =  "Select * from LOG order by Id desc"  
#print query
# print HTML.table( getConfig.selectData( dbconn, getConfig.LOG , "*", "order by `Id` desc" ),\
print HTML.table( getConfig.executeQueryFetchAll( dbconn, query ),\
#executeQueryFetchAll
                        header_row=[ 'Id',   'Remote-IP',   'UserId', 'UserName', 'Timestamp', 'Action', 'Status', 'Data' ]
                      )

 
print "</body>"
print "</html>" 