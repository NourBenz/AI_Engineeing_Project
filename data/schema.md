# P0 database design: Online bookstore

Our Natural Language → SQL benchmark uses a small fictional online bookstore. All customers, products, orders, and payments are synthetic.

## Tables

- `customers`: customer ID, name, email, city, country, join date, active status.
- `categories`: category ID and category name.
- `products`: product ID, category ID, name, price, active status.
- `orders`: order ID, customer ID, order date, status, completion date, cancellation date.
- `order_items`: order ID, line number, product ID, quantity, price paid per item.
- `payments`: payment ID, order ID, attempt date, amount, successful or failed status.
- `returns`: return ID, order ID, item line number, return date, quantity, reason.

## Relationships

A customer can have many orders. An order can contain many items and have multiple payment attempts. A product belongs to one category and can appear in many orders. An order item may have a return.

## Definitions

- **Order total:** the sum of quantity × price paid for every item in an order.
- **Completed order:** an order with status `completed`.
- **Cancelled order:** an order with status `cancelled`.
- **Successful payment:** a payment with status `successful`; failed attempts do not count as money received.
- **Returned item:** an order item recorded in the `returns` table.
- **Active customer:** a customer whose active status is 1. This does not mean they have placed an order.

The data will include customers with no orders, products never bought, cancelled orders, failed payments, partial returns, and repeat purchases. These cases help distinguish correct SQL from incorrect SQL.