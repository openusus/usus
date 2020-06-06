FROM ubuntu:18.04

#

#  docker build - -t mpahnke/lamp:0.10 < Lamp.Dockerfile
#
#
# docker run -dit --hostname lsus010 --name lsus010 -p 8080:80 -p 2222:22 -p 33306:3306 mpahnke/lsus:0.10
# docker exec -it lsus010 bash

# docker stop lsus010
#
#  docker rm lsus010

ENV LSUSADMIN=lsusadmin

RUN apt-get -y update && apt-get -y install apt-utils && apt-get -y dist-upgrade

RUN apt-get -y install apache2 apache2-utils libapache2-mod-python mariadb-client mariadb-server \
    python-pip python-mysql.connector python-gtk2-dev vim mc ssh sudo
RUN apt-get -y install sudo iputils-ping
RUN pip install click

RUN a2enmod rewrite ssl actions include cgi headers actions alias python




#  add Line in /etc/apache/apache2.conf via sed
#  Addhandler ModPython .py
RUN sed -i '/<Directory \/var\/www\/>/,/<\/Directory>/ s/AllowOverride None$/AllowOverride None \n#added automatically\n        Addhandler cgi-script .py/' /etc/apache2/apache2.conf && \
    sed -i '/<Directory \/var\/www\/>/,/<\/Directory>/ s/Options Indexes FollowSymLinks/Options Includes ExecCGI Indexes FollowSymLinks\n#added automatically\n        Addhandler cgi-script .py/' /etc/apache2/apache2.conf && \
    sed -i 's/^#PermitRootLogin prohibit-password/# PermitRootLogin prohibit-password\n#added automatically\nPermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/^#X11UseLocalhost yes/# X11UseLocalhost yes\n#added automatically\nX11UseLocalhost no/' /etc/ssh/sshd_config


#RUN service apache2 stop