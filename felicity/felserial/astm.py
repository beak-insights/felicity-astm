import threading
from felicity.logger import Logger
from felicity.felserial.handler import MessageHandler
from felicity.felserial.repository import OrderRepository

logger = Logger(__name__, __file__)


#: Message start token.
STX = '\x02'
#: Message end token.
ETX = '\x03'
#: ASTM session termination token.
EOT = '\x04'
#: ASTM session initialization token.
ENQ = '\x05'
#: Command accepted token.
ACK = '\x06'
#: Command rejected token.
NAK = '\x15'
#: Message chunk end token.
ETB = '\x17'
LF = '\x0A'
CR = '\x0D'
#: CR + LF shortcut.
CRLF = CR + LF

MAPPINGS = {
    STX: "<STX>",
    ETX: "<ETX>",
    EOT: "<EOT>",
    ENQ: "<ENQ>",
    ACK: "<ACK>",
    NAK: "<NAK>",
    ETB: "<ETB>",
    LF: "<LF>",
    CR: "<CR>",
    CRLF: "<CR><LF>"
}


class Message(object):
    """A collection of related information on a single topic, used here to mean
    all the identity, tests, and comments sent at one time. When used with
    Specification E 1394, this term means a record as defined by Specification
    E 1394
    """

    frames = None

    def __init__(self):
        self.frames = []

    def add_frame(self, frame):
        if self.can_add_frame(frame):
            self.frames.append(frame)

    def can_add_frame(self, frame):
        """A frame should be rejected because:
        (1) Any character errors are detected (parity error, framing
            error, etc.),
        (2) The frame checksum does not match the checksum computed on the
            received frame,
        (3) The frame number is not the same as the last accepted frame or one
            number higher (modulo 8).
        """
        if not frame.is_valid():
            return False
        if frame.fn != (len(self.frames)+1) % 8:
            logger.log("info", " No valid frame: FN is not consecutive")
            return False
        if self.is_complete():
            logger.log("info", "No valid frame: Message is complete")
            return True
        return not self.is_complete()

    def is_complete(self):
        if self.is_empty():
            return False
        return self.frames[-1].is_final

    def is_empty(self):
        return not self.frames

    def is_incomplete(self):
        if self.is_empty():
            return False
        return not self.frames[-1].is_final

    def text(self):
        texts = list(map(lambda frame: frame.text, self.frames))
        return CRLF.join(texts)


class Frame(object):
    """A subdivision of a message, used to allow periodic communication
    housekeeping such as error checks and acknowledgements
    """
    frame = None

    def __init__(self, frame):
        """
        The frame structure is illustrated as follows:
            <STX> FN text <ETB> C1 C2 <CR> <LF>  intermediate frame
            <STX> FN text <ETX> C1 C2 <CR> <LF>  end frame
        where:
            <STX> Start of Text transmission control character
            FN    single digit Frame Number 0 to 7
            text  Data Content of Message
            <ETB> End of Transmission Block transmission control character
            <ETX> 5 End of Text transmission control character
            C1    5 most significant character of checksum 0 to 9 and A to F
            C2    5 least significant character of checksum 0 to 9 and A to F
            <CR> 5 Carriage Return ASCII character
            <LF> 5 Line Feed ASCII character

        Any characters occurring before the <STX> or after the end of the
        block character (the <ETB> or <ETX>) are ignored by the receiver when
        checking the frame.
        """
        if STX in frame:
            self.frame = frame[frame.index(STX):]

    @property
    def fn(self):
        """Frame Number: The frame number permits the receiver to distinguish
        between new and retransmitted frames. It is a single digit sent
        immediately after the <STX> character.
        The frame number is an ASCII digit ranging from 0 to 7. The frame number
        begins at 1 with the first frame of the Transfer phase. The frame number
        is incremented by one for every new frame transmitted. After 7, the
        frame number rolls over to 0, and continues in this fashion.
        """
        return int(self.frame[1])

    @property
    def text(self):
        """Data content of the frame
        """
        end = self.is_intermediate and ETB or ETX
        return self.frame[2:self.frame.index(end)]

    @property
    def is_intermediate(self):
        """A message containing more than 240 characters are sent in
        intermediate frames with the last part of the message sent in an end
        frame. Intermediate frames terminate with the characters <ETB>,
        checksum, <CR> and <LF>
        """
        return ETB in self.frame and self.frame.index(ETB) >= 2

    @property
    def is_final(self):
        """A message containing 240 characters or less is sent in a single end
        frame. End frames terminate with the characters <ETX>, checksum, <CR>
        and <LF>
        """
        return ETX in self.frame and self.frame.index(ETX) >= 2

    @property
    def checksum_characters(self):
        """
        Checksum: The checksum permits the receiver to detect a defective
        frame. The checksum is encoded as two characters which are sent after
        the <ETB> or <ETX> character.
        """
        end = self.is_intermediate and ETB or ETX
        return self.frame[self.frame.index(end)+1:len(self.frame)-2]

    def is_valid(self):
        """Returns false if
        (1) Any character errors are detected (parity error, framing
            error, etc.),
        (2) The frame checksum does not match the checksum computed on the
            received frame,
        :return:
        """
        if not self.frame or len(self.frame) < 7:
            logger.log("info", " No valid frame: len < 7")
            return False

        if self.frame[0] != STX:
            logger.log("info", " No valid frame: STX not found")
            return False

        if self.frame[-2:] != CRLF:
            logger.log("info", " No valid frame: CRLF not found")
            return False

        if not self.is_valid_fn():
            return False

        if all([self.is_intermediate, self.is_final]):
            # Both intermediate and final (ETB + ETX)
            logger.log("info", " No valid frame: ETB + ETX")
            return False

        if not any([self.is_intermediate, self.is_final]):
            # Neither intermediate nor final
            logger.log("info", " No valid frame: ETB or ETX is missing")
            return False

        # Leave the checksum check for later
        # return self.is_valid_checksum()
        return True

    def is_valid_fn(self):
        fn = -1
        try:
            fn = self.fn
        except:
            logger.log("info", " No valid frame: FN")
            return False
        if fn < 0:
            logger.log("info", " No valid frame: FN < 0")
            return False
        if fn > 7:
            logger.log("info", " No valid frame: FN > 7")
            return False
        return True

    def has_text(self):
        try:
            return len(self.text) > 0
        except:
            logger.log("info", "  No valid frame: No text")
            return False

    def calculate_checksum(self):
        """Checksum: The checksum permits the receiver to detect a defective
        frame. The checksum is encoded as two characters which are sent after
        the <ETB> or <ETX> character. The checksum is computed by adding the
        binary values of the characters, keeping the least significant eight
        bits of the result.

        The checksum is initialized to zero with the <STX> character. The first
        character used in computing the checksum is the frame number. Each
        character in the message text is added to the checksum (modulo 256).
        The computation for the checksum does not include <STX>, the checksum
        characters, or the trailing <CR> and <LF>.

        The checksum is an integer represented by eight bits, it can be
        considered as two groups of four bits. The groups of four bits are
        converted to the ASCII characters of the hexadecimal representation. The
        two ASCII characters are transmitted as the checksum, with the most
        significant character first.

        For example, a checksum of 122 can be represented as 01111010 in binary
        or 7A in hexadecimal. The checksum is transmitted as the ASCII character
        7 followed by the character A.
        """
        end = self.is_intermediate and ETB or ETX
        seed = list(map(ord, self.frame[1:self.frame.index(end) + 1]))
        return hex(sum(seed) & 0xFF)[2:].upper().zfill(2).encode()

    def is_valid_checksum(self):
        try:
            expected = self.calculate_checksum()
            if expected == self.checksum_characters:
                return True
        except:
            pass
        logger.log("info", " No valid frame: checksum")
        return False


class ASTMHandler(MessageHandler):

    establishment = False
    messages = None
    response = None

    @property
    def current_message(self):
        return self.messages and self.messages[-1] or Message()

    def is_open(self):
        return self.messages is not None

    def is_busy(self):
        return self.response is not None

    def open(self):
        logger.log("info", "Opening session")
        self.messages = []
        self.response = None
        self.establishment = False

    def close(self):
        logger.log("info", "Closing session: neutral state")
        self.messages = None
        self.establishment = False

    def to_str(self, command):
        if not command:
            return "EMPTY"

        if len(command) > 1:
            items = list(filter(None, list(command)))
            items = "".join(list(map(self.to_str, items)))
            return items

        if command in MAPPINGS:
            return MAPPINGS[command]

        return command

    def write(self, command):
        logger.log("info", f"-> {self.to_str(command)}")
        if command == ENQ:
            # Initiate establishment phase
            self.handle_enq()
            return

        if self.establishment:
            # Establishment phase has been initiated already and we are now in
            # Transfer phase
            if STX in command:
                self.handle_frame(command)
                return

            elif EOT in command:
                # Received an End Of Transmission. Resume and enter to neutral
                # state
                self.handle_eot(command)
                return

            else:
                logger.log(
                    "info", " No valid message. No <STX> or <EOT> received")
        else:
            logger.log("info", "Establishment phase not initiated")

        self.response = NAK

    def handle_enq(self):
        logger.log("debug", "Initiating Establishment Phase ...")
        if self.is_busy():
            """
            A receiver that cannot immediately receive information, replies with
            the <NAK> transmission control character. Upon receiving <NAK>, the 
            sender must wait at least 10 s before transmitting another <ENQ>
            """
            logger.log("info", " Receiver is busy")
            self.response = NAK
        else:
            """
            The system with information available initiates the establishment 
            phase. After the sender determines the data link is in a neutral 
            state, it transmits the <ENQ> transmission control character to the 
            intended receiver. Sender will ignore all responses other than 
            <ACK>, <NAK>, or <ENQ>.
            """
            logger.log("info", "Ready for Transfer Phase ...")
            self.establishment = True
            self.response = ACK

    def handle_frame(self, frame_string):
        """
        The receiver replies to each frame. When it is ready to receive the
        next frame, it transmits one of three replies to acknowledge the last
        frame. This reply must be transmitted within the timeout period of 15s

        A reply of <NAK> signifies the last frame was not successfully received
        and the receiver is prepared to receive the frame again

        A reply of <ACK> signifies the last frame was received successfully and
        the receiver is prepared to receive another frame. The sender must
        increment the frame number and either send a new frame or terminate.

        A receiver checks every frame to guarantee it is valid. A reply of
        <NAK> is transmitted for invalid frames. Upon receiving the <NAK>, the
        sender retransmits the last frame with the same frame number. In this
        way, transmission errors are detected and automatically corrected.
        """
        # Not successfully received or wrong. Reply <NAK>
        frame = Frame(frame_string)
        if not frame.is_valid():
            self.response = NAK
            return

        message = self.current_message
        if not message.can_add_frame(frame):
            logger.log("info", " Cannot add frame to message")
            self.response = NAK
            return

        # Successfully received. Reply <ACK>
        logger.log("debug", " Frame accepted")
        message.add_frame(frame)

        self.messages.append(message)
        if message.is_complete():
            logger.log("info", "Message completed:")
            # Print out the message
            self.notify_message(message)
        else:
            logger.log("info", " Waiting for a new frame ...")

        self.response = ACK

    def handle_eot(self, command):
        """Handles an End Of Transmission message
        """
        logger.log("info", "Transfer phase completed")
        message = self.current_message
        if message and message.is_incomplete():
            logger.log("info", "Incomplete message:")
            self.notify_message(message)

        self.response = ACK
        self.close()

    def notify_message(self, message):
        """Prints the messaged in stdout
        """
        if not message:
            return

        print("-" * 80)
        print(message.text())
        print("-" * 80)

    def read(self):
        if self.response:
            logger.log("debug", "<- {}".format(self.to_str(self.response)))
        resp = self.response
        self.response = None
        return resp


class ASTMTOrderHandler(ASTMHandler):

    _received_messages = list()

    def handle_eot(self, command):
        logger.log("info", "Transfer phase completed")
        message = self.current_message
        if message and message.is_incomplete():
            # Don't push to result repository. This is an incomplete message!
            logger.log("error", "[SKIP] Incomplete message:")
            super(ASTMTOrderHandler, self).notify_message(message)

        elif not self._received_messages:
            # Don't push to result repository. There are no messages to send
            logger.log("warn", "[SKIP] There is no message to send")
            super(ASTMTOrderHandler, self).notify_message(message)

        else:
            # Send to result repository in a new Thread
            messages = list(self._received_messages)
            thread = threading.Thread(target=self.push_to_order_repository,
                                      args=(messages,))
            thread.start()

        # Go to neutral state
        self._received_messages = list()
        self.response = None
        self.close()

    def notify_message(self, message):
        super(ASTMTOrderHandler, self).notify_message(message)
        if message and message.text():
            self._received_messages.append(message.text())

    def push_to_order_repository(self, messages):
        if isinstance(messages, str):
            messages = [messages]

        result_repository = OrderRepository()

        while len(messages) > 0:
            msg = messages.pop()
            result_repository.handle_order_message(msg)

    def close(self):
        super(ASTMTOrderHandler, self).close()
        self._received_messages = list()
