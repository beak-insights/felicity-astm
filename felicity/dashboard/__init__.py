import uvicorn


def start_dashboard():
    uvicorn.run("felicity.dashboard.panel:app", port=9999, log_level="info")
