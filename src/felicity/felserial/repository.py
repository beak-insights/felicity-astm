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
        payloads = self.converter.process(message)
        if isinstance(payloads, dict):
            payloads = [payloads]
        for order in payloads:
            order = self._to_order(order)
            logger.log("info", f"order for db {order}")
            self.database.persist_order(order, message)

    @staticmethod
    def _to_order(message):
        id = message.get("id")
        return {
            "order_id": id,
            "test_id": id,
            "keywork": message.get("keyword"),
            "result": message.get("result"),
            "result_date": message.get("capture_date")
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
