from felicity.db.models import Orders, RawData
from felicity.logger import Logger
from felicity.helpers import has_special_char

from sqlalchemy import text
from felicity.db.session import engine
from sqlalchemy.orm import Session
import pandas as pd

logger = Logger(__name__, __file__)


def fetch_astm_results():
    select_stmt = text(f"""select * from orders""")

    with Session(engine) as session:
        result = session.execute(select_stmt)

    return pd.DataFrame(
        [self.sanitise(line) for line in result.all()],
        columns=result.keys()
    )


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
            # EID do repeat so need some hack to save more here

            #
            logger.log(
                "info", f"order with the same order_id ({order_id}) is already persisted, skipping ...")
            return

        Orders.create(**{
            "raw_data_uid": raw_data_uid,
            **order,
            "synced": 5 if has_special_char(order_id) else 0
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
            "synced": 5 if has_special_char(order_id) else 0
        })
