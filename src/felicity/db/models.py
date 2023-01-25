from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.dialects.mysql import LONGTEXT
from felicity.db.base_model import DBModel


class RawData(DBModel):
    __tablename__ = "raw_data"
    __table_args__ = {'extend_existing': True}

    content = Column(LONGTEXT, nullable=False)


class Order(DBModel):
    __tablename__ = "order"
    __table_args__ = {'extend_existing': True}

    order_id = Column(String(50), nullable=False)
    test_id = Column(String(50), nullable=True)
    keywork = Column(String(50), nullable=False)
    instrument = Column(String(50), nullable=True)
    result = Column(String(255), nullable=False)
    result_date = Column(String(25), nullable=False)
    unit = Column(String(20), nullable=True)
    comment = Column(String(255), nullable=True)
    is_sync_allowed = Column(Boolean, nullable=False, default=True)
    synced = Column(Boolean, nullable=False, default=False)
    sync_date = Column(String(25), nullable=True)
    sync_comment = Column(String(255), nullable=True)
    raw_data_uid = Column(
        Integer,
        ForeignKey("raw_data.uid", ondelete="CASCADE"),
        nullable=False
    )
