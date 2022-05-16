#!/usr/bin/env python3
import os

CFGDIRNAME='conf'
HOSTS = "Hosts"
USERS = "Users"
LOG   = "Log"

CFGFILENAME='lsus.cfg'

# LOG DB COLUMNS

IPADDRESS = "Ipaddress"
USERID    = "Userid"
USERNAME  = "Username"
TIMESTAMP = "Timestamp"
ACTION    = "Action"
STATUS    = "Status"
DATA      = "Data"

# USERS Table
USER_LOGINNAME  = 'loginname'
USER_RWMODE     = 'rwmode'
USER_LASTLOGIN  = 'lastlogin'
USER_FIRSTLOGIN = 'firstlogin'



UNKNOWN_LSUS_USER = 'Unknown_LSUS_User'

# DB.Core returns the config-Dict
# reads the ConfigFile which returned by getConfigFilePath()
# and assign its Fields to
# result[CFGKEYDBHOST]
# result[CFGKEYDBNAME]
# result[CFGKEYDBUSER]
# result[CFGKEYDBPASS]
# todo: replace error-out with write2errorlogfile && "error occurred (((reading config)))?, check logfile"

# Core.Config.Get.DataFolder
#  todo: write and use builtin nosql
#  todo: add some file(xyz.py). exists checks before return.
#    - check for symlink spoofing cross-site injections
def getBaseDir():
  # __file__ == core/backend/config/default.py
  configpath = os.path.dirname( os.path.realpath( __file__ ) )
  return os.path.realpath( os.path.join( configpath, "..", "..", ".." ) )

# Core.Config.Get.ConfDir
# Gets the default config dir
# todo. clarify - cleanup, deduplicate redundant code, use builtin nosql
def getConfDir():
  # binpath=os.path.dirname( os.path.realpath( __file__ ) )
  return os.path.realpath( os.path.join( getBaseDir(), CFGDIRNAME ) )


