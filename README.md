# openLSUS - LinuxServer Update Services 
### README  

With openLSUS LSUS you are able to manage cron based 
updates for several Linux systems. Doing Updates is central controlled and initiated by 
a central server.  

openLSUS uses public key authentication, that means and therefore its able to 
interact with its client password less without root password needed.

### Prerequisites:

mysql-server
apache2 + apache-mod-python

python-mysql-connector



pip:  sudo apt-get install python-pip
python-zenity: pip install python-zenity

apache without mod-compress

ON Ubuntu run:

    sudo apt-get install python-mysql.connector




##How it works in short:
 
1. you creates one dedicated user account, deploys a ssh public key and 
   setup one sudo rule on the target client machine, that should be updated.

2. you registers this machine in the LSUS server database.

That's it. 

From now on, depended on the cron Schedule, this system looks for and installs all 
updates non-interactive.
 
LSUS offers native packages to prepare a client. This packages are in deb and 
rpm format.
With this, the deployment of the ssh key and setup of the sudo rule is just one 
click or one commandline as root. 

There are hardcoded key filenames in this packages. If you change something 
like paths or names you have to recreate this packages. Read docu/COMPILE how.

Also the user who owns the ssh-public key, per default named 'lsusadmin', gets 
one encrypted password per default within the native package installation.
To change this  password you have to re-encrypt this with the crypt tool.
Enter the encrypted password in the prepareregister.sh and rebuild the native
packs afterward. To know how to compile the crypt tool, read the docu/COMPILE. 

 
 



