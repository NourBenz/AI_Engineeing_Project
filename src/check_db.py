from pathlib import Path
import sqlite3
import json

db = Path(__file__).resolve().parents[1] / "data" / "bookstore.sqlite"
conn = sqlite3.connect(db)
conn.execute("PRAGMA foreign_keys = ON")

checks = {
    "customers with no orders": """
        SELECT COUNT(*) FROM customers c
        WHERE NOT EXISTS (
            SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id
        )
    """,
    "products never ordered": """
        SELECT COUNT(*) FROM products p
        WHERE NOT EXISTS (
            SELECT 1 FROM order_items i WHERE i.product_id = p.product_id
        )
    """,
    "completed orders": """
        SELECT COUNT(*) FROM orders WHERE status = 'completed'
    """,
    "cancelled orders": """
        SELECT COUNT(*) FROM orders WHERE status = 'cancelled'
    """,
    "successful payments": """
        SELECT COUNT(*) FROM payments WHERE status = 'successful'
    """,
    "failed payments": """
        SELECT COUNT(*) FROM payments WHERE status = 'failed'
    """,
    "returns": "SELECT COUNT(*) FROM returns",
}

for name, sql in checks.items():
    print(f"{name}: {conn.execute(sql).fetchone()[0]}")

foreign_key_errors = conn.execute("PRAGMA foreign_key_check").fetchall()
print(f"foreign-key errors: {len(foreign_key_errors)}")

for line in (db.parent / "items.jsonl").read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    item = json.loads(line)
    rows = conn.execute(item["reference_sql"]).fetchall()
    print(f"{item['id']}: {rows[:3]} (total rows: {len(rows)})")
    

conn.close()