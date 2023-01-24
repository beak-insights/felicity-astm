# -*- coding: utf-8 -*-

import argparse
import sys

import serial
from serial.tools import list_ports
from serial.serialutil import to_bytes
from felicity.felserial.astm import ASTMTOrderHandler

"""Serial Command Line Tools

Insatallation: pip instal -e .
Usage: serial --help
"""


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

    # Start the server
    if args.server:
        start_server(args.port)


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


if __name__ == "__main__":
    trial()
