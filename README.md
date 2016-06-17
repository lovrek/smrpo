### dev environment setup
1. install virtualbox
2. install vagrant
3. cd into project dir
4. run **vagrant up** command
5. run **vagrant ssh** command
6. run **runserver** command
7. open your browser and go to 192.168.99.100:8000

### upgrade (local, deployment)
- run the **upgrade** command

### additional useful vagrant commands
- to shutdown the vm run the **vagrant halt** command
- if you want to destroy the vm run the **vagrant destroy** command
- cache ubuntu image with **vagrant box add ubuntu/trusty64** command
- check your vms with the **vagrant global-status** command

### local db
- name: smrpo_db
- user: smrpo_db_user
- password: smrpo_uber_secure

### local phpmyadmin
- 192.168.99.100/phpmyadmin
- username: root
- password: smrpo_uber_secure

### administration
- /admin
- username: admin
- password: smrpo_uber_secure
- reset locked ips: manage.py axes_reset

### fill database 
- sudo python3.4 /vagrant/smrpo/data_scripts/main.py

### fixed database - create new
- sudo mysql -uroot -psmrpo_uber_secure -e "CREATE DATABASE smrpo_db CHARACTER SET utf8 COLLATE utf8_general_ci"
- sudo mysql -uroot -psmrpo_uber_secure -e "grant all privileges on smrpo_db.* to 'smrpo_db_user'@'localhost' identified by 'smrpo_uber_secure'"

