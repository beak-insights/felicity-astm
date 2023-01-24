from felicity.db.models import Order, RawData
from felicity.logger import Logger

logger = Logger(__name__, __file__)


class DBOrderHandler:

    def persist_order(self, order, raw):
        filters = {
            'order_id': order["order_id"]
        }
        found = Order.get(**filters).all()
        if found:
            logger.log(
                "info", f"order with the same order_id is already persisted, skipping ... {order}")
            return
        raw_data = RawData.create(**{"content": str(raw)})
        Order.create(**{
            "raw_data_uid": raw_data.uid,
            **order
        })
