import serial
import time

STX = '\x02'
ETX = '\x03'
EOT = '\x04'
ENQ = '\x05'
ACK = '\x06'
NAK = '\x15'
ETB = '\x17'
LF = '\x0A'
CR = '\x0D'
CRLF = CR + LF
CRETX = CR + ETX

socket = serial.Serial('/dev/pts/3', 9600, timeout=10)

msg1 = f"{ENQ}"
msg2 = f"{STX}1H|\^&|||m2000^8.1.9.0^275022122^H1P1O1R1C1L1|||||||P|1|20230124085422{CRETX}53{CRLF}"
msg3 = f"{STX}2P|1{CRETX}3F{CRLF}"
msg4 = f"{STX}3O|1|DBS23-02212|DBS23-02212^WS23-8671^A1|^^^HIV1mlDBS^HIV1.0mlDBS|||||||||||||||||||||F{CRETX}93{CRLF}"
msg5 = f"{STX}4R|1|^^^HIV1mlDBS^HIV1.0mlDBS^531516^10003166^^F|Not detected|Copies / mL||||F||csc^csc||20230123221132|275022122{CRETX}B4{CRLF}"
msg6 = f"{STX}5R|2|^^^HIV1mlDBS^HIV1.0mlDBS^531516^10003166^^I|Target not detected|||||F||csc^csc||20230123221132|275022122{CRETX}D5{CRLF}"
msg7 = f"{STX}6R|3|^^^HIV1mlDBS^HIV1.0mlDBS^531516^10003166^^P|-1.00|cycle number||||F||csc^csc||20230123221132|275022122{CRETX}49{CRLF}"
msg8 = f"{STX}7L|1{CRETX}40{CRLF}"
msg9 = f"{EOT}"

socket.write(msg1.encode())
socket.read()
time.sleep(3)
# socket.write(msg2.encode())
# socket.read()
time.sleep(3)
socket.write(msg3.encode())
socket.read()
time.sleep(3)
socket.write(msg4.encode())
time.sleep(3)
socket.write(msg5.encode())
time.sleep(3)
socket.write(msg6.encode())
time.sleep(3)
socket.write(msg7.encode())
time.sleep(3)
socket.write(msg8.encode())
time.sleep(3)
socket.write(msg9.encode())
