"""
Twin Liquors Organizer — CLI
Manage inventory + duties with MariaDB backend.
"""

import argparse
import csv
from datetime import date
from typing import Optional

from tabulate import tabulate

from db import get_conn

# ---------- Inventory commands ----------


def remember_name(name: str) -> None:
    """Save product name in name_catalog for future suggestions."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("INSERT IGNORE INTO name_catalog(name) VALUES (%s)", (name,))


def list_items() -> None:
    """List active inventory with location context."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, item, quantity, category,
                   location_type, aisle, position, barcode, last_ordered
            FROM inventory
            WHERE active = 1
            ORDER BY item;
            """
        )
        print(tabulate(cur.fetchall(), headers="keys", tablefmt="github"))


def add_item(
    item: str,
    qty: int,
    cat: Optional[str] = None,
    aisle: Optional[str] = None,
    pos: Optional[str] = None,
    loc: str = "overstock",
    barcode: Optional[str] = None,
    img: Optional[str] = None,
) -> None:
    """Insert new inventory row and save its name for suggestions."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO inventory(item, quantity, category, aisle, position,
                                  location_type, barcode, image_url, last_ordered)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (item, qty, cat, aisle, pos, loc, barcode, img, date.today()),
        )
    remember_name(item)
    where = f"{loc} {aisle or ''} {pos or ''}".strip()
    print(f"Added: {item} (qty {qty}) @ {where}")


def update_qty(item_id: int, qty: int) -> None:
    """Update quantity for given inventory id."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("UPDATE inventory SET quantity=%s WHERE id=%s", (qty, item_id))
    print("Updated", item_id)


def low_stock(threshold: int) -> None:
    """Show items with qty <= threshold."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id,item,quantity,category FROM inventory "
            "WHERE quantity<=%s ORDER BY quantity ASC;",
            (threshold,),
        )
        rows = cur.fetchall()
        print(tabulate(rows, headers="keys", tablefmt="github") if rows else "No low-stock items.")


def export_low_stock(threshold: int, csv_path: str) -> None:
    """Export low-stock items to CSV."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id,item,quantity,category FROM inventory "
            "WHERE quantity<=%s ORDER BY quantity ASC;",
            (threshold,),
        )
        rows = cur.fetchall()
    if not rows:
        print("None")
        return
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "item", "quantity", "category"])
        writer.writeheader()
        writer.writerows(rows)
    print("Exported", len(rows))


# ---------- Duties ----------


def list_duties() -> None:
    """List duties (newest first)."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id,task,completed,date FROM duties ORDER BY date DESC,id DESC;")
        print(tabulate(cur.fetchall(), headers="keys", tablefmt="github"))


def add_duty(task: str) -> None:
    """Insert a new duty for today."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO duties(task,completed,date) VALUES(%s,0,%s)", (task, date.today()))
    print("Added duty", task)


def complete_duty(duty_id: int) -> None:
    """Mark duty as completed."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("UPDATE duties SET completed=1 WHERE id=%s", (duty_id,))
    print("Completed duty", duty_id)


# ---------- Archive & suggestions ----------


def archive_item(item_id: int) -> None:
    """Soft delete: set active=0 for given inventory id."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("UPDATE inventory SET active=0 WHERE id=%s", (item_id,))
    print(f"Archived item {item_id}")


def suggest_names(q: str) -> None:
    """Suggest product names that contain the query substring."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT name FROM name_catalog WHERE name LIKE %s ORDER BY name LIMIT 20",
            (f"%{q}%",),
        )
        rows = cur.fetchall()
    print(tabulate(rows, headers="keys", tablefmt="github") if rows else "No suggestions.")


# ---------- CLI setup ----------


def build_parser() -> argparse.ArgumentParser:
    """Define CLI commands and args."""
    p = argparse.ArgumentParser(prog="twinliquors", description="Twin Liquors Organizer CLI")
    s = p.add_subparsers(dest="cmd", required=True)

    # inventory
    s.add_parser("list-items", help="List inventory")
    a = s.add_parser("add-item", help="Add a new inventory item")
    a.add_argument("--item", required=True)
    a.add_argument("--qty", required=True, type=int)
    a.add_argument("--cat")
    a.add_argument("--aisle")
    a.add_argument("--pos")
    a.add_argument("--loc", choices=["shelf", "overstock"], default="overstock")
    a.add_argument("--barcode")
    a.add_argument("--img")

    u = s.add_parser("update-qty", help="Update quantity by id")
    u.add_argument("--id", required=True, type=int)
    u.add_argument("--qty", required=True, type=int)

    low_parser = s.add_parser("low-stock", help="Show items at/below threshold")
    low_parser.add_argument("--threshold", type=int, default=3)

    e = s.add_parser("export-low-stock", help="Export low-stock items to CSV")
    e.add_argument("--threshold", type=int, default=3)
    e.add_argument("--csv", required=True)

    # duties
    s.add_parser("list-duties", help="List all duties")
    d = s.add_parser("add-duty", help="Add a duty")
    d.add_argument("--task", required=True)
    c = s.add_parser("complete-duty", help="Complete a duty")
    c.add_argument("--id", required=True, type=int)

    # extras
    arch = s.add_parser("archive-item", help="Archive an item (soft delete)")
    arch.add_argument("--id", required=True, type=int)

    sg = s.add_parser("suggest-names", help="Suggest item names")
    sg.add_argument("--q", required=True)

    return p


def main() -> None:
    """Dispatch CLI commands to functions."""
    a = build_parser().parse_args()
    if a.cmd == "list-items":
        list_items()
    elif a.cmd == "add-item":
        add_item(a.item, a.qty, a.cat, a.aisle, a.pos, a.loc, a.barcode, a.img)
    elif a.cmd == "update-qty":
        update_qty(a.id, a.qty)
    elif a.cmd == "low-stock":
        low_stock(a.threshold)
    elif a.cmd == "export-low-stock":
        export_low_stock(a.threshold, a.csv)
    elif a.cmd == "list-duties":
        list_duties()
    elif a.cmd == "add-duty":
        add_duty(a.task)
    elif a.cmd == "complete-duty":
        complete_duty(a.id)
    elif a.cmd == "archive-item":
        archive_item(a.id)
    elif a.cmd == "suggest-names":
        suggest_names(a.q)


if __name__ == "__main__":
    main()
