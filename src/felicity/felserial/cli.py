# -*- coding: utf-8 -*-

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor

import serial
from serial.tools import list_ports
from serial.serialutil import to_bytes
from felicity.felserial.astm import ASTMTOrderHandler
from felicity.forward import start_fowading

from felicity.logger import Logger
logger = Logger(__name__, __file__)

"""Serial Command Line Tools

Insatallation: pip instal -e .
Usage: serial --help
"""


def run_in_parallel(tasks):
    with ThreadPoolExecutor() as executor:
        running_tasks = [executor.submit(task) for task in tasks]
        for running_task in running_tasks:
            running_task.result()


def start_server(port, baudrate=9600, handler=None):
    """Start serial server
    """

    if handler is None:
        handler = ASTMTOrderHandler()

    with serial.Serial(port, baudrate, timeout=2) as ser:
        print("Listening on port {}, press Ctrl+c to exit.".format(port))
        while True:
            line = ser.readline().decode(encoding="utf-8")
            if line:
                # Is this a new session?
                if not handler.is_open():
                    handler.open()

                # Notify the receiver with the new message
                handler.write(line)

                # Does the receiver has to send something back?
                response = handler.read()
                if response:
                    if isinstance(response, str):
                        # convert to bytes
                        response = response.encode()
                    socket = serial.Serial(port, baudrate, timeout=10)
                    socket.write(to_bytes(response))


def main():

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "-s",
        "--server",
        action="store_true",
        help="Start the serial server tool"
    )

    parser.add_argument(
        "-p",
        "--port",
        type=str,
        default="/dev/ttys002",
        help="COM Port to connect"
    )

    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="List available ports"
    )

    args = parser.parse_args()

    # List available ports
    if args.list:
        sys.argv = ["--include-links", "-v"]
        list_ports.main()
        sys.exit(0)

    # Start the servers
    if args.server:
        run_in_parallel([
            lambda: start_server(args.port),
            lambda: start_fowading()
        ])


def trial():
    from felicity.felserial.repository import OrderRepository
    msg = """
    H|\^&|||m2000^8.1.9.0^275022112^H1P1O1R1C1L1|||||||P|1|20190903162134
    P|1
    O|1|DBS19-002994|DBS19-002994^WS19-2459^D1|^^^HIV1mlDBS^HIV1.0mlDBS|||||||||||||||||||||F
    R|1|^^^HIV1mlDBS^HIV1.0mlDBS^489932^11790271^^F|< 839|Copies / mL||||R||naralabs^naralabs||20190902191654|275022112
    R|2|^^^HIV1mlDBS^HIV1.0mlDBS^489932^11790271^^I|Detected|||||R||naralabs^naralabs||20190902191654|275022112
    R|3|^^^HIV1mlDBS^HIV1.0mlDBS^489932^11790271^^P|28.21|cycle number||||R||naralabs^naralabs||20190902191654|275022112
    """
    OrderRepository().handle_order_message(msg)


def hl7Try():
    from felicity.felserial.repository import OrderRepository
    hl_mess = """
    MSH|^~\&|COBAS6800/8800||LIS||20230123104355||OUL^R22|13968052-baa9-474c-91bb-f7cf19d988fe|P|2.5||||||ASCII
    SPM||BP23-04444||PLAS^plasma^HL70487|||||||P||||||||||||||||
    SAC|||||||||||||||||||||500|||uL^^UCUM
    OBR|1|||70241-5^HIV^LN|||||||A
    OBX|1|ST|HIV^HIV^99ROC||ValueNotSet|||BT|||F|||||Lyna||C6800/8800^Roche^^~Unknown^Roche^^~ID_000000000012076380^IM300-002765^^|20230120144614|||||||||386_neg^^99ROC~385_pos^^99ROC
    TCD|70241-5^HIV^LN|^1^:^0
    OBX|2|NA|HIV^HIV^99ROC^S_OTHER^Other Supplemental^IHELAW||41.47^^37.53||||||F|||||Lyna||C6800/8800^Roche^^~Unknown^Roche^^~ID_000000000012076380^IM300-002765^^|20230120144614|||||||||386_neg^^99ROC~385_pos^^99ROC
    OBX|3|ST|70241-5^HIV^LN|1/1|ValueNotSet|||RR|||F|||||Lyna||C6800/8800^Roche^^~Unknown^Roche^^~ID_000000000012076380^IM300-002765^^|20230120144614|||||||||386_neg^^99ROC~385_pos^^99ROC
    OBX|4|ST|70241-5^HIV^LN|1/2|< Titer min|||""|||F|||||Lyna||C6800/8800^Roche^^~Unknown^Roche^^~ID_000000000012076380^IM300-002765^^|20230120144614|||||||||386_neg^^99ROC~385_pos^^99ROC
    TCD|70241-5^HIV^LN|^1^:^0
    """
    OrderRepository().handle_order_message(hl_mess)


if __name__ == "__main__":
    hl7Try()
