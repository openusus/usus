#!/usr/bin/env python
# -*- coding: utf-8 -*-



import sys
import os
import string
import stat
import cgi

import cgitb
cgitb.enable()

# OWN Modules

import getConfig
import lsusversion


def parseresult( inputresultList ):
  result = ''
  resultDict={}
  """
['{:timestamp=>"2016-08-11T11:54:48.970371+0200", :message=>"Created package", :path=>"personal-lsus-preregister-of-pancake-for-dev-host.local_0.6.1_all.deb"}'
, '']
"""  

  for item in inputresultList:
    dictLine = string.replace( item, '{', '')
    dictLine = string.replace( dictLine, '}', '') 
    #print dictLine, '<br>'
    items = string.split( dictLine, ',' )
    #print 'items:', items, '<br>'
    for dictItem in items:
      
      kv = string.split( dictItem, '=>' )
      #print 'kv:', kv, '<br>'
      if len( kv ) > 1:
        resultDict[ string.strip( kv[ 0 ] ) ] = kv[ 1 ]
  try:    
    result = string.strip( resultDict[ ':path' ], '"' )
  except:
    result = str( inputresultList )  
  return result  
      
      
    
 

os.chdir( os.path.join( os.getcwd(), '..', 'download' ) )

LSUS_HOST = os.environ.get( 'SERVER_NAME', os.environ.get( 'HOSTNAME', 'localhost' ) + '.' + getConfig.DNS_DOMAIN )



HOSTOWNER=os.environ.get( 'REMOTE_USER', os.environ.get( 'LOGNAME', 'unknown_user' ) )



aKVDict = { 'HOST_OWNER': HOSTOWNER,
            'LSUS_HOST' : LSUS_HOST
          }

personal_prep_scriptContent = getConfig.loadTemplateReplaceData( 'src/clients/opt/openlsus/sbin/prepareregister.sh', aKVDict )


prepareshellScriptfileName = 'prepareregister_of_' + HOSTOWNER + '_for_' + LSUS_HOST + '.sh'


personal_prep_file = file( prepareshellScriptfileName, 'w' )
personal_prep_file.write( personal_prep_scriptContent )
personal_prep_file.flush()
personal_prep_file.close()

os.chmod( prepareshellScriptfileName, stat.S_IRWXU | stat.S_IRWXG | stat.S_IXOTH |stat.S_IROTH )

form=cgi.FieldStorage()
if form.has_key( 'pack' ):
  packformat = form.getvalue( 'pack', 'deb' )
else:
  packformat = 'deb'

if not (packformat == 'rpm' or packformat == 'deb'):
  packformat = 'deb'
# fpmcommandList 
fpmcl = []
fpmcl.append( '/usr/local/bin/fpm' ) 
fpmcl.append( '-t' )
fpmcl.append( packformat )  
fpmcl.append( '-n' )
fpmcl.append( 'personal_lsus-preregister_of_' + HOSTOWNER + '_for_' + LSUS_HOST ) 
fpmcl.append( '--license' )
fpmcl.append( 'GPL2' )
fpmcl.append( '--vendor' ) 
fpmcl.append( '"Marc Pahnke, openlsus community"' )
fpmcl.append( '--category' )
fpmcl.append( 'admin' )
if packformat == 'deb':
  fpmcl.append( '-d' )
  fpmcl.append( 'openssh-server' ) 
else:
  fpmcl.append( '-d' )
  fpmcl.append( 'openssh' )
fpmcl.append( '-d' )
fpmcl.append( 'sudo' ) 
fpmcl.append( '-d' ) 
fpmcl.append( 'wget' ) 
fpmcl.append( '-a' ) 
fpmcl.append( 'all' )
fpmcl.append( '-m' )
fpmcl.append( '"Marc Pahnke marc.pahnke@gmx.de"' ) 
fpmcl.append( '--description' )
fpmcl.append( '"openLSUS -prepare client package- * creates lsususer, * install ssh public key from control server and * adds sudo rule. * and registers at https://linux-updateserver.my.lan.local after installation"' )
fpmcl.append( '--url' ) 
fpmcl.append( 'https://github.com/openlsus/lsus' )
fpmcl.append( '--before-remove' )
fpmcl.append( '../src/clients/opt/openlsus/sbin/unprepareregister.sh' ) 
fpmcl.append( '--after-install' )
fpmcl.append( prepareshellScriptfileName ) 
fpmcl.append( '-C' )
fpmcl.append( '../src/clients' ) 
fpmcl.append( '-v' )
fpmcl.append( lsusversion.VERSION + '.' + str( lsusversion.CLIENT_PACK_VERSION ) )  

if packformat == 'deb':
  fpmcl.append( '--deb-no-default-config-files' ) 
#fpmcl.append( '--workdir' )
#fpmcl.append( '../downloads' )

fpmcl.append( '-s' )
fpmcl.append( 'dir' )
fpmcl.append( '.' )

fpmcommand = string.join( fpmcl )

#print "Content-Type: text/html"
#print

#print os.getcwd() + '<br>' 

getConfig.log( fpmcommand, aData='exec_fpm_command' )



#print '<pre>'
#print personal_prep_scriptContent


result = getConfig.getSubprocessValue( fpmcommand, web=False )



packageName =  parseresult( result )
# print fpmcommand + '<br>' 
#print  packageName # result

#print '</pre>'

#print '<br>'

# exit( 0 )

print "Content-Location:", packageName

dlfile = open( packageName )
content = dlfile.read()
dlfile.close()

  
print "Content-Type: application/octet-stream"
print 'Content-Disposition: attachment; filename="' + packageName + '"'
print "Content-Length: " + str( len(content) )
print
 

#sys.stdout.flush()

sys.stdout.write( content )

sys.stdout.flush() 


getConfig.log( packageName, aData='remove file' )
os.remove( packageName )
getConfig.log( packageName, aData='removed file' )

getConfig.log( prepareshellScriptfileName, aData='remove file' )
os.remove( prepareshellScriptfileName )
getConfig.log( prepareshellScriptfileName, aData='removed file' )

