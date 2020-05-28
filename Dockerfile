FROM mpahnke/lamp:0.10

# docker build -t mpahnke/lsus:0.10 .
#
#
# docker run -dit --hostname lsus010 --name lsus010 -p 8080:80 -p 2222:22 -p 33306:3306 mpahnke/lsus:0.10
# docker exec -it lsus010 bash
#
#  docker exec -it lsus010 "service mysql restart && service ssh start"
#

# docker stop lsus010
#
#  docker rm lsus010

ENV LSUSADMIN=lsusadmin

#RUN apt-get -y update && apt-get -y install apt-utils && apt-get -y dist-upgrade

#RUN apt-get -y install apache2 apache2-utils libapache2-mod-python mariadb-client mariadb-server\
#    python-pip python-mysql.connector python-gtk2-dev vim mc ssh

RUN pip install click

#COPY . /var/www/html/

#RUN a2enmod rewrite ssl actions include cgi headers actions alias python




#  add Line in /etc/apache/apache2.conf via sed
#  Addhandler ModPython .py
#RUN sed -i '/<Directory \/var\/www\/>/,/<\/Directory>/ s/AllowOverride None$/AllowOverride None \n#added automatically\n        Addhandler cgi-script .py/' /etc/apache2/apache2.conf && \
#    sed -i '/<Directory \/var\/www\/>/,/<\/Directory>/ s/Options Indexes FollowSymLinks/Options Includes ExecCGI Indexes FollowSymLinks\n#added automatically\n        Addhandler cgi-script .py/' /etc/apache2/apache2.conf && \
#    sed -i 's/^#PermitRootLogin prohibit-password/# PermitRootLogin prohibit-password\n#added automatically\nPermitRootLogin yes/' /etc/ssh/sshd_config



RUN update-rc.d -f mysql defaults && \
    update-rc.d -f ssh defaults && \
    update-rc.d mysql enable && \
    update-rc.d apache2 enable && \
    update-rc.d ssh enable && \
    service ssh start



RUN groupadd wheel && \
    useradd  -d /home/lsusadmin -s /bin/bash -g wheel -c 'LSUS System User' ${LSUSADMIN}

RUN echo "root:r00t" | chpasswd && echo "lsusadmin:13UZ4dm.n" | chpasswd && echo 'set password'

RUN service mysql start && sleep 1 && mysql -u root -e "CREATE DATABASE lsus; GRANT ALL PRIVILEGES ON lsus.* TO 'lsusdba'@'%'IDENTIFIED BY 'lsusdba1'; GRANT ALL PRIVILEGES ON lsus.* TO 'lsusdba'@'localhost'IDENTIFIED BY 'lsusdba1'; FLUSH PRIVILEGES" && \
mysql -uroot lsus -e "SHOW TABLES;"

COPY . /var/www/html/

RUN service mysql start && sleep 1 && cd /var/www/html/bin && ./setup.py connection localhost lsusdba lsusdba1 lsus y && ./setup.py database lsus

# APACHE or lsusadmin +w
# sudo chmod a+w /var/www/html/conf/lsus.cfg

EXPOSE 80
EXPOSE 3306
EXPOSE 22


CMD ["/usr/sbin/apachectl", "-D", "FOREGROUND"]

#RUN service apache2 stop