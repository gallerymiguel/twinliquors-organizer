from app import db


def get_topstock_items():
    conn = db()
    cursor = conn.cursor()

    # Find all items marked as overstock
    cursor.execute(
        """
        SELECT id, item, quantity, category, location_type, aisle, position, barcode, last_ordered
        FROM inventory
        WHERE location_type = 'overstock'
    """
    )
    items = cursor.fetchall()
    conn.close()
    return items
