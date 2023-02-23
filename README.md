# NMRL Serial to SQL Database Instrument Interface

This package provides a command line interface for:
1. RS-232 device connection.
2. Direct serial port read


## Setup

Make sure you have Mysql/MariaDb installed

    create databse create database db_name;

    # create user if you are using mysql: 
    create user 'username'@'%' identified with mysql_native_password by '<password>'; 
    GRANT ALL PRIVILEGES ON db_name.* TO 'username'@'%';
    
    # create user if you are using mariadb 
    grant all privileges on databse_name.* TO 'username'@'%' identified by '<password>';

    # finally 
    fush privileges;
    

Make sure you have installed python 3.9.5 or higher and pip3 for this project:

    $ python3 --version
    Python 3.X
    
    git clone https://github.com/NMRL-Zimbabwe/astm-improved.git
    cd astm-improved && sudo su
    pip3 install -r requirements.txt
    pip3 install -e .
    
    
Update configs 

    cd astm-improved/src/felicity/
    nano config.py  # and update as necessary
    


Make sure you have a working database before proceeding to this step

    # Run alembic migrations to generate our database tables
    cd astm-improved/src/felicity/
    bash ./al_upgrade.sh


Install the package as a simlink in order to local changes tracking:

    $ pip install -e .
    
    
ALl should be up by now: Check

    serial -s -p /dev/ttyUSB0
    # Listening .... etc
    
    
Setup supervisor for easier script management manager

    # install
    sudo apt update && sudo apt install supervisor
    
    # check status
    sudo systemctl status supervisor
    
    # add programs
    sudo nano /etc/supervisor/conf.d/astm_serial.conf
    
    # add any of the following programs based onavailable serial devices 
    [program:serial_usb0]
    command=/usr/bin/python3 /usr/local/bin/serial -s -p /dev/ttyUSB0
    autostart=true
    autorestart=true
    stderr_logfile=/var/log/serial_usb0.err.log
    stdout_logfile=/var/log/serial_usb0.out.log
   
    [program:serial_usb1]
    command=/usr/bin/python3 /usr/local/bin/serial -s -p /dev/ttyUSB1
    autostart=true
    autorestart=true
    stderr_logfile=/var/log/serial_usb1.err.log
    stdout_logfile=/var/log/serial_usb1.out.log

    [program:serial_s0]
    command=/usr/bin/python3 /usr/local/bin/serial -s -p /dev/ttyS0
    autostart=true
    autorestart=true
    stderr_logfile=/var/log/serial_s0.err.log
    stdout_logfile=/var/log/serial_s0.out.log
   
    [program:serial_s1]
    command=/usr/bin/python3 /usr/local/bin/serial -s -p /dev/ttyS1
    autostart=true
    autorestart=true
    stderr_logfile=/var/log/serial_s1.err.log
    stdout_logfile=/var/log/serial_s1.out.log
   
    # inform supervisor of our new programs
    sudo supervisorctl reread
    
    # tell superviror enact any changes
    sudo supervisorctl update
    
    
Supervisor management
    # check program status
    sudo supervisorctl status
    
    # reload all
    sudo supervisorctl reload
    
    # reload/ retart a single program
    sudo supervisorctl restart <program>
    
    # tail error logs
    sudo supervisorctl tail -f <program> stderr
    or tail -f /var/log/<program>.err.log
    
    # tail output logs
    sudo supervisorctl tail -f <program> stdout
    or tail -f /var/log/<program>.out.log
    
Done!
