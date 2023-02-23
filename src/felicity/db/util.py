from felicity.db.models import Orders, RawData
from felicity.logger import Logger

logger = Logger(__name__, __file__)


class DBOrderHandler:

    def persist_raw(self, message):
        raw_data = RawData.create(**{"content": str(message)})
        return raw_data.uid

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
            **order
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
            "synced": found.synced,
            "sync_date": found.sync_date,
        })
