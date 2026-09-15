PRAGMA foreign_keys = ON;

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    city TEXT NOT NULL,
    country TEXT NOT NULL,
    joined_at TEXT NOT NULL,
    is_active INTEGER NOT NULL CHECK (is_active IN (0, 1))
);

CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY,
    category_name TEXT NOT NULL UNIQUE
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    category_id INTEGER NOT NULL,
    product_name TEXT NOT NULL,
    list_price_cents INTEGER NOT NULL CHECK (list_price_cents > 0),
    is_active INTEGER NOT NULL CHECK (is_active IN (0, 1)),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    ordered_at TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('placed', 'completed', 'cancelled')),
    completed_at TEXT,
    cancelled_at TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CHECK (
        (status = 'placed' AND completed_at IS NULL AND cancelled_at IS NULL)
        OR
        (status = 'completed' AND completed_at IS NOT NULL AND cancelled_at IS NULL)
        OR
        (status = 'cancelled' AND completed_at IS NULL AND cancelled_at IS NOT NULL)
    )
);

CREATE TABLE order_items (
    order_id INTEGER NOT NULL,
    line_no INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price_cents INTEGER NOT NULL CHECK (unit_price_cents > 0),
    PRIMARY KEY (order_id, line_no),
    UNIQUE (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE payments (
    payment_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    attempted_at TEXT NOT NULL,
    amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
    status TEXT NOT NULL CHECK (status IN ('successful', 'failed')),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE TABLE returns (
    return_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    line_no INTEGER NOT NULL,
    returned_at TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    reason TEXT NOT NULL,
    UNIQUE (order_id, line_no),
    FOREIGN KEY (order_id, line_no)
        REFERENCES order_items(order_id, line_no)
);