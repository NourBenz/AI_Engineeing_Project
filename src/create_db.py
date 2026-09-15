from datetime import date, timedelta
from pathlib import Path
import random
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DB = DATA / "bookstore.sqlite"
rng = random.Random(496)


def day(offset):
    return (date(2025, 11, 1) + timedelta(days=offset)).isoformat()


if DB.exists():
    raise SystemExit(
        f"{DB} already exists. Move or delete it yourself before regenerating."
    )

conn = sqlite3.connect(DB)
conn.executescript((DATA / "schema.sql").read_text(encoding="utf-8"))
conn.execute("PRAGMA foreign_keys = ON")

categories = [
    "Fiction", "History", "Science", "Technology",
    "Business", "Art", "Travel", "Children",
]
conn.executemany(
    "INSERT INTO categories VALUES (?, ?)",
    [(i, name) for i, name in enumerate(categories, 1)],
)

countries = {
    "Tunisia": ["Tunis", "Sfax", "Sousse"],
    "France": ["Paris", "Lyon", "Marseille"],
    "Morocco": ["Rabat", "Casablanca", "Marrakesh"],
    "Algeria": ["Algiers", "Oran", "Constantine"],
}
places = [
    (country, city)
    for country, cities in countries.items()
    for city in cities
]

customers = []
for customer_id in range(1, 121):
    country, city = places[(customer_id - 1) % len(places)]
    customers.append((
        customer_id,
        f"Customer {customer_id:03d}",
        f"customer{customer_id:03d}@example.test",
        city,
        country,
        day(rng.randrange(0, 90)),
        0 if customer_id % 9 == 0 else 1,
    ))
conn.executemany(
    "INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, ?)",
    customers,
)

products = []
for product_id in range(1, 81):
    products.append((
        product_id,
        ((product_id - 1) % 8) + 1,
        f"Book {product_id:03d}",
        rng.randrange(5, 151) * 100,
        0 if product_id % 11 == 0 else 1,
    ))
conn.executemany(
    "INSERT INTO products VALUES (?, ?, ?, ?, ?)",
    products,
)

# Customers 1–12 have no orders.
# Customers 13–36 have exactly one order.
# Customers 37–120 have at least three orders.
order_customers = list(range(13, 37))
order_customers += [
    customer_id
    for customer_id in range(37, 121)
    for _ in range(3)
]
order_customers += [
    rng.randrange(37, 121)
    for _ in range(24)
]
rng.shuffle(order_customers)

statuses = (
    ["completed"] * 210
    + ["placed"] * 45
    + ["cancelled"] * 45
)
rng.shuffle(statuses)

# 90 orders have one item; 180 have three; 30 have four.
# Total: 750 order-item rows.
line_counts = [1] * 90 + [3] * 180 + [4] * 30
rng.shuffle(line_counts)

orders = []
items = []
totals = {}
completed_lines = []

for order_id in range(1, 301):
    status = statuses[order_id - 1]
    ordered = day(rng.randrange(90, 310))
    closed = day(rng.randrange(311, 330))

    orders.append((
        order_id,
        order_customers[order_id - 1],
        ordered,
        status,
        closed if status == "completed" else None,
        closed if status == "cancelled" else None,
    ))

    # Products 69–80 are never ordered.
    # Products 1–10 are chosen more often.
    choices = list(range(1, 11)) * 5 + list(range(11, 69))
    selected = []
    while len(selected) < line_counts[order_id - 1]:
        product_id = rng.choice(choices)
        if product_id not in selected:
            selected.append(product_id)

    total = 0
    for line_no, product_id in enumerate(selected, 1):
        quantity = rng.randrange(1, 6)
        list_price = products[product_id - 1][3]
        paid_price = max(
            100,
            list_price + rng.choice([-100, 0, 0, 100]),
        )

        items.append((
            order_id,
            line_no,
            product_id,
            quantity,
            paid_price,
        ))
        total += quantity * paid_price

        if status == "completed":
            completed_lines.append((order_id, line_no, quantity))

    totals[order_id] = total

conn.executemany(
    "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)",
    orders,
)
conn.executemany(
    "INSERT INTO order_items VALUES (?, ?, ?, ?, ?)",
    items,
)

# Exactly 25 completed orders have two successful installments.
completed_ids = [
    order_id
    for order_id in range(1, 301)
    if statuses[order_id - 1] == "completed"
]
split_payment_orders = set(completed_ids[:25])

payments = []
payment_id = 1

for order_id in range(1, 301):
    status = statuses[order_id - 1]

    if status == "completed":
        total = totals[order_id]
        if order_id in split_payment_orders:
            first = total // 2
            amounts = [first, total - first]
        else:
            amounts = [total]

        for amount in amounts:
            payments.append((
                payment_id,
                order_id,
                day(330),
                amount,
                "successful",
            ))
            payment_id += 1

# Fifteen placed orders have a successful partial prepayment.
placed_ids = [
    order_id
    for order_id in range(1, 301)
    if statuses[order_id - 1] == "placed"
]
for order_id in placed_ids[:15]:
    payments.append((
        payment_id,
        order_id,
        day(330),
        max(100, totals[order_id] // 3),
        "successful",
    ))
    payment_id += 1

# Add failed attempts until there are 360 payment rows.
while len(payments) < 360:
    order_id = rng.randrange(1, 301)
    payments.append((
        payment_id,
        order_id,
        day(rng.randrange(90, 330)),
        totals[order_id],
        "failed",
    ))
    payment_id += 1

conn.executemany(
    "INSERT INTO payments VALUES (?, ?, ?, ?, ?)",
    payments,
)

# Forty partial returns and twenty full returns.
# Every return is on a distinct item line from a completed order.
partial_pool = [
    line for line in completed_lines
    if line[2] > 1
]
rng.shuffle(partial_pool)
partial = partial_pool[:40]

used = {
    (order_id, line_no)
    for order_id, line_no, _ in partial
}
full_pool = [
    line for line in completed_lines
    if (line[0], line[1]) not in used
]
rng.shuffle(full_pool)
full = full_pool[:20]

returns = []
for return_id, (order_id, line_no, purchased) in enumerate(
    partial + full,
    1,
):
    returned = purchased - 1 if return_id <= 40 else purchased
    returns.append((
        return_id,
        order_id,
        line_no,
        day(340 + return_id % 20),
        returned,
        rng.choice([
            "damaged",
            "wrong item",
            "changed mind",
        ]),
    ))

conn.executemany(
    "INSERT INTO returns VALUES (?, ?, ?, ?, ?, ?)",
    returns,
)

conn.commit()
conn.close()

print(f"Created {DB}")
print(
    "Rows: 120 customers, 8 categories, 80 products, "
    "300 orders, 750 items, 360 payments, 60 returns"
)
print("Payments: 250 successful, 110 failed")