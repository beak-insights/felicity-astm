import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Database
DB_NAME = "astm_results"
DB_USER = "nmrl"
DB_PASSWORD = "password"
DB_HOST = "localhost:3306"
DB_CLEAR_DATA_OVER_DAYS = 14

# Forward app settings
SENAITE_HOST = "xxx.xxx.xxx.xxx:80"
SENAITE_BASE_URL = f"http://{SENAITE_HOST}/senaite"
SENAITE_API_URL = f"{SENAITE_BASE_URL}/@@API/senaite/v1"
SENAITE_USER = "system_daemon"
SENAITE_PASSWORD = "s89Ajs-UIas!3k"

# SENAITE.JSONAPI
SEND_TO_QUEUE = False
API_MAX_ATTEMPTS = 10
API_ATTEMPT_INTERVAL = 30

# If Not SENAITE.JSONAPI a.k.a SEND_TO_QUEUE = True
VERIFY_RESULT = False
SLEEP_SECONDS = 5
# logger every ?
SLEEP_SUBMISSION_COUNT = 10
# check the database every xx minutes :
POLL_BD_EVERY = 10
# on each check, limit results to
RESULT_SUBMISSION_COUNT = 250

# Trial Hack for Hologic EID
RESOLVE_HOLOGIC_EID = False

# Results
EXCLUDE_RESULTS = ["Invalid", "ValueNotSet"]

# Keyword mappings
KEYWORDS_MAPPING = {
    # Abbott
    "HIV1mlDBS": ["Abbott", "HIV06ml", "VLDBS", "VLPLASMA", ],
    "HIV1.0mlDBS": ["Abbott", "HIV06ml", "VLDBS", "VLPLASMA", ],
    "HIV06ml": ["Abbott", "HIV06ml", "VLDBS", "VLPLASMA", ],
    "HIV0.2ml": ["Abbott", "HIV06ml", "VLDBS", "VLPLASMA", ],
    # Roche Cobas
    "HI2DIL96": ["HI2CAP96", "VLDBS", "VLPLASMA", ],
    "HI2DIL48": ["HI2CAP96", "VLDBS", "VLPLASMA", ],
    "HI2CAP48": ["HI2CAP96", "VLDBS", "VLPLASMA", ],
    "HI2CAP96": ["HI2CAP96", "VLDBS", "VLPLASMA", ],
    # Hologic Panther
    "qHIV-1": ["ViralLoad", "VLDBS", "VLPLASMA", ],
    "HIV-1": ["ViralLoad", "VLDBS", "VLPLASMA", ],
    "HPV": ["HPV", "HPV01", ]
}

# Admin pane
STATIC_DIR = f"{BASE_DIR}/dashboard/static"
TEMPLATE_DIR = f"{BASE_DIR}/dashboard/templates"
