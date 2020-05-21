#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import sys
from time import gmtime, strftime
CURRENTYEAR=strftime("%Y", gmtime())

VMAJOR=0
VMINOR=11
# 3 - Fixed OpenSSH Dependency BUG on SUSE
# 4 - Fixed locate of visudo
# 5 - Added support for SELINUX on RedHat
CLIENT_PACK_VERSION = 5
VENDOR="OpenLSUS"
PRODUCT="UpdateManager"
ALIAS="LSUS"
FULL_PRODUCT=VENDOR + ' ' + ALIAS + ' ' + PRODUCT

VERSION=str( VMAJOR) + '.' + str( VMINOR )

COMPLETE = FULL_PRODUCT + ' ' + VERSION
COPYRIGHT='2015-' + CURRENTYEAR
COPYRIGHTTEXT='Copyright(c) ' + COPYRIGHT + ' by marc.pahnke@gmx.de'

_V_ = '-v'
_N_ = '-n'
_C_ = '-c'
_U_ = '-u'
_L_ = '-l'
__V = '--v'
_h_ = "-h"
__help = "--help"

HELP = '\nHelp for Parameters\n\t' + _V_ + ' for verbose' + '\n\t' + _N_ + ' for no linefeed' 
HELP += '\n\t' + __V + ' filename_compliant_format_v.2' + '\n\t' + _U_ + ' pre tar apply_update_transformation_a_b_format ' 
HELP += '\n\t' + _C_ + ' no linefeed plus client pack version' +  '\n\t-h/--help this help message' 

def getCopyright():
    return COPYRIGHTTEXT

if __name__ == '__main__':
    
    if len( sys.argv ) > 1 and sys.argv[ 1 ] == _V_:
      print( FULL_PRODUCT, VERSION ) 
      
    if len( sys.argv ) > 1 and sys.argv[ 1 ] == __V:
      print( str( FULL_PRODUCT ).replace(' ', '_' ) + '-' + VERSION )


    if len( sys.argv ) > 1 and sys.argv[ 1 ] == _U_:
      print( str( VMAJOR) + '_' + str( VMINOR ) )
        
    elif len( sys.argv ) > 1 and sys.argv[ 1 ] == _N_:
      print( VERSION, end='')
      
    elif len( sys.argv ) > 1 and sys.argv[ 1 ] == _C_:
      print( VERSION + '.' + str( CLIENT_PACK_VERSION ), end='')

    elif len( sys.argv ) > 1 and sys.argv[ 1 ] == _L_:
      print( COPYRIGHTTEXT) #, end='')
      
    elif len( sys.argv ) > 1 and ( sys.argv[ 1 ] == _h_ or sys.argv[ 1 ] == __help ):
      print( FULL_PRODUCT, VERSION, HELP )

    else:
      print( VERSION )