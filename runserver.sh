#!/bin/sh 
sudo service mysql restart 
python3.4 /vagrant/smrpo/manage.py runserver 0.0.0.0:8000