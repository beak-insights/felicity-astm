import ssl
import json
import time
from time import sleep
import pandas as pd
from datetime import datetime
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.auth import HTTPBasicAuth
from sqlalchemy import text
from sqlalchemy.orm import Session
from felicity.config import (
    SENAITE_BASE_URL,
    SENAITE_API_URL,
    SENAITE_USER,
    SENAITE_PASSWORD,
    VERIFY_RESULT,
    SLEEP_SECONDS,
    SLEEP_SUBMISSION_COUNT,
    EXCLUDE_RESULTS,
    SEND_TO_QUEUE,
    API_MAX_ATTEMPTS,
    API_ATTEMPT_INTERVAL,
)
from felicity.db.session import engine, test_db_connection
from felicity.forward.result_parser import ResultParser
from felicity.logger import Logger


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
logger = Logger(__name__, __file__)


class FowardOrderHandler:

    @staticmethod
    def sanitise(incoming):
        incoming = list(incoming)
        for index, item in enumerate(incoming):
            if isinstance(item, str):
                incoming[index] = item.replace(';', ' ').strip()
        return incoming

    def fetch_astm_results(self):
        logger.log("info", f"AstmOrderHandler: Fetching astm result orders ...")
        select_stmt = text(
            """select * from orders o where synced=0 and result not in ("Invalid", "ValueNotSet")"""
        )

        with Session(engine) as session:
            result = session.execute(select_stmt)

        return self.astm_result_to_dataframe(result.all(), result.keys())

    def astm_result_to_dataframe(self, results, keys):
        # Aso skip those whose raw_data payload len is > 1200
        return pd.DataFrame(
            [self.sanitise(line) for line in results],
            columns=keys
        )

    @staticmethod
    def astm_result_to_csv(data_frame):
        data_frame.to_csv("astm_results.csv", index=False)

    @staticmethod
    def update_astm_result(order_id: int, lims_sync_status: int):
        logger.log(
            "info", f"AstmOrderHandler: Updating astm result orders with uid: {order_id} with synced: {lims_sync_status} ...")
        update_stmt = text(
            """update orders set synced = :status, sync_date = :date_updated where uid = :uid""")

        update_line = {
            "uid": order_id,
            "status": lims_sync_status,
            "date_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        with Session(engine) as session:
            session.execute(update_stmt, update_line)
            session.commit()


class SenaiteHandler:
    def __init__(self):
        self.username = SENAITE_USER
        self.password = SENAITE_PASSWORD
        self.api_url = SENAITE_API_URL
        self.also_verify = VERIFY_RESULT

    def _auth_session(self):
        """ start a fresh requests session """
        self.session = requests.session()
        self.session.verify = ssl.CERT_NONE
        self.session.auth = HTTPBasicAuth(self.username, self.password)

    def test_senaite_connection(self) -> bool:
        self._auth_session()
        url = f"{self.api_url}/"
        try:
            response = self.session.post(url)
            if response.status_code == 200:
                logger.log(
                    "info", f"SenaiteConn: connection established with {url}")
                return True
            else:
                logger.log(
                    "error", f"SenaiteConn: connection failed with {url}")
                self.error_handler(None, url, response)
                return False
        except Exception as e:
            logger.log(
                "error", f"SenaiteConn: connection failed with error: {e}")
            return False

    @staticmethod
    def error_handler(action=None, url=None, res=None):
        logger.log(
            "info", f"SenaiteHandler: Error Status Code: {res.status_code} Reason: {res.reason}")
        if action:
            logger.log(
                "info", f"SenaiteHandler: Error Resource ({action}) {url}")
        logger.log("info", f"SenaiteHandler: Error Detail {res.text}")

    @staticmethod
    def decode_response(response):
        return json.loads(response)

    def search_analyses_by_request_id(self, request_id):
        """Searches senaite's Analysis portal for results
        @param request_id: Sample ID e.g BP-XXXXX
        @return dict
        """
        # searching using an ID.
        search_url = f"{self.api_url}/search?getRequestID={request_id}&catalog=bika_analysis_catalog"
        logger.log(
            "info", f"SenaiteHandler: Searching for analysis with getRequestID {request_id}")
        response = self.session.get(search_url)
        if response.status_code == 200:
            data = self.decode_response(response.text)
            return True, data
        else:
            self.error_handler("search_analyses_by_csid", search_url, response)
            return False, None

    def update_resource(self, uid, payload):
        """ create a new resource in senaite: single or bundled """
        url = f"{self.api_url}/update/{uid}"
        logger.log("info", f"SenaiteHandler: Updating resource: {url}")
        response = self.session.post(url, json=payload)
        if response.status_code == 200:
            data = self.decode_response(response.text)
            return True, data
        else:
            self.error_handler("create", url, response)
            return False, None

    def do_work_for_order(self, request_id, result, keyword=None):
        self._auth_session()

        searched, search_payload = self.search_analyses_by_request_id(
            request_id)
        # 'getResult': '', 'getResultCaptureDate': None, 'getSubmittedBy': None, 'getKeyword': 'XXXXXXX'

        submitted = False
        submit_payload = {
            "transition": "submit",
            "Result": result,
            "InterimFields": []
        }

        if not searched:
            return False

        search_items = search_payload.get("items")
        if not len(search_items) > 0:
            return False

        search_data = search_items[0]
        assert search_data.get("getParentTitle") == request_id

        logger.log("info", f"SenaiteHandler:  ---submission---")
        submitted, submission = self.update_resource(
            search_data.get("uid"), submit_payload)
        # Result is not None
        # 'SubmittedBy': 'system_daemon', ResultCaptureDate is not None, DateSubmitted == ResultCaptureDate

        if self.also_verify:
            if not submitted:
                return False

            verified = False
            verify_payload = {"transition": "verify"}

            submission_items = submission.get("items")
            if not len(submission_items) > 0:
                return False

            submission_data = submission_items[0]
            assert submission_data.get("uid") == search_data.get("uid")

            logger.log("info", f"SenaiteHandler:  ---verification---")
            verified, verification = self.update_resource(
                submission_data.get("uid"), verify_payload
            )

            # DateVerified is not None, 'VerifiedBy': 'system_daemon'
        return True


class SenaiteQueuer:

    def __init__(self):
        self.base_url = SENAITE_BASE_URL
        self.api_url = SENAITE_API_URL
        self.session = None
        self.start_session(SENAITE_USER, SENAITE_PASSWORD)

    def start_session(self, username, password):
        logger.log("info", "Starting session with SENAITE ...")
        self.session = requests.Session()
        self.session.auth = (username, password)

        # try to get the version of the remote JSON API
        version = self.get_version()
        if not version or not version.get('version'):
            logger.log(
                "error", f"senaite.jsonapi not found on at {self.api_url}")
            return False

        # try to get the current logged in user
        user = self.get_authenticated_user()
        if not user or user.get("authenticated") is False:
            logger.log("error", "Wrong username/password")
            return False

        logger.log(
            "info", f"Session established ('{username}') with '{self.base_url}'")
        return True

    def send_message(self, message):
        logger.log("info", f"Sending message to SENAITE: {message[:50]} ...")
        if not self.session:
            logger.log("info", "Session not started yet")
            return False

        url_import = f"{self.base_url}/serial_push"
        response = self.session.post(url_import,
                                     data={"message": message},
                                     timeout=30)
        if response.text == "ACK":
            logger.log("info", "Message accepted")
            return True
        logger.log("info", F"Message not accepted: {response.__dict__}")
        return False

    def get_version(self):
        """Return the remote JSON API version
        """
        return self.get_json("version")

    def get_authenticated_user(self):
        """Return the current logged in remote user
        """
        return self.get_first_item("users/current")

    def get_first_item(self, endpoint, **kw):
        """Fetch the first item of the 'items' list from a std. JSON API reponse
        """
        items = self.get_items_with_retry(
            endpoint=endpoint, **kw)
        if not items:
            return None
        return items[0]

    def get_items_with_retry(self, max_attempts=API_MAX_ATTEMPTS,
                             interval=API_ATTEMPT_INTERVAL, **kwargs):
        """
        Retries to retrieve items if HTTP response fails.
        :param max_attempts: maximum number of attempts to try
        :param interval: time delay between attempts in seconds
        :param kwargs: query and parameters pass to get_items
        :return:
        """
        items = None
        for i in range(max_attempts):
            items = self.get_items(kwargs.get("endpoint", None))
            if items:
                break
            sleep(interval)
        return items

    def get_items(self, endpoint):
        """
        Return the 'items' list from a std. JSON API response
        """
        data = self.get_json(endpoint)
        if not isinstance(data, dict):
            return []
        return data.get("items", [])

    def get_json(self, endpoint):
        """Fetch the given url or endpoint and return a parsed JSON object
        """
        api_url = self.get_api_url(endpoint)
        try:
            response = self.session.get(api_url)
        except Exception as e:
            message = f"Could not connect to {api_url} Please check"
            logger.log("error", message)
            logger.log("error", e)
            return {}
        status = response.status_code
        if status != 200:
            message = f"GET for {endpoint} ({api_url}) returned Status Code {status}. Please check."
            logger.log("error", message)
            return {}
        return response.json()

    def get_api_url(self, endpoint):
        """Create an API URL from an endpoint"""
        return "/".join([
            self.api_url,
            "/".join(endpoint.split("/"))
        ])


class ResultInterface(FowardOrderHandler, SenaiteHandler):
    def run(self):
        database_reachable = test_db_connection()
        if not self.test_senaite_connection() or not database_reachable:
            return
        to_exclude = [x.strip().lower() for x in EXCLUDE_RESULTS]
        orders = self.fetch_astm_results()
        if not len(orders) > 0:
            logger.log("info", f"AstmOrderHandler: No orders at the moment :)")

        for index, order in orders.iterrows():
            if index > 0 and index % SLEEP_SUBMISSION_COUNT == 0:
                logger.log("info", f"ResultInterface:  ---sleeping---")
                time.sleep(SLEEP_SECONDS)
                logger.log("info", f"ResultInterface:  ---waking---")

            senaite_updated = False
            if SEND_TO_QUEUE:
                senaite_updated = SenaiteQueuer(
                ).send_message(order['raw_message'])
            else:
                # Parse the result object before sending to LIMS
                result_parser = ResultParser(order["result"], order["unit"])
                result = str(result_parser.output)

                if isinstance(result, str):
                    if result.strip().lower() in to_exclude:
                        # also update astm db for excluded to avoid unecessary trips
                        senaite_updated = True
                    else:
                        senaite_updated = self.do_work_for_order(
                            order["order_id"],
                            result,
                            order["keywork"]
                        )
                else:
                    senaite_updated = self.do_work_for_order(
                        order["order_id"],
                        result,
                        order["keywork"]
                    )
            #
            if senaite_updated:
                self.update_astm_result(order["uid"], 1)
