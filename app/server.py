# app/server.py
from typing import Optional
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from . import repo  # our data layer (app/repo.py)

app = FastAPI(title="Twin Liquors Organizer")

# ---- HTML helpers ----

FORM_HTML = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>Twin Liquors Organizer</title>
    <style>
      body { font-family: system-ui, Arial, sans-serif; max-width: 720px; margin: 32px auto; padding: 0 16px; }
      h1 { margin-bottom: 8px; }
      form { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 16px 0; }
      label { font-size: 12px; color: #444; }
      input, select, button { padding: 8px; font-size: 14px; }
      .row { display: flex; gap: 12px; }
      .full { grid-column: 1 / -1; }
      table { border-collapse: collapse; width: 100%; margin-top: 16px; }
      th, td { border: 1px solid #ddd; padding: 6px 8px; font-size: 13px; }
      th { background: #f5f5f5; text-align: left; }
      .ok { background: #e9f7ef; padding: 8px; border: 1px solid #b6e2c5; }
      .warn { background: #fff8e1; padding: 8px; border: 1px solid #ffe082; }
      .actions a { margin-right: 10px; }
    </style>
  </head>
  <body>
    <h1> Twin Liquors Organizer </h1>
    <p class="ok">Quick add form writes to the same DB the CLI uses.</p>

    <h2>Add Inventory</h2>
    <form method="post" action="/add">
      <div>
        <label>Item</label>
        <input name="item" required />
      </div>
      <div>
        <label>Qty</label>
        <input name="qty" type="number" value="1" required />
      </div>
      <div>
        <label>Category</label>
        <input name="cat" />
      </div>
      <div>
        <label>Aisle</label>
        <input name="aisle" />
      </div>
      <div>
        <label>Position</label>
        <input name="pos" placeholder="Top-Right" />
      </div>
      <div>
        <label>Location</label>
        <select name="loc">
          <option value="overstock" selected>overstock</option>
          <option value="shelf">shelf</option>
        </select>
      </div>
      <div class="full">
        <label>Barcode</label>
        <input name="barcode" />
      </div>
      <div class="full">
        <label>Image URL (optional)</label>
        <input name="img" />
      </div>
      <div class="full">
        <button type="submit">Add Item</button>
      </div>
    </form>

    <div class="actions">
      <a href="/items">View items (JSON)</a>
      <a href="/low?threshold=3">Low stock <= 3 (JSON)</a>
      <a href="/suggest?q=Tito">Suggest “Tito” (JSON)</a>
    </div>

    <h2>Active Inventory</h2>
    <div id="table"></div>

    <script>
      // simple client-side fetch to render a table quickly
      async function loadTable() {
        const res = await fetch('/items');
        const rows = await res.json();
        if (!Array.isArray(rows) || rows.length === 0) {
          document.getElementById('table').innerHTML = '<p class="warn">No rows.</p>';
          return;
        }
        const cols = Object.keys(rows[0]);
        let html = '<table><thead><tr>' + cols.map(c => '<th>'+c+'</th>').join('') + '</tr></thead><tbody>';
        for (const r of rows) {
          html += '<tr>' + cols.map(c => '<td>'+(r[c] ?? '')+'</td>').join('') + '</tr>';
        }
        html += '</tbody></table>';
        document.getElementById('table').innerHTML = html;
      }
      loadTable();
    </script>
  </body>
</html>
"""

# ---- Routes ----

@app.get("/", response_class=HTMLResponse)
def home():
    """Simple HTML form + a live table (pulls from /items)."""
    return FORM_HTML

@app.post("/add")
def add(
    item: str = Form(...),
    qty: int = Form(...),
    cat: Optional[str] = Form(None),
    aisle: Optional[str] = Form(None),
    pos: Optional[str] = Form(None),
    loc: str = Form("overstock"),
    barcode: Optional[str] = Form(None),
    img: Optional[str] = Form(None),
):
    repo.insert_item(item, qty, cat, aisle, pos, loc, barcode, img)
    repo.remember_name(item)
    # Redirect back to form so refresh doesn't re-post
    return RedirectResponse(url="/", status_code=303)

@app.get("/items")
def items():
    """Active inventory as JSON."""
    rows = repo.list_items_active()
    return JSONResponse(rows)

@app.get("/low")
def low(threshold: int = 3):
    """Low stock JSON (<= threshold)."""
    rows = repo.low_stock_rows(threshold)
    return JSONResponse(rows)

@app.get("/suggest")
def suggest(q: str):
    """Name suggestions JSON."""
    rows = repo.suggest_names_like(q)
    return JSONResponse(rows)
