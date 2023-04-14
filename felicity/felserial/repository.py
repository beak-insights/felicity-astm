# -*- coding: utf-8 -*-

from felicity.logger import Logger
from felicity.db import DBOrderHandler
from felicity.felserial.converter import ASTMSerialHandler

logger = Logger(__name__, __file__)


class OrderRepository:

    def __init__(self):
        self._converter = None
        self._database = None

    def handle_order_message(self, message):
        # persist raw_data
        rawdata_uid = self.database.persist_raw(message)

        payloads = self.converter.process(message)
        if isinstance(payloads, dict):
            payloads = [payloads]

        # persist message splits as orders
        for order in payloads:
            order = self._to_order(order)
            order_id = order.get("order_id", None)
            order_result = order.get("result", None)
            logger.log(
                "info", f"order for db:: order_id -> {order_id} -> result -> {order_result}")
            self.database.persist_order(order, rawdata_uid)

    def handle_replay(self, raw_data):
        payloads = self.converter.process(raw_data.content)
        if isinstance(payloads, dict):
            payloads = [payloads]

        # persist message splits as orders
        for order in payloads:
            order = self._to_order(order)
            order_id = order.get("order_id", None)
            order_result = order.get("result", None)
            logger.log(
                "info", f"order for db:: order_id -> {order_id} -> result -> {order_result}")
            self.database.persist_order(order, raw_data.uid)

    def update_fix(self, raw_data):
        """For updating old messages fix"""
        payloads = self.converter.process(raw_data.content)
        if isinstance(payloads, dict):
            payloads = [payloads]

        # persist message splits as orders
        for order in payloads:
            order = self._to_order(order)
            logger.log("info", f"order for update: {order}")
            self.database.update_order_fix({
                "order_id": order['order_id'],
                "result": order['result'],
                "raw_message": order['raw_message']
            }, raw_data.uid)

    @staticmethod
    def _to_order(message):
        id = message.get("id")
        return {
            "order_id": id,
            "test_id": id,
            "keywork": message.get("keyword"),
            "result": message.get("result"),
            "result_date": message.get("capture_date"),
            "raw_message": message.get("raw_message")
        }

    @property
    def database(self):
        if not self._database:
            self._database = DBOrderHandler()
        return self._database

    @property
    def converter(self):
        if not self._converter:
            self._converter = ASTMSerialHandler()
        return self._converter
