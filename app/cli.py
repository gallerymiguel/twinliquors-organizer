# app/cli.py
import csv
from typing import Optional

import typer
from rich import print
from rich.table import Table

from . import repo  # app/repo.py

app = typer.Typer(help="Twin Liquors Organizer CLI")

# ----- helpers -----


def print_table(rows, title: str):
    if not rows:
        print("[dim]No rows.[/dim]")
        return
    t = Table(title=title, show_lines=False)
    for k in rows[0]:
        t.add_column(str(k))
    for r in rows:
        t.add_row(*[str(v) if v is not None else "" for v in r.values()])
    print(t)


# ----- inventory -----

inv = typer.Typer(help="Inventory commands")
app.add_typer(inv, name="inv")


@inv.command("list")
def inv_list():
    """List active inventory with location info."""
    rows = repo.list_items_active()
    print_table(rows, "Inventory (active)")


@inv.command("add")
def inv_add(
    item: str = typer.Option(..., help="Display name"),
    qty: int = typer.Option(..., help="Quantity"),
    cat: Optional[str] = typer.Option(None, help="Category"),
    aisle: Optional[str] = typer.Option(None, help="Aisle label, e.g., A4"),
    pos: Optional[str] = typer.Option(None, help="Position within aisle"),
    loc: str = typer.Option("overstock", help="shelf|overstock"),
    barcode: Optional[str] = typer.Option(None, help="UPC/EAN"),
    img: Optional[str] = typer.Option(None, help="Image URL"),
):
    repo.insert_item(item, qty, cat, aisle, pos, loc, barcode, img)
    repo.remember_name(item)
    print(f"[green]Added[/green] {item} (qty {qty}) @ {loc} {aisle or ''} {pos or ''}")


@inv.command("qty")
def inv_update_qty(id: int, qty: int):
    """Update quantity for an item id."""
    changed = repo.update_qty(id, qty)
    print("[green]Updated[/green]" if changed else "[yellow]No change[/yellow]", id)


@inv.command("low")
def inv_low(threshold: int = 3):
    """Show items with qty <= threshold."""
    rows = repo.low_stock_rows(threshold)
    print_table(rows, f"Low stock (<= {threshold})")


@inv.command("export")
def inv_export(threshold: int = 3, csv_path: str = typer.Option(..., help="Output CSV path")):
    """Export low-stock items to CSV."""
    rows = repo.low_stock_rows(threshold)
    if not rows:
        print("[dim]None[/dim]")
        return
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"[green]Exported[/green] {len(rows)} -> {csv_path}")


@inv.command("archive")
def inv_archive(id: int):
    """Soft delete item (active=0)."""
    changed = repo.archive_item(id)
    print("[green]Archived[/green]" if changed else "[yellow]Not found[/yellow]", id)


@inv.command("unarchive")
def inv_unarchive(id: int):
    """Restore item (active=1)."""
    changed = repo.unarchive_item(id)
    print("[green]Unarchived[/green]" if changed else "[yellow]Not found[/yellow]", id)


@inv.command("suggest")
def inv_suggest(q: str):
    """Suggest names containing q."""
    rows = repo.suggest_names_like(q)
    print_table(rows, f"Suggestions: {q}")


# ----- duties -----

dut = typer.Typer(help="Duties commands")
app.add_typer(dut, name="dut")


@dut.command("list")
def dut_list():
    rows = repo.list_duties_rows()
    print_table(rows, "Duties")


@dut.command("add")
def dut_add(task: str):
    repo.insert_duty(task)
    print(f"[green]Added duty[/green] {task}")


@dut.command("done")
def dut_done(id: int):
    changed = repo.complete_duty_id(id)
    print("[green]Completed[/green]" if changed else "[yellow]Not found[/yellow]", id)


if __name__ == "__main__":
    app()
