# openUSUS - UnixServer Update Services 
## Readme

From the upcoming release 0.2 there will be a 
new REST JSON API backend, as base for a new 
React.js or VUE.JS frontend

This re-work is still work in progress
and wil be documented here.

Meanwhile, the legacy classic LSUS missing Libs will be sent to you on demand.
No more work will be done in that area


--- 
---
# OLD LEGACY DOCU
## openLSUS - LinuxServer Update Services 
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

* fpm
     
     is required for creating personalized RPM, Deb Client Packages
     is ruby based therefore you need ruby and ruby-dev to build the latest release  
     fpm itself comes via the ruby-gem package manager
     
      sudo apt-get -y install ruby ruby-dev gcc
      gem install fpm 
      
    currently the generated packages will be written in ./download 
    so ensure the apache process, user or group (www-data) has 
    write permission to   ./download
      
      root@lsus010:/# ls -la /var/www/html/download/
      total 60      
     <code>drwxr**w**xr-x 1 root **www-data** 4096 Oct 30  2018 .</code>

* 

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

 
Known Issues:
 Sometimes especially in a docker enviroment, the cgi socket inside of the apache process isn't initialized properly. 
 That causes execution erros of SSI commands.
 In this case just restart apache. it should solve the issue. Otherwise if the error doesn't disappear send me your environment detailed as possible
 and I'll try to reproduce and fix.    



