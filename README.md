# Senaite Serial to SQL Database Instrument Interface

This package provides a command line interface for:
1. RS-232 device connection.


## Setup

Make sure you have Mysql/MariaDb installed

    create databse create database db_name;

    # create user if you are using mysql: 
    create user 'username'@'%' identified with mysql_native_password by '<password>'; 
    GRANT ALL PRIVILEGES ON db_name.* TO 'username'@'%';
    
    # create user if you are using mariadb 
    grant all privileges on databse_name.* TO 'username'@'%' identified by '<password>';

    finally fush privileges
    

Make sure you have installed python 3.9.5 or higher and pip3 for this project:

    $ python3 --version
    Python 3.X
    
    git clone https://github.com/NMRL-Zimbabwe/astm-to-db.git
    cd astm-to-db && sudo su
    pip3 install alembic==1.9.2 sqlalchemy==1.4.31 pyserial==3.5 pymysql requests
   
    pip3 install -e .
    
    
Update configs 

    cd astm-to-db/src/felicity/
    nano config.py  and update as necessary


Make sure you have a working database before proceeding to this step

    # from inside astm-to-db/src/felicity/ do
    bash ./al_upgrade.sh

Install the package for development:

    $ pip install -e .
    
    
ALl should be up by now: Check

    serial -s -p /dev/ttyUSB0
    # Listening ....
    

Create cron job to automaticaly run serial
    
    cd /dev/init.d/
    touch initserial
    
    cat <<EOT >> initserial
    /usr/bin/python3 /usr/local/bin/serial -s -p /dev/ttyS0 &
    /usr/bin/python3 /usr/local/bin/serial -s -p /dev/ttyUSB0 &
    EOT
    
    
    crontab -e
    @reboot /etc/init.d/initserial
    
Done!
    
    

