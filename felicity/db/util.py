from felicity.db.models import Orders, RawData
from felicity.logger import Logger

logger = Logger(__name__, __file__)


class DBOrderHandler:

    def persist_raw(self, message):
        raw_data = RawData.create(**{"content": str(message)})
        return raw_data.uid

    def _has_special_char(order_id):
        """
        Check if order_id contains any special characters other than hyphens.

        Args:
            order_id (str): The order ID to check.

        Returns:
            bool: True if order_id contains special characters other than hyphens, False otherwise.
        """
        special_chars = list("~`!@#$%^&*()+=[]{}\\|;:'\",.<>/?")
        for char in order_id:
            if char in special_chars and char != "-":
                return True
        return False

    def persist_order(self, order, raw_data_uid):
        order_id = order["order_id"]
        filters = {
            'order_id': order_id
        }
        found = Orders.get(**filters)
        if found:
            logger.log(
                "info", f"order with the same order_id ({order_id}) is already persisted, skipping ...")
            return

        Orders.create(**{
            "raw_data_uid": raw_data_uid,
            **order,
            "synced": 5 if self._has_special_char(order_id) else 0

        })

    def update_order_fix(self, order, raw_data_uid):
        order_id = order["order_id"]
        filters = {
            'order_id': order_id
        }
        found = Orders.get(**filters)
        if not found:
            logger.log(
                "info", f"order with the same order_id ({order_id}) is does not exist, skipping ...")
            return

        found.update(**{
            "raw_data_uid": raw_data_uid,
            **order,
            "synced": 5 if self._has_special_char(order_id) else 0
        })
