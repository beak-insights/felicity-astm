from felicity.db.models import Orders, RawData
from felicity.logger import Logger

logger = Logger(__name__, __file__)


class DBOrderHandler:

    def persist_order(self, order, raw):
        filters = {
            'order_id': order["order_id"]
        }
        found = Orders.get(**filters)
        if found:
            logger.log(
                "info", f"order with the same order_id is already persisted, skipping ... {order}")
            return
        raw_data = RawData.create(**{"content": str(raw)})
        Orders.create(**{
            "raw_data_uid": raw_data.uid,
            **order
        })
