import argparse, csv
from datetime import date
from tabulate import tabulate
from db import get_conn


def remember_name(name: str):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("INSERT IGNORE INTO name_catalog(name) VALUES (%s)", (name,))


def list_items():
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
    item, qty, cat=None, aisle=None, pos=None, loc="overstock", barcode=None, img=None
):
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


def update_qty(i, q):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("UPDATE inventory SET quantity=%s WHERE id=%s", (q, i))
    print("Updated", i)


def low_stock(t):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id,item,quantity,category FROM inventory WHERE quantity<=%s ORDER BY quantity ASC;",
            (t,),
        )
        rows = cur.fetchall()
        print(
            tabulate(rows, headers="keys", tablefmt="github")
            if rows
            else "No low-stock items."
        )


def export_low_stock(t, path):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id,item,quantity,category FROM inventory WHERE quantity<=%s ORDER BY quantity ASC;",
            (t,),
        )
        rows = cur.fetchall()
    if not rows:
        print("None")
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "item", "quantity", "category"])
        w.writeheader()
        w.writerows(rows)
    print("Exported", len(rows))


def list_duties():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id,task,completed,date FROM duties ORDER BY date DESC,id DESC;"
        )
        print(tabulate(cur.fetchall(), headers="keys", tablefmt="github"))


def add_duty(task):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO duties(task,completed,date) VALUES(%s,0,%s)",
            (task, date.today()),
        )
    print("Added duty", task)


def complete_duty(i):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("UPDATE duties SET completed=1 WHERE id=%s", (i,))
    print("Completed duty", i)


def build_parser():
    p = argparse.ArgumentParser()
    s = p.add_subparsers(dest="cmd", required=True)

    # inventory
    s.add_parser("list-items")

    a = s.add_parser("add-item")
    a.add_argument("--item", required=True)
    a.add_argument("--qty", required=True, type=int)
    a.add_argument("--cat")
    a.add_argument("--aisle")
    a.add_argument("--pos")
    a.add_argument("--loc", choices=["shelf", "overstock"], default="overstock")
    a.add_argument("--barcode")
    a.add_argument("--img")

    u = s.add_parser("update-qty")
    u.add_argument("--id", required=True, type=int)
    u.add_argument("--qty", required=True, type=int)

    l = s.add_parser("low-stock")
    l.add_argument("--threshold", type=int, default=3)

    e = s.add_parser("export-low-stock")
    e.add_argument("--threshold", type=int, default=3)
    e.add_argument("--csv", required=True)

    # duties
    s.add_parser("list-duties")
    d = s.add_parser("add-duty")
    d.add_argument("--task", required=True)
    c = s.add_parser("complete-duty")
    c.add_argument("--id", required=True, type=int)

    # new commands
    arch = s.add_parser("archive-item")
    arch.add_argument("--id", required=True, type=int)

    sg = s.add_parser("suggest-names")
    sg.add_argument("--q", required=True)

    return p


def archive_item(i):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("UPDATE inventory SET active=0 WHERE id=%s", (i,))
    print(f"Archived item {i}")


def suggest_names(q):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT name FROM name_catalog WHERE name LIKE %s ORDER BY name LIMIT 20",
            (f"%{q}%",),
        )
        rows = cur.fetchall()
    print(
        tabulate(rows, headers="keys", tablefmt="github") if rows else "No suggestions."
    )


def main():
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
