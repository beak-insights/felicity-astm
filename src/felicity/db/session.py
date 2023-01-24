from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from felicity.logger import Logger

from felicity.config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST

logger = Logger(__name__, __file__)

db_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?charset=utf8mb4"

engine = create_engine(db_url, pool_pre_ping=True, echo=False, future=True)
# session = scoped_session(sessionmaker(bind=engine, autocommit=True))


def test_db_connection() -> bool:
    try:
        with Session(engine) as session:
            result = session.execute(text("""select * from orders limit 1"""))
        logger.log("info", f"HL7DB: connection established")
        return True
    except Exception as e:
        logger.log("error", f"HL7DB: connection failed with error: {e}")
        return False
