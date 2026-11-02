
-- Table 1: Customers
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    first_name VARCHAR(60) NOT NULL,
    last_name VARCHAR(60) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(30),
    city VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL
);

-- Table 2: Orders
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL
        REFERENCES customers(customer_id),
    order_date TIMESTAMP NOT NULL,
    total_amount NUMERIC(12, 2) NOT NULL
        CHECK (total_amount >= 0),
    current_status VARCHAR(20) NOT NULL
        CHECK (current_status IN (
            'PENDING',
            'CONFIRMED',
            'PROCESSING',
            'SHIPPED',
            'DELIVERED',
            'CANCELLED',
            'RETURNED'
        )),
    updated_at TIMESTAMP NOT NULL
);

-- Table 3: Temporal order status history
CREATE TABLE order_status_history (
    history_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL
        REFERENCES orders(order_id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL
        CHECK (status IN (
            'PENDING',
            'CONFIRMED',
            'PROCESSING',
            'SHIPPED',
            'DELIVERED',
            'CANCELLED',
            'RETURNED'
        )),
    valid_from TIMESTAMP NOT NULL,
    valid_until TIMESTAMP,
    notes TEXT,
    CHECK (
        valid_until IS NULL
        OR valid_until > valid_from
    )
);

-- Indexes for common queries
CREATE INDEX idx_orders_customer
    ON orders(customer_id);

CREATE INDEX idx_history_order_time
    ON order_status_history(order_id, valid_from);

-- At most one open-ended history record per order
CREATE UNIQUE INDEX idx_one_open_history_per_order
    ON order_status_history(order_id)
    WHERE valid_until IS NULL;

 
 


