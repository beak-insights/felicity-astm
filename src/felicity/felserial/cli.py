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
