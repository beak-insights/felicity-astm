from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from felicity.config import STATIC_DIR, TEMPLATE_DIR
from felicity.db.models import Orders

templates = Jinja2Templates(directory=TEMPLATE_DIR)

app = FastAPI(
    title="ASTM Results Dashboard"
)
# app.include_router(web, include_in_schema=False)
app.mount(
    "/static", StaticFiles(directory=STATIC_DIR), name="static"
)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "message": "This was received from server"})


@app.get("/api/orders")
async def api_orders(request: Request):
    return Orders.all()

@app.post("/api/orders/resync/{uid}")
async def api_orders(uid):
    order = Orders.find(uid)
    order.update(synced=0)
    return order
