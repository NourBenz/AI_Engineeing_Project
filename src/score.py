from collections import Counter
from pathlib import Path
import json
import math
import sqlite3
import time

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "bookstore.sqlite"
ITEMS = ROOT / "data" / "items.jsonl"


def run_query(sql):
    if not isinstance(sql, str) or not sql.strip():
        return None, "empty_sql"

    sql = sql.strip()
    if not sql.upper().startswith(("SELECT", "WITH")):
        return None, "not_select"

    conn = sqlite3.connect(DB.as_uri() + "?mode=ro", uri=True)
    conn.execute("PRAGMA query_only = ON")

    deadline = time.monotonic() + 2.0
    conn.set_progress_handler(
        lambda: 1 if time.monotonic() > deadline else 0,
        1000,
    )

    try:
        cursor = conn.execute(sql)
        rows = cursor.fetchmany(1001)

        if len(rows) > 1000:
            return None, "too_many_rows"

        return (len(cursor.description), rows), None

    except sqlite3.Error as error:
        if "interrupted" in str(error).lower():
            return None, "timeout"
        return None, f"sql_error: {error}"

    finally:
        conn.close()


def same_value(a, b):
    if a is None or b is None:
        return a is None and b is None

    numbers = (int, float)
    if isinstance(a, numbers) and isinstance(b, numbers):
        if isinstance(a, int) and isinstance(b, int):
            return a == b
        return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-6)

    return a == b


def same_row(a, b):
    return len(a) == len(b) and all(
        same_value(x, y) for x, y in zip(a, b)
    )


def same_unordered_rows(actual, expected):
    if len(actual) != len(expected):
        return False

    # Exact values use a fast multiset comparison.
    has_float = any(
        isinstance(value, float)
        for row in actual + expected
        for value in row
    )
    if not has_float:
        return Counter(actual) == Counter(expected)

    # For decimal values, match rows while preserving duplicates.
    possible = [
        [
            j for j, actual_row in enumerate(actual)
            if same_row(expected_row, actual_row)
        ]
        for expected_row in expected
    ]
    matched_to = [-1] * len(actual)

    def assign(expected_index, visited):
        for actual_index in possible[expected_index]:
            if actual_index in visited:
                continue
            visited.add(actual_index)

            previous = matched_to[actual_index]
            if previous == -1 or assign(previous, visited):
                matched_to[actual_index] = expected_index
                return True
        return False

    for expected_index in sorted(
        range(len(expected)),
        key=lambda i: len(possible[i]),
    ):
        if not assign(expected_index, set()):
            return False

    return True


def score_item(item, proposed_sql):
    expected, expected_error = run_query(item["reference_sql"])
    if expected_error:
        raise ValueError(
            f"Broken reference SQL for {item['id']}: {expected_error}"
        )

    actual, actual_error = run_query(proposed_sql)
    if actual_error:
        return {"correct": False, "error": actual_error}

    expected_columns, expected_rows = expected
    actual_columns, actual_rows = actual

    if expected_columns != actual_columns:
        correct = False
    elif item["order_sensitive"]:
        correct = (
            len(actual_rows) == len(expected_rows)
            and all(
                same_row(a, e)
                for a, e in zip(actual_rows, expected_rows)
            )
        )
    else:
        correct = same_unordered_rows(actual_rows, expected_rows)

    return {"correct": correct, "error": None}


def load_items():
    items = []
    for line in ITEMS.read_text(encoding="utf-8").splitlines():
        if line.strip():
            items.append(json.loads(line))
    return items


if __name__ == "__main__":
    items = load_items()

    count_item = next(i for i in items if i["id"] == "dev_002")
    print(
        "Correct count:",
        score_item(
            count_item,
            "SELECT COUNT(*) FROM customers WHERE country = 'Tunisia'",
        ),
    )
    print(
        "Wrong count:",
        score_item(
            count_item,
            "SELECT COUNT(*) FROM customers",
        ),
    )

    avg_item = next(i for i in items if i["id"] == "dev_010")
    equivalent_avg_sql = """
        SELECT ca.category_name,
               SUM(p.list_price_cents) * 1.0 / COUNT(*)
        FROM categories AS ca
        JOIN products AS p ON p.category_id = ca.category_id
        WHERE p.is_active = 1
        GROUP BY ca.category_id, ca.category_name
        ORDER BY ca.category_name ASC
    """
    print(
        "Equivalent average:",
        score_item(avg_item, equivalent_avg_sql),
    )