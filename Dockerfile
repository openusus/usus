FROM ubuntu:20.04
# mpahnke/lamp:0.10

# docker build -t mpahnke/lsus:0.10 .
#
#
# docker run -dit --hostname lsus010 --name lsus010 -p 8080:80 -p 2222:22 -p 33306:3306 mpahnke/lsus:0.10
# docker exec -it lsus010 bashexec -it lsus010 bash
#
#  docker exec -it lsus010 "service mysql restart && service ssh start"
#

# docker stop lsus010
#
#  docker rm lsus010

 #### delete: usermod        -a -G wheel lsusupdateuser

ENV LSUSADMIN=lsusadmin
ENV LSUSUPDATEUSER=lsusupdateuser
ENV LSUSDBAUSER=lsusdba
ENV LSUSDBAPASSWD=lsusdba1
ENV LSUSDBNAME=lsus


RUN apt-get -y update && apt-get -y install apt-utils && apt-get -y dist-upgrade

RUN apt-get -y install apache2 apache2-utils libapache2-mod-python mariadb-client \
    python3-pip python3-mysql.connector vim mc ssh sudo iputils-ping network-manager

# python3-gtk2-dev failed

RUN pip3 install click


COPY . /var/www/html/

RUN a2enmod rewrite ssl actions include cgi headers actions alias python
# workaround as long I don't us ajax
RUN a2dismod -f deflate



#  add Line in /etc/apache/apache2.conf via sed
#  Addhandler ModPython .py
#RUN sed -i '/<Directory \/var\/www\/>/,/<\/Directory>/ s/AllowOverride None$/AllowOverride None \n#added automatically\n        Addhandler cgi-script .py/' /etc/apache2/apache2.conf && \
#    sed -i '/<Directory \/var\/www\/>/,/<\/Directory>/ s/Options Indexes FollowSymLinks/Options Includes ExecCGI Indexes FollowSymLinks\n#added automatically\n        Addhandler cgi-script .py/' /etc/apache2/apache2.conf && \
#    sed -i 's/^#PermitRootLogin prohibit-password/# PermitRootLogin prohibit-password\n#added automatically\nPermitRootLogin yes/' /etc/ssh/sshd_config


RUN sed -i '/<Directory \/var\/www\/>/,/<\/Directory>/ s/AllowOverride None$/AllowOverride None \n#added automatically\n        Addhandler cgi-script .py/' /etc/apache2/apache2.conf && \
    sed -i '/<Directory \/var\/www\/>/,/<\/Directory>/ s/Options Indexes FollowSymLinks/Options Includes ExecCGI Indexes FollowSymLinks\n#added automatically\n        Addhandler cgi-script .py/' /etc/apache2/apache2.conf && \
    sed -i 's/^#PermitRootLogin prohibit-password/# PermitRootLogin prohibit-password\n#added automatically\nPermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/^#X11UseLocalhost yes/# X11UseLocalhost yes\n#added automatically\nX11UseLocalhost no/' /etc/ssh/sshd_config


RUN apt-get -y install ruby ruby-dev gcc && gem install fpm



RUN update-rc.d -f ssh defaults && \
    update-rc.d apache2 enable && \
    update-rc.d ssh enable && \
    service ssh start



RUN groupadd wheel && \
    useradd  -m -d /home/${LSUSADMIN} -s /bin/bash -g wheel -c 'LSUS System User' ${LSUSADMIN} && \
    useradd  -m -d /home/${LSUSUPDATEUSER} -s /bin/bash -g users -c 'LSUS Remote Update User' ${LSUSUPDATEUSER} && \
    usermod -a -G wheel www-data && usermod -a -G wheel ${LSUSUPDATEUSER}

RUN SUDOLINE='%wheel ALL = (ALL) NOPASSWD: ALL'	&& echo "$SUDOLINE" | (sudo su -c "EDITOR='tee -a' visudo -f /etc/sudoers.d/wheelgroup") && chmod 0440 /etc/sudoers.d/wheelgroup

# adjust write permission for the www-data user to the download folder to allow to generate the personal deb/rpm
RUN chown -R www-data /var/www/html/download

RUN echo "root:r00t" | chpasswd && echo "${LSUSADMIN}:13UZ4dm.n" | chpasswd && echo "${LSUSUPDATEUSER}:13USu7d8053r" | chpasswd && echo 'set password'
RUN sudo -u ${LSUSUPDATEUSER} ssh-keygen -b 4096 -P '' -f /home/${LSUSUPDATEUSER}/.ssh/id_rsa && \
 cp /home/${LSUSUPDATEUSER}/.ssh/id_rsa.pub /var/www/html/ssh/ && \
 cd /var/www/html/ssh/ &&  ln -s id_rsa.pub ${LSUSUPDATEUSER}@linux-updateserver.4096bit.rsa.key && cd $OLDPWD

#RUN service mysql start && sleep 1 && mysql -u root -e "CREATE DATABASE ${LSUSDBNAME}; GRANT ALL PRIVILEGES ON ${LSUSDBNAME}.* TO '${LSUSDBAUSER}'@'%' IDENTIFIED BY '${LSUSDBAPASSWD}'; GRANT ALL PRIVILEGES ON ${LSUSDBNAME}.* TO '${LSUSDBAUSER}'@'localhost' IDENTIFIED BY '${LSUSDBAPASSWD}'; FLUSH PRIVILEGES" && \
#mysql ${LSUSDBNAME} -e "SHOW TABLES;"


#RUN service mysql start && sleep 1 && cd /var/www/html/bin && ./setup.py connection localhost lsusdba lsusdba1 lsus y && ./setup.py database lsus
#RUN service --status-all && networking status &&  service networking start && sleep 8 && ping -c 1 databaseserver && cat /etc/hosts && env && chown -R ${LSUSADMIN}:www-data /var/www/html/conf &&  chmod -R ug+w /var/www/html/conf && \
RUN chown -R ${LSUSADMIN}:www-data /var/www/html/conf &&  chmod -R ug+w /var/www/html/conf && chmod +x /var/www/html/bin/wait-for-it.sh && chmod +x /var/www/html/bin/run.sh
# && \
#    cd /var/www/html/bin && sudo -u ${LSUSADMIN} ./setup.py connection databaseserver lsusdba lsusdba1 lsus y && sudo -u ${LSUSADMIN} ./setup.py database lsus

# APACHE or lsusadmin +w
# sudo chmod a+w /var/www/html/conf/lsus.cfg

# COPY ./wait-for-it.sh /wait-for-it.sh

EXPOSE 80
#EXPOSE 3306
#EXPOSE 22


CMD ["/usr/sbin/apachectl", "-D", "FOREGROUND"]

#RUN service apache2 stop