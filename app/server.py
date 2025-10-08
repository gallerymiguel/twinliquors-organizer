from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.topstock import get_topstock_items

from . import repo

app = FastAPI(title="Twin Liquors Organizer")

# Tell FastAPI where your templates live
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


@app.get("/")
def home(request: Request):
    items = repo.list_items_json()
    return templates.TemplateResponse("index.html", {"request": request, "items": items})


@app.get("/topstock")
def topstock(request: Request):
    items = get_topstock_items()
    return templates.TemplateResponse("topstock.html", {"request": request, "items": items})


@app.post("/add")
def add_item(
    request: Request,
    item: str = Form(...),
    quantity: int = Form(...),
    category: str = Form(None),
    aisle: str = Form(None),
    position: str = Form(None),
    location_type: str = Form("overstock"),
    barcode: str = Form(None),
    image_url: str = Form(None),
):
    repo.insert_item(item, quantity, category, aisle, position, location_type, barcode, image_url)
    repo.remember_name(item)
    return RedirectResponse(url="/", status_code=303)
