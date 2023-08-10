# -*- coding: utf-8 -*-

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor

import serial
from serial.tools import list_ports
from serial.serialutil import to_bytes
from felicity.felserial.astm import ASTMTOrderHandler
from felicity.forward import start_fowading
from felicity.dashboard import start_dashboard

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

    parser.add_argument(
        "-f",
        "--forward",
        action="store_true",
        help="Foward Results to LIMS"
    )

    parser.add_argument(
        "-d",
        "--dashboard",
        action="store_true",
        help="Start Admin Dashboard"
    )

    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Start All"
    )

    parser.add_argument(
        "-fm",
        "--fixmessages",
        action="store_true",
        help="Fix messages imported earlier"
    )

    parser.add_argument(
        "-r",
        "--replay",
        action="store_true",
        help="Repley messages import"
    )

    args = parser.parse_args()

    # List available ports
    if args.list:
        sys.argv = ["--include-links", "-v"]
        list_ports.main()
        sys.exit(0)

    # Start the servers
    if args.server:
        start_server(args.port)

    # Start the forwarder: serial -f
    if args.forward:
        start_fowading()

    # run admin interface: serial -d
    if args.dashboard:
        start_dashboard()

    # fix messages imported earlier
    if args.fixmessages:
        from felicity.felserial.repository import OrderRepository
        from felicity.db.models import RawData
        raw_data = RawData.all()
        for _raw in raw_data:
            OrderRepository().update_fix(_raw)

    # replay reimport results for raw_data
    if args.replay:
        from felicity.felserial.repository import OrderRepository
        from felicity.db.models import RawData, Orders
        for _order in Orders().all():
            _order.delete()

        raw_data = RawData.all()
        for _raw in raw_data:
            OrderRepository().handle_replay(_raw)

    # run all: for sites with a single maching connected: serial -a -p /dev/ttyUSB0
    if args.all:
        run_in_parallel([
            lambda: start_server(args.port),
            lambda: start_fowading(),
            lambda: start_dashboard()
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


def hpvTry():
    from felicity.felserial.repository import OrderRepository
    ms = """
    H|\^&|||Panther|||||Host||P|1|
    P|5||||^^|||||||||||^|^|||||||||||||||^|^|
    O|1|CS23-22443|cc72d06c-87de-463c-ad08-275211789126^451167|^^^HPV^HPV^^1|R|20230222142246|||||||||||||||||||F
    R|1|^^^HPV^ICRLU^^1|181107|||||F\R||||20230222192433|
    R|2|^^^HPV^ICInterpretation^^1|Valid|||||F\R||||20230222192433|
    R|3|^^^HPV^AnalyteRLU^^1|2746489|||||F\R||||20230222192433|
    R|4|^^^HPV^AnalyteSCO^^1|20.07|||||F\R||||20230222192433|
    R|5|^^^HPV^OverallInterpretation^^1|POSITIVE|||||F\R||||20230222192433|
    R|6|^^^HPV^Analyte Cutoff^^1||||||F\R||||20230222192433|
    R|7|^^^HPV^IC Cutoff^^1||||||F\R||||20230222192433|
    L|1|N
    """
    OrderRepository().handle_order_message(ms)


def err():
    from felicity.felserial.repository import OrderRepository
    ms = """
    H|\^&|||m2000^8.1.9.0^275022096^H1P1O1R1C1L1|||||||P|1|20230717163415
    P|1
    O|1|DB&E&23-33E22|DB&E&23-33E22^WS23-11684^D2|^^^HIV1mlDBS^HIV1.0mlDBS|||||||||||||||||||||F
    R|1|^^^HIV1mlDBS^HIV1.0mlDBS^381303^10003187^^F|Not detected|Copies / mL||||R||BRIAN PAKARIMWA^BRIAN PAKARIMWA||20230713214311|275022096
    R|2|^^^HIV1mlDBS^HIV1.0mlDBS^381303^10003187^^I|Target not detected|||||R||BRIAN PAKARIMWA^BRIAN PAKARIMWA||20230713214311|275022096
    R|3|^^^HIV1mlDBS^HIV1.0mlDBS^381303^10003187^^P|-1.00|cycle number||||R||BRIAN PAKARIMWA^BRIAN PAKARIMWA||20230713214311|275022096
    L|1
    """
    OrderRepository().handle_order_message(ms)


if __name__ == "__main__":
    hpvTry()
    # err()
    # hl7Try()
    # trial()