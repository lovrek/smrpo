#!/bin/sh

cd /vagrant
git pull origin master
sudo pip3 install -r /vagrant/requirements.txt
sudo service mysql restart
python3.4 /vagrant/smrpo/manage.py migrate
python3.4 /vagrant/smrpo/manage.py compilemessages
sudo service apache2 restart
