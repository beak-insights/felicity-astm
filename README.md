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
    flush privileges;
    

Make sure you have installed Python 3.9.5 or higher and pip3 for this project:
You can download Miniconda for ease of installation and accept licence and answer yes everywhere

    $ wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-s390x.sh
    $ bash Miniconda3-latest-Linux-s390x.sh

Check python version 

    $ python3 --version or python --version
    Python 3.x.x
    
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
    
    
Check for the latest device connected to your computer by:
    
    $ s -lh /dev/
    

### Simulation Tests
Simulation test with socat:

    $ sudo apt-get install socat
    $ socat -d -d pty,raw,echo=0 pty,raw,echo=0
    2019/05/27 09:49:54 socat[19584] N PTY is /dev/pts/5
    2019/05/27 09:49:54 socat[19584] N PTY is /dev/pts/6
    2019/05/27 09:49:54 socat[19584] N starting data transfer loop with FDs [5,5] and [7,7]

    
Start the receiver (serial):

    $ serial -s -p /dev/pts/6
    
    
Simulate the receiver (instrument):

    $ echo -n -e '\x05' > /dev/pts/5
    Opening session
    -> <ENQ>
    Initiating Establishment Phase ...
    Ready for Transfer Phase ...
    <- <ACK>
       
    $ echo -n -e '\x021This is my first and last frame\x03F0\x0D\x0A' > /dev/pts/5
    -> <STX>1This is my first and last frame<ETX>F0<CR><LF>
     Frame accepted
    Transfer phase completed:
    --------------------------------------------------------------------------------
    This is my first and last frame
    --------------------------------------------------------------------------------
    Closing session: neutral state
    <- <ACK>
    
    $ echo -n -e '\x05' > /dev/pts/5
    $ echo -n -e '\x021This is my first frame\x17F0\x0D\x0A' > /dev/pts/5
    $ echo -n -e '\x022This is my second frame\x17F0\x0D\x0A' > /dev/pts/5
    $ echo -n -e '\x023This is my third frame\x17F0\x0D\x0A' > /dev/pts/5
    $ echo -n -e '\x024This is my fourth and last frame\x03F0\x0D\x0A' > /dev/pts/5
    Opening session
    -> <ENQ>
    Initiating Establishment Phase ...
    Ready for Transfer Phase ...
    <- <ACK>
    -> <STX>1This is my first frame<ETB>F0<CR><LF>
     Frame accepted
     Waiting for a new frame ...
    <- <ACK>
    -> <STX>2This is my second frame<ETB>F0<CR><LF>
     Frame accepted
     Waiting for a new frame ...
    <- <ACK>
    -> <STX>3This is my third frame<ETB>F0<CR><LF>
     Frame accepted
     Waiting for a new frame ...
    <- <ACK>
    -> <STX>4This is my fourth and last frame<ETX>F0<CR><LF>
     Frame accepted
    Transfer phase completed:
    --------------------------------------------------------------------------------
    This is my first frame
    This is my second frame
    This is my third frame
    This is my fourth and last frame
    --------------------------------------------------------------------------------
    Closing session: neutral state
    <- <ACK>
 
 
### Real Insrtument Setup
Serial ports are mostly set with a baudrate of 9600 by default, but you can modify these settings with stty command, if needed. Eg:
    
    $ sudo stty -F /dev/ttyUSB0 9600
    
    
The same command, but without specifying the baudrate will give you the actual configuration
 
    $ sudo stty -F /dev/ttyUSB0
    speed 9600 baud; line = 0;
    -brkint -imaxbel
    
Al should be up by now: Check

    serial -s -p /dev/ttyUSB0
    # Listening .... etc
    
    
### Serial Management with supervisor
Setup supervisor for easier script management manager

installation:

    $ sudo apt update && sudo apt install supervisor
    
    
check status:

    $ sudo systemctl status supervisor
    
open supervisor config file:

    $ sudo nano /etc/supervisor/conf.d/astm_serial.conf
    

Copy and Paste any of the following programs based on available serial devices 

    [program:result_forward]
    command=/usr/bin/python3 /usr/local/bin/serial -f
    autostart=true
    autorestart=true
    stderr_logfile=/var/log/result_forward.err.log
    stdout_logfile=/var/log/result_forward.out.log
    
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


If you used miniconda to install python modify the above `command` to point to miniconda accordingly.

    command=/home/administrator/miniconda3/bin/python /home/administrator/miniconda3/bin/serial -f
    command=/home/administrator/miniconda3/bin/python /home/administrator/miniconda3/bin/serial -s -p /dev/ttyUSB0
    command=/home/administrator/miniconda3/bin/python /home/administrator/miniconda3/bin/serial -s -p /dev/ttyUSB1

   
inform supervisor of our new programs:

    $ sudo supervisorctl reread
    

tell superviror enact any changes:

    $ sudo supervisorctl update
    
    
##### Supervisor management commands
check program status:

    $ sudo supervisorctl status
    
    
reload all services

    $ sudo supervisorctl reload


reload or retart a single program:
    
    $ sudo supervisorctl restart <program>
    

tail error logs:

    $ sudo supervisorctl tail -f <program> stderr
    or tail -f /var/log/<program>.err.log
    
tail output logs:

    $ sudo supervisorctl tail -f <program> stdout
    or tail -f /var/log/<program>.out.log
    
    
View Serial Dashboard
    
    $ serial -d
    
   
Navigate to the dashboard [http://127.0.0.1:9999](http://127.0.0.1:9999)
    
Done!
