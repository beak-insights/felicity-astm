# -*- coding: utf-8 -*-
from collections import OrderedDict
from felicity.logger import Logger
from felicity.felserial.converter.adapter import astm_adapters, hl7_adapters

logger = Logger(__name__, __file__)


class ASTMSerialHandler:

    def process(self, message):
        # Message can contain multiple headers (one per Sample). In such case,
        # we need to process them independently
        protocol, blocks = self.split_message_blocks(message)

        # Skip messages without result record (R)
        blocks = list(filter(lambda b: "R|" in b or "OBX|" in b, blocks))

        # Remove empties and duplicates while keeping the order
        blocks = list(filter(None, blocks))
        blocks = list(OrderedDict.fromkeys(blocks))

        msgs = []
        for block in blocks:
            try:
                msgs += self.adapt_message(block, protocol)
            except Exception as e:
                logger.log("info", "msgs: {}".format(msgs))
                logger.log("info", "block: {}".format(block))

        return msgs

    def split_message_blocks(self, message):
        split = "H|\^&|"
        protocol = "astm"
        if "MSH|^~\&" in message:
            split = "MSH|^~\&"
            protocol = "hl7"
        blocks = list(filter(None, message.strip().split(split)))
        blocks = list(
            map(lambda msg: "{}{}".format(split, msg.strip()), blocks))
        return protocol, list(filter(None, blocks))

    def get_adapter(self, message, protocol):
        """Looks for a suitable subscriber adapters for the message passed in
        """
        # We only want the adapters that can read the message
        if protocol == "astm":
            adapters = astm_adapters
        else:
            adapters = hl7_adapters
        adapters = list(map(lambda ad: ad(message), adapters))
        adapters = list(filter(lambda ad: ad.is_supported(), adapters))

        if not adapters:
            return None

        if len(adapters) > 1:
            logger.log(
                "warn", "Multiple subscriber adapters found, returning first")

        return adapters[0]

    def adapt_message(self, message, protocol):
        """Imports the message's results to Senaite
        """
        msg = len(message) > 50 and "{}...".format(message[:47]) or message
        logger.log("info", "Importing message: {}".format(msg))
        adapter = self.get_adapter(message, protocol)

        if not adapter:
            logger.log("error", "No adapters found for message: {}".format(msg))
            return False

        # Read the message
        data = adapter.read()

        if not data:
            logger.log("error", "No data found for message: {}".format(msg))
            return False

        if isinstance(data, dict):
            data = [data]

        # Bail-out items without id/keyword
        data = list(filter(lambda d: self.is_valid_data(d), data))
        if not data:
            return False

        return data

    def is_valid_data(self, data):
        """Returns whether the ASTMDataResult has a valid id and keyword
        """
        values = [data["id"], data["keyword"], str(data["result"])]
        return all(list(map(self.is_valid_value, values)))

    def is_valid_value(self, val):
        """Returns whether the value passed in is non-empty and non-None
        """
        if isinstance(val, (list, tuple)):
            return all(list(map(self.is_valid_value, val)))
        if val is None:
            return False
        val = val.strip()
        if not val:
            return False
        return val != "None"
