#!/bin/sh

DBNAME=smrpo_db
DBUSER=smrpo_db_user
DBPASSWD=smrpo_uber_secure

sudo apt-get update
sudo apt-get -y install git python3 python3-dev python3-pip apache2 gettext libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk

echo "mysql-server mysql-server/root_password password $DBPASSWD" | debconf-set-selections
echo "mysql-server mysql-server/root_password_again password $DBPASSWD" | debconf-set-selections
sudo apt-get -y --force-yes install mysql-server

mysql -uroot -p$DBPASSWD -e "CREATE DATABASE $DBNAME CHARACTER SET utf8 COLLATE utf8_general_ci"
mysql -uroot -p$DBPASSWD -e "grant all privileges on $DBNAME.* to '$DBUSER'@'localhost' identified by '$DBPASSWD'"
sudo service mysql restart
sudo apt-get -y install libmysqlclient-dev

echo "phpmyadmin phpmyadmin/dbconfig-install boolean true" | debconf-set-selections
echo "phpmyadmin phpmyadmin/app-password-confirm password $DBPASSWD" | debconf-set-selections
echo "phpmyadmin phpmyadmin/mysql/admin-pass password $DBPASSWD" | debconf-set-selections
echo "phpmyadmin phpmyadmin/mysql/app-pass password $DBPASSWD" | debconf-set-selections
echo "phpmyadmin phpmyadmin/reconfigure-webserver multiselect none" | debconf-set-selections
sudo apt-get -y --force-yes install phpmyadmin


sudo pip3 install -r /vagrant/requirements.txt
printf "export PYTHONPATH=\"${PYTHONPATH}:/usr/local/lib/python3.4/dist-packages\"\n" >> ~vagrant/.bashrc

python3.4 /vagrant/smrpo/manage.py migrate --fake-initial
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@smrpo.si', '$DBPASSWD')" | python3.4 /vagrant/smrpo/manage.py shell

printf "alias runserver='source /vagrant/runserver.sh'\n" >> ~vagrant/.bashrc
printf "alias upgrade='source /vagrant/upgrade_local.sh'\n" >> ~vagrant/.bashrc

export DB_NAME=$DBNAME
export DB_USER=$DBUSER
export DB_PASS=$DBPASSWD

sudo timedatectl set-timezone CET
sudo apt-get -y install ntp
sudo service ntp reload

echo ""
echo "Vagrant install complete."
echo "Now try logging in:"
echo "    $ vagrant ssh"
echo "When logged in run the django server:"
echo "    $ runserver\n"
echo "Web application is accessible on 192.168.99.100:8000"
echo "Phpmyadmin is accessible on 192.168.99.100/phpmyadmin"
