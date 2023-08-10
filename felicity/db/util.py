from datetime import datetime, timedelta
from felicity.db.models import Orders, RawData
from felicity.logger import Logger
from felicity.helpers import has_special_char
from felicity.config import DB_CLEAR_DATA_OVER_DAYS

logger = Logger(__name__, __file__)


def sanitise(incoming):
    incoming = list(incoming)
    for index, item in enumerate(incoming):
        if isinstance(item, str):
            incoming[index] = item.replace(';', ' ').strip()
    return incoming


class DBOrderHandler:
    @staticmethod
    def clean():
        cutoff_date = datetime.now() - timedelta(days=DB_CLEAR_DATA_OVER_DAYS)
        logger.log("info", 
                   f"DBOrderHandler: cleaning raw messages and orders greater than {cutoff_date} == {DB_CLEAR_DATA_OVER_DAYS} days ago...")
        raws = RawData.find_all(filters={"created_at__le": cutoff_date})
        for raw in raws:
            orders = Orders.get_all(raw_data_uid=raw.uid)
            for order in orders:
                order.delete()
            raw.delete()
        logger.log("info", "DBOrderHandler: cleaning complete")

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
            # EID do repeat so need some hack to save more here

            #
            logger.log(
                "info", f"order with the same order_id ({order_id}) is already persisted, skipping ...")
            return

        hspc = has_special_char(order_id)
        Orders.create(**{
            "raw_data_uid": raw_data_uid,
            **order,
            "synced": 2 if hspc else 0,
            "sync_comment": "Incorrect Sample Id" if hspc else None
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

        hspc = has_special_char(order_id)
        found.update(**{
            "raw_data_uid": raw_data_uid,
            **order,
            "synced": 2 if hspc else 0,
            "sync_comment": "Incorrect Sample Id" if hspc else None
        })


if __name__ == "__main__":
    DBOrderHandler().clean()