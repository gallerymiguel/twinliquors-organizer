# app/repo.py
from collections.abc import Iterable
from datetime import date
from typing import Optional

from .db import get_conn

# ----- inventory -----


def list_items_json():
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
        return cur.fetchall()


def list_items_active() -> Iterable[dict]:
    sql = """
    SELECT id, item, quantity, category, location_type, aisle, position, barcode, last_ordered
    FROM inventory WHERE active=1 ORDER BY item;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()


def insert_item(
    item: str,
    qty: int,
    cat: Optional[str],
    aisle: Optional[str],
    pos: Optional[str],
    loc: str,
    barcode: Optional[str],
    img: Optional[str],
) -> None:
    sql = """
    INSERT INTO inventory(item, quantity, category, aisle, position,
                          location_type, barcode, image_url, last_ordered)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (item, qty, cat, aisle, pos, loc, barcode, img, date.today()))


def remember_name(name: str) -> None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("INSERT IGNORE INTO name_catalog(name) VALUES (%s)", (name,))


def update_qty(item_id: int, qty: int) -> int:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("UPDATE inventory SET quantity=%s WHERE id=%s", (qty, item_id))
        return cur.rowcount


def low_stock_rows(threshold: int) -> Iterable[dict]:
    sql = """
    SELECT id,item,quantity,category
    FROM inventory
    WHERE quantity<=%s
    ORDER BY quantity ASC;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (threshold,))
        return cur.fetchall()


def archive_item(item_id: int) -> int:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("UPDATE inventory SET active=0 WHERE id=%s", (item_id,))
        return cur.rowcount


def unarchive_item(item_id: int) -> int:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("UPDATE inventory SET active=1 WHERE id=%s", (item_id,))
        return cur.rowcount


def suggest_names_like(q: str) -> Iterable[dict]:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT name FROM name_catalog WHERE name LIKE %s ORDER BY name LIMIT 20",
            (f"%{q}%",),
        )
        return cur.fetchall()


# ----- duties -----


def list_duties_rows() -> Iterable[dict]:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id,task,completed,date FROM duties ORDER BY date DESC,id DESC;")
        return cur.fetchall()


def insert_duty(task: str) -> None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO duties(task,completed,date) VALUES(%s,0,%s)", (task, date.today()))


def complete_duty_id(duty_id: int) -> int:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("UPDATE duties SET completed=1 WHERE id=%s", (duty_id,))
        return cur.rowcount
