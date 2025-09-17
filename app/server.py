from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from . import repo

app = FastAPI(title="Twin Liquors Organizer")

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


@app.get("/")
def home(request: Request):
    items = repo.list_items_json()
    return templates.TemplateResponse("index.html", {"request": request, "items": items})


@app.post("/add")
def add_item(
    request: Request,
    item: str = Form(...),
    qty: int = Form(...),
    cat: str = Form(None),
    aisle: str = Form(None),
    pos: str = Form(None),
    loc: str = Form("overstock"),
    barcode: str = Form(None),
    img: str = Form(None),
):
    repo.insert_item(item, qty, cat, aisle, pos, loc, barcode, img)
    repo.remember_name(item)
    return RedirectResponse(url="/", status_code=303)
