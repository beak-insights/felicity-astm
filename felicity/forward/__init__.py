import time
from felicity.logger import Logger
from felicity.forward.engine import ResultInterface
from felicity.db.util import DBOrderHandler
from felicity.config import POLL_BD_EVERY

logger = Logger(__name__, __file__)


def commence_raw():
    ResultInterface().run()
    
def clean_database():
    DBOrderHandler().clean()

def commence_scheuled():
    import schedule

    # run now and schedule the nest jobs
    commence_raw()
    schedule.every(POLL_BD_EVERY).minutes.do(commence_raw)
    schedule.every().day.at("02:00").do(clean_database)

    while True:
        schedule.run_pending()
        time.sleep(10)


def start_fowading():
    logger.log("info", "Result forwarder started ...")
    commence_scheuled()
