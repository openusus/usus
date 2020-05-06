#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#
# Query-Host Script prints a HTML Formular to query a host 
# 
# wget  http://linux-updateserver.my.lan.local/lsus/register?username=updateuser&amp;hostname=$hostname
#
# * Check if pingable and
# ssh $user@$Host uname -a && ssh $user@$Host hostname
#
# 1. 
#
'''

REGISTER_FRAME="""
<html>
<head>
  <title></title>
  <meta content="">
    <style></style>

  <frameset rows="*%,40%">
  <frame name="lsus-form-area" src="../bin/register.py">
  <frame name="lsus-help-area"  src="../html/register_instructions_de.html">
</head>
<noframes>
<body>

  
  
  

  
  
  
NO FRAMES SUPPORTED BY YOUR Browser 

</body>
</noframes>
</frameset>
</html>
"""

print "Content-type: text/html; charset=utf-8\n\n"

print REGISTER_FRAME