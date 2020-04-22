#!/usr/bin/env python2

import os
import os.path
import string

# Variant 1
# 
# check if conf/apply.update.to.0.9.py and or sql exists
#
#  execute this 
#
# and rename to conf/applied.update.to.0.9.sql 
#

CONF='conf'

#print lsusversion.VERSION 

#updateExec = os.path.join( getBaseDir() , CONF, 'apply.update.to.' + lsusversion.VERSION + '.py' ) 
 
#print "updateExec",   updateExec

# TODO: Log this action for "debug and execution control"
# TODO: Log this action for "debug, possible rollback and execution control"


def applyUpdate():
  from getConfig import getBaseDir 
  from lsusversion import VMAJOR, VMINOR
  BIN='data' 
  updateExec = os.path.join( getBaseDir() , BIN, 'apply_update_to_' + str( VMAJOR ) + '_' + str( VMINOR ) + '.py' ) 
  updateBak =  os.path.join( getBaseDir() , BIN, 'applied_update_to_' + str( VMAJOR ) + '_' + str( VMINOR ) + '.bak' )



  if os.path.exists( updateExec ):

    # TODO LOG - Execution
    # TODO LOG - Execution

    execfile( updateExec, globals() )

    # TODO LOG - Rename
    
    os.rename( updateExec , updateBak )
    
    
    
        
  