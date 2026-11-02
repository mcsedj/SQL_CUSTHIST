"""
Synthetic Dataset Generator for Temporal E-Commerce Order History Project
Target DBMS: PostgreSQL with PL/pgSQL Temporal Extensions

Tables Generated:
1. customers (300 records)
2. orders (700 records)
3. order_status_history (2,000 records)

Outputs:
- customers.csv
- orders.csv
- order_status_history.csv
- insert_data.sql

Standard Library only: random, datetime, csv, pathlib, sys
"""

import csv
from datetime import datetime, timedelta
from pathlib import Path
import random
import sys
from typing import Any, Dict, List, Optional, Tuple

# ==============================================================================
# CONFIGURATION & REPRODUCIBILITY
# ==============================================================================
RANDOM_SEED = 42
NUM_CUSTOMERS = 300
NUM_ORDERS = 700
NUM_HISTORY_RECORDS = 2000

# Base timeframe for order simulation
SIMULATION_START = datetime(2024, 1, 1, 8, 0, 0)
SIMULATION_END = datetime(2024, 12, 1, 20, 0, 0)

# ==============================================================================
# REALISTIC SYNTHETIC REFERENCE DATA (International / Foreign)
# ==============================================================================
FIRST_NAMES = [
    # French
    "Jean", "Camille", "Antoine", "Élodie", "Julien", "Chloé", "Pierre", "Mathilde",
    # German & Austrian
    "Lukas", "Maximilian", "Hannah", "Sophie", "Felix", "Leon", "Mia", "Jonas",
    # Spanish
    "Mateo", "Santiago", "Valentina", "Sofía", "Alejandro", "Lucía", "Diego", "Elena",
    # Italian
    "Leonardo", "Francesco", "Giulia", "Lorenzo", "Chiara", "Matteo", "Aurora", "Federico",
    # British & Irish
    "Oliver", "Charlotte", "Harry", "Amelia", "George", "Isla", "Liam", "Aoife",
    # Scandinavian (Swedish, Norwegian, Danish)
    "Freja", "Astrid", "Lars", "Magnus", "Elin", "Soren", "Ingrid", "Henrik",
    # Dutch & Flemish
    "Daan", "Sem", "Lieke", "Fleur", "Thijs", "Bram", "Sanne", "Lars",
    # Japanese & East Asian
    "Kenji", "Yuki", "Haruto", "Aoi", "Ren", "Hina", "Sora", "Mei",
    # Swiss & Other European
    "Beat", "Ursula", "Stefan", "Katja", "Pavel", "Zuzana", "Marek", "Aneta"
]

LAST_NAMES = [
    "Dubois", "Moreau", "Laurent", "Simon", "Michel", "Lefebvre", "Leroy", "Roux",
    "Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker",
    "García", "Rodríguez", "González", "Fernández", "López", "Martínez", "Sánchez", "Pérez",
    "Rossi", "Russo", "Ferrari", "Esposito", "Bianchi", "Romano", "Colombo", "Ricci",
    "Davies", "Evans", "Taylor", "Wilson", "O'Connor", "Walsh", "Murphy", "Smith",
    "Lindqvist", "Johansson", "Nilsson", "Andersson", "Larsson", "Bergström", "Holm",
    "De Jong", "Van Dijk", "Van den Berg", "Bakker", "Jansen", "Visser", "Smit",
    "Tanaka", "Sato", "Takahashi", "Watanabe", "Ito", "Nakamura", "Kobayashi",
    "Novak", "Kowalski", "Dvořák", "Horváth", "Nagy", "Varga", "Huber", "Meier"
]

CITIES_COUNTRIES = [
    ("Paris", "France", "+33"),
    ("Lyon", "France", "+33"),
    ("Marseille", "France", "+33"),
    ("Berlin", "Germany", "+49"),
    ("Munich", "Germany", "+49"),
    ("Hamburg", "Germany", "+49"),
    ("Frankfurt", "Germany", "+49"),
    ("Vienna", "Austria", "+43"),
    ("Salzburg", "Austria", "+43"),
    ("Madrid", "Spain", "+34"),
    ("Barcelona", "Spain", "+34"),
    ("Valencia", "Spain", "+34"),
    ("Rome", "Italy", "+39"),
    ("Milan", "Italy", "+39"),
    ("Florence", "Italy", "+39"),
    ("London", "United Kingdom", "+44"),
    ("Manchester", "United Kingdom", "+44"),
    ("Edinburgh", "United Kingdom", "+44"),
    ("Dublin", "Ireland", "+353"),
    ("Stockholm", "Sweden", "+46"),
    ("Gothenburg", "Sweden", "+46"),
    ("Oslo", "Norway", "+47"),
    ("Copenhagen", "Denmark", "+45"),
    ("Amsterdam", "Netherlands", "+31"),
    ("Rotterdam", "Netherlands", "+31"),
    ("Brussels", "Belgium", "+32"),
    ("Zurich", "Switzerland", "+41"),
    ("Geneva", "Switzerland", "+41"),
    ("Tokyo", "Japan", "+81"),
    ("Osaka", "Japan", "+81"),
    ("Prague", "Czech Republic", "+420"),
    ("Warsaw", "Poland", "+48"),
    ("Budapest", "Hungary", "+36"),
    ("Toronto", "Canada", "+1"),
    ("Montreal", "Canada", "+1")
]

EMAIL_DOMAINS = [
    "gmail.com", "outlook.com", "icloud.com", "yahoo.com", "proton.me",
    "mail.de", "orange.fr", "bluewin.ch", "libero.it", "telecom.net"
]

# Realistic status lifecycle paths with their respective notes
STATUS_TRANSITION_TEMPLATES = [
    # 1. Standard Completed Cycle (5 steps)
    [
        ("PENDING", "Order placed by customer through web portal"),
        ("CONFIRMED", "Payment authorized via payment gateway"),
        ("PROCESSING", "Warehouse fulfillment started and items picked"),
        ("SHIPPED", "Package handed over to carrier service"),
        ("DELIVERED", "Shipment successfully delivered to customer address")
    ],
    # 2. Delivered then Returned (6 steps)
    [
        ("PENDING", "Order placed by customer through web portal"),
        ("CONFIRMED", "Payment authorized via payment gateway"),
        ("PROCESSING", "Warehouse fulfillment started and items picked"),
        ("SHIPPED", "Package handed over to carrier service"),
        ("DELIVERED", "Shipment successfully delivered to customer address"),
        ("RETURNED", "Customer requested return; package received at warehouse")
    ],
    # 3. Currently in Transit (4 steps)
    [
        ("PENDING", "Order placed by customer through web portal"),
        ("CONFIRMED", "Payment authorized via payment gateway"),
        ("PROCESSING", "Warehouse fulfillment started and items picked"),
        ("SHIPPED", "Package handed over to carrier service")
    ],
    # 4. Currently being Packed (3 steps)
    [
        ("PENDING", "Order placed by customer through web portal"),
        ("CONFIRMED", "Payment authorized via payment gateway"),
        ("PROCESSING", "Warehouse fulfillment started and items picked")
    ],
    # 5. Cancelled after Confirmation (3 steps)
    [
        ("PENDING", "Order placed by customer through web portal"),
        ("CONFIRMED", "Payment authorized via payment gateway"),
        ("CANCELLED", "Order cancelled by customer before dispatch")
    ],
    # 6. Cancelled immediately (2 steps)
    [
        ("PENDING", "Order placed by customer through web portal"),
        ("CANCELLED", "Payment declined or cancelled by user at checkout")
    ],
    # 7. Newly Placed Pending Order (1 step)
    [
        ("PENDING", "Order placed by customer through web portal")
    ],
    # 8. Newly Confirmed Order (2 steps)
    [
        ("PENDING", "Order placed by customer through web portal"),
        ("CONFIRMED", "Payment authorized via payment gateway")
    ]
]


# ==============================================================================
# DATA GENERATION FUNCTIONS
# ==============================================================================

def generate_customers(num_customers: int, seed: int) -> List[Dict[str, Any]]:
    """Generates unique customer records with realistic international demographic data."""
    random.seed(seed)
    customers = []
    used_emails = set()

    for cust_id in range(1, num_customers + 1):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        city, country, dial_code = random.choice(CITIES_COUNTRIES)

        # Generate guaranteed unique email address
        clean_first = "".join(c for c in first_name.lower() if c.isalnum())
        clean_last = "".join(c for c in last_name.lower() if c.isalnum())
        domain = random.choice(EMAIL_DOMAINS)
        
        email_candidate = f"{clean_first}.{clean_last}@{domain}"
        counter = 1
        while email_candidate in used_emails:
            email_candidate = f"{clean_first}.{clean_last}{counter}@{domain}"
            counter += 1
        used_emails.add(email_candidate)

        # Realistic phone number
        phone_suffix = "".join([str(random.randint(0, 9)) for _ in range(8)])
        phone = f"{dial_code} {phone_suffix[:4]} {phone_suffix[4:]}"

        # Registration timestamp in 2022-2023 (strictly prior to simulation start)
        days_offset = random.randint(30, 700)
        seconds_offset = random.randint(0, 86399)
        created_at = SIMULATION_START - timedelta(days=days_offset, seconds=seconds_offset)

        customers.append({
            "customer_id": cust_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email_candidate,
            "phone": phone,
            "city": city,
            "country": country,
            "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return customers


def plan_order_history_lengths(num_orders: int, target_history_count: int, seed: int) -> List[int]:
    """
    Distributes exactly target_history_count records across num_orders orders.
    Each order will have between 1 and 6 status transitions.
    """
    random.seed(seed)
    
    # Each order must have at least 1 history record
    counts = [1] * num_orders
    remaining = target_history_count - num_orders

    # Realistic weights for status chain lengths:
    # 1: 5%, 2: 15%, 3: 20%, 4: 25%, 5: 30%, 6: 5%
    weights = [0.05, 0.15, 0.20, 0.25, 0.30, 0.05]
    step_choices = [1, 2, 3, 4, 5, 6]

    # Pre-sample lengths according to realistic distribution
    samples = random.choices(step_choices, weights=weights, k=num_orders)
    
    # Normalize to match exact target_history_count
    current_sum = sum(samples)
    diff = target_history_count - current_sum

    if diff > 0:
        # Add to orders that have less than 6 steps
        eligible = [i for i, c in enumerate(samples) if c < 6]
        random.shuffle(eligible)
        for i in range(diff):
            idx = eligible[i % len(eligible)]
            samples[idx] += 1
    elif diff < 0:
        # Subtract from orders that have more than 1 step
        eligible = [i for i, c in enumerate(samples) if c > 1]
        random.shuffle(eligible)
        for i in range(abs(diff)):
            idx = eligible[i % len(eligible)]
            samples[idx] -= 1

    assert sum(samples) == target_history_count, "Calculated steps must exactly match target."
    return samples


def generate_orders_and_history(
    customers: List[Dict[str, Any]],
    num_orders: int,
    total_history_count: int,
    seed: int
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Generates orders and temporal order_status_history records with:
    - Guaranteed non-overlapping valid_from and valid_until intervals
    - Current record has valid_until as None (empty string in CSV, NULL in SQL)
    - order.current_status matches the last status from history
    - order.updated_at matches valid_from of the current status
    - Total history count is exactly total_history_count
    """
    random.seed(seed + 10)
    customer_ids = [c["customer_id"] for c in customers]
    history_lengths = plan_order_history_lengths(num_orders, total_history_count, seed + 20)

    # Sort orders by initial date for a realistic progressive sequence
    total_simulation_seconds = int((SIMULATION_END - SIMULATION_START).total_seconds())
    order_offsets = sorted([random.randint(0, total_simulation_seconds) for _ in range(num_orders)])

    orders = []
    order_status_history = []
    history_pk = 1

    # Map templates by length for easy retrieval
    templates_by_length: Dict[int, List[List[Tuple[str, str]]]] = {}
    for template in STATUS_TRANSITION_TEMPLATES:
        length = len(template)
        templates_by_length.setdefault(length, []).append(template)

    for order_id in range(1, num_orders + 1):
        cust_id = random.choice(customer_ids)
        order_date = SIMULATION_START + timedelta(seconds=order_offsets[order_id - 1])
        steps_count = history_lengths[order_id - 1]

        # Select a suitable template with length steps_count
        if steps_count in templates_by_length:
            chosen_template = random.choice(templates_by_length[steps_count])
        else:
            # Fallback to standard flow truncated
            standard_flow = STATUS_TRANSITION_TEMPLATES[0]
            chosen_template = standard_flow[:steps_count]

        # Generate non-overlapping temporal periods
        current_valid_from = order_date
        order_history_entries = []

        for step_idx, (status, note) in enumerate(chosen_template):
            is_last_step = (step_idx == len(chosen_template) - 1)

            if is_last_step:
                valid_until = None
            else:
                # Duration between status changes: realistic hours/days
                if status == "PENDING":
                    interval_hours = random.randint(1, 24)
                elif status == "CONFIRMED":
                    interval_hours = random.randint(6, 48)
                elif status == "PROCESSING":
                    interval_hours = random.randint(12, 72)
                elif status == "SHIPPED":
                    interval_hours = random.randint(24, 120)
                elif status == "DELIVERED":
                    interval_hours = random.randint(48, 168)
                else:
                    interval_hours = random.randint(2, 24)

                valid_until = current_valid_from + timedelta(hours=interval_hours)

            entry = {
                "history_id": history_pk,
                "order_id": order_id,
                "status": status,
                "valid_from": current_valid_from.strftime("%Y-%m-%d %H:%M:%S"),
                "valid_until": valid_until.strftime("%Y-%m-%d %H:%M:%S") if valid_until else "",
                "notes": note
            }
            order_history_entries.append(entry)
            order_status_history.append(entry)
            history_pk += 1

            if valid_until:
                current_valid_from = valid_until

        # Current order state mirrors the final history record
        latest_entry = order_history_entries[-1]
        current_status = latest_entry["status"]
        updated_at = latest_entry["valid_from"]

        # Realistic order amount (e.g. 15.00 to 2450.00)
        total_amount = round(random.uniform(15.0, 2450.0), 2)

        orders.append({
            "order_id": order_id,
            "customer_id": cust_id,
            "order_date": order_date.strftime("%Y-%m-%d %H:%M:%S"),
            "total_amount": f"{total_amount:.2f}",
            "current_status": current_status,
            "updated_at": updated_at
        })

    return orders, order_status_history


# ==============================================================================
# DATA INTEGRITY VALIDATION
# ==============================================================================

def validate_dataset(
    customers: List[Dict[str, Any]],
    orders: List[Dict[str, Any]],
    history: List[Dict[str, Any]]
) -> List[str]:
    """
    Performs comprehensive verification of entity counts, primary/foreign keys,
    temporal continuity, latest status synchronization, and nullability rules.
    Returns a list of error strings (empty if valid).
    """
    errors = []

    # 1. Record Counts
    if len(customers) != NUM_CUSTOMERS:
        errors.append(f"Expected {NUM_CUSTOMERS} customers, got {len(customers)}.")
    if len(orders) != NUM_ORDERS:
        errors.append(f"Expected {NUM_ORDERS} orders, got {len(orders)}.")
    if len(history) != NUM_HISTORY_RECORDS:
        errors.append(f"Expected {NUM_HISTORY_RECORDS} history records, got {len(history)}.")

    # 2. Primary Key Uniqueness
    cust_ids = [c["customer_id"] for c in customers]
    if len(cust_ids) != len(set(cust_ids)):
        errors.append("Duplicate primary keys detected in customers.")

    order_ids = [o["order_id"] for o in orders]
    if len(order_ids) != len(set(order_ids)):
        errors.append("Duplicate primary keys detected in orders.")

    hist_ids = [h["history_id"] for h in history]
    if len(hist_ids) != len(set(hist_ids)):
        errors.append("Duplicate primary keys detected in order_status_history.")

    # 3. Foreign Key Integrity
    valid_cust_ids = set(cust_ids)
    for o in orders:
        if o["customer_id"] not in valid_cust_ids:
            errors.append(f"Order {o['order_id']} references non-existent customer {o['customer_id']}.")

    valid_order_ids = set(order_ids)
    for h in history:
        if h["order_id"] not in valid_order_ids:
            errors.append(f"History entry {h['history_id']} references non-existent order {h['order_id']}.")

    # 4. Temporal Integrity & Status Sync
    history_by_order: Dict[int, List[Dict[str, Any]]] = {}
    for h in history:
        history_by_order.setdefault(h["order_id"], []).append(h)

    for o in orders:
        oid = o["order_id"]
        order_hists = history_by_order.get(oid, [])

        if not order_hists:
            errors.append(f"Order {oid} has no status history entries.")
            continue

        # Check earliest history valid_from matches order_date
        first_h = order_hists[0]
        if first_h["valid_from"] != o["order_date"]:
            errors.append(
                f"Order {oid} order_date ({o['order_date']}) does not match first history valid_from ({first_h['valid_from']})."
            )

        # Check latest history status matches order current_status
        last_h = order_hists[-1]
        if last_h["status"] != o["current_status"]:
            errors.append(
                f"Order {oid} current_status ({o['current_status']}) does not match latest history status ({last_h['status']})."
            )

        # Check latest record has blank valid_until
        if last_h["valid_until"] != "":
            errors.append(f"Order {oid} latest history record must have valid_until as empty/null.")

        # Check temporal sequence continuity without overlap
        for i in range(len(order_hists) - 1):
            curr_h = order_hists[i]
            next_h = order_hists[i + 1]

            t_from = datetime.strptime(curr_h["valid_from"], "%Y-%m-%d %H:%M:%S")
            if curr_h["valid_until"] == "":
                errors.append(f"Historical record {curr_h['history_id']} is not final but has empty valid_until.")
                continue

            t_until = datetime.strptime(curr_h["valid_until"], "%Y-%m-%d %H:%M:%S")
            t_next_from = datetime.strptime(next_h["valid_from"], "%Y-%m-%d %H:%M:%S")

            if t_from >= t_until:
                errors.append(f"History entry {curr_h['history_id']} has valid_from >= valid_until.")
            if t_until != t_next_from:
                errors.append(
                    f"Discontinuity or overlap between history {curr_h['history_id']} and {next_h['history_id']}."
                )

    return errors


# ==============================================================================
# EXPORT FUNCTIONS (CSV & SQL)
# ==============================================================================

def write_csv(filepath: Path, fieldnames: List[str], data: List[Dict[str, Any]]) -> None:
    """Writes a list of dictionaries to a standard CSV file."""
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def escape_sql_str(value: Any) -> str:
    """Properly escapes SQL strings for PostgreSQL insertion."""
    if value is None:
        return "NULL"
    val_str = str(value)
    # Double single quotes for standard SQL escaping
    escaped = val_str.replace("'", "''")
    return f"'{escaped}'"


def write_sql_script(
    filepath: Path,
    customers: List[Dict[str, Any]],
    orders: List[Dict[str, Any]],
    history: List[Dict[str, Any]],
    batch_size: int = 250
) -> None:
    """
    Generates a clean PostgreSQL script with batched INSERT statements.
    Formats timestamps, numerics, and handles NULL valid_until values properly.
    """
    with open(filepath, mode="w", encoding="utf-8") as f:
        f.write("-- =====================================================================\n")
        f.write("-- Synthetic Temporal E-Commerce Dataset Import Script\n")
        f.write("-- Target: PostgreSQL\n")
        f.write(f"-- Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"-- Counts: {len(customers)} customers, {len(orders)} orders, {len(history)} status history records\n")
        f.write("-- =====================================================================\n\n")
        f.write("BEGIN;\n\n")

        # 1. Insert Customers
        f.write("-- ---------------------------------------------------------------------\n")
        f.write("-- 1. Insert Customers\n")
        f.write("-- ---------------------------------------------------------------------\n")
        for i in range(0, len(customers), batch_size):
            batch = customers[i:i + batch_size]
            f.write("INSERT INTO customers (customer_id, first_name, last_name, email, phone, city, country, created_at) VALUES\n")
            rows = []
            for c in batch:
                row_str = (
                    f"  ({c['customer_id']}, "
                    f"{escape_sql_str(c['first_name'])}, "
                    f"{escape_sql_str(c['last_name'])}, "
                    f"{escape_sql_str(c['email'])}, "
                    f"{escape_sql_str(c['phone'])}, "
                    f"{escape_sql_str(c['city'])}, "
                    f"{escape_sql_str(c['country'])}, "
                    f"TIMESTAMP {escape_sql_str(c['created_at'])})"
                )
                rows.append(row_str)
            f.write(",\n".join(rows) + ";\n\n")

        # 2. Insert Orders
        f.write("-- ---------------------------------------------------------------------\n")
        f.write("-- 2. Insert Orders\n")
        f.write("-- ---------------------------------------------------------------------\n")
        for i in range(0, len(orders), batch_size):
            batch = orders[i:i + batch_size]
            f.write("INSERT INTO orders (order_id, customer_id, order_date, total_amount, current_status, updated_at) VALUES\n")
            rows = []
            for o in batch:
                row_str = (
                    f"  ({o['order_id']}, "
                    f"{o['customer_id']}, "
                    f"TIMESTAMP {escape_sql_str(o['order_date'])}, "
                    f"{o['total_amount']}, "
                    f"{escape_sql_str(o['current_status'])}, "
                    f"TIMESTAMP {escape_sql_str(o['updated_at'])})"
                )
                rows.append(row_str)
            f.write(",\n".join(rows) + ";\n\n")

        # 3. Insert Order Status History
        f.write("-- ---------------------------------------------------------------------\n")
        f.write("-- 3. Insert Order Status History\n")
        f.write("-- ---------------------------------------------------------------------\n")
        for i in range(0, len(history), batch_size):
            batch = history[i:i + batch_size]
            f.write("INSERT INTO order_status_history (history_id, order_id, status, valid_from, valid_until, notes) VALUES\n")
            rows = []
            for h in batch:
                valid_until_sql = (
                    f"TIMESTAMP {escape_sql_str(h['valid_until'])}" if h['valid_until'] else "NULL"
                )
                row_str = (
                    f"  ({h['history_id']}, "
                    f"{h['order_id']}, "
                    f"{escape_sql_str(h['status'])}, "
                    f"TIMESTAMP {escape_sql_str(h['valid_from'])}, "
                    f"{valid_until_sql}, "
                    f"{escape_sql_str(h['notes'])})"
                )
                rows.append(row_str)
            f.write(",\n".join(rows) + ";\n\n")

        f.write("COMMIT;\n")


# ==============================================================================
# MAIN EXECUTION ROUTINE
# ==============================================================================

def main() -> None:
    # Ensure UTF-8 output encoding on Windows consoles
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print("=" * 70)
    print("TEMPORAL E-COMMERCE DATASET GENERATOR FOR POSTGRESQL")
    print("=" * 70)
    print(f"Random Seed: {RANDOM_SEED}")
    print(f"Target Counts: Customers={NUM_CUSTOMERS}, Orders={NUM_ORDERS}, History={NUM_HISTORY_RECORDS}\n")

    output_dir = Path(__file__).resolve().parent

    try:
        # Step 1: Generate Entities
        print("[1/4] Generating customers...")
        customers = generate_customers(NUM_CUSTOMERS, RANDOM_SEED)
        print(f"      [OK] Generated {len(customers)} customer records.")

        print("[2/4] Generating orders and temporal order status history...")
        orders, history = generate_orders_and_history(
            customers, NUM_ORDERS, NUM_HISTORY_RECORDS, RANDOM_SEED
        )
        print(f"      [OK] Generated {len(orders)} orders.")
        print(f"      [OK] Generated {len(history)} order_status_history records.")

        # Step 2: Validate Data Integrity
        print("[3/4] Running automatic data validation checks...")
        validation_errors = validate_dataset(customers, orders, history)

        if validation_errors:
            print("\n[ERROR] DATA INTEGRITY ERRORS DETECTED:")
            for err in validation_errors:
                print(f"  - {err}")
            sys.exit(1)
        else:
            print("      [OK] Primary keys uniqueness verified.")
            print("      [OK] Foreign key consistency verified.")
            print("      [OK] Non-overlapping temporal validity intervals verified.")
            print("      [OK] Active status sync with current_status verified.")
            print("      [OK] Current status valid_until == NULL/empty verified.")

        # Step 3: Export to CSV and SQL
        print("[4/4] Exporting dataset to CSV and SQL files...")

        # Export customers.csv
        cust_csv_path = output_dir / "customers.csv"
        cust_fields = ["customer_id", "first_name", "last_name", "email", "phone", "city", "country", "created_at"]
        write_csv(cust_csv_path, cust_fields, customers)
        print(f"      [OK] Saved: {cust_csv_path.name} ({cust_csv_path.stat().st_size:,} bytes)")

        # Export orders.csv
        orders_csv_path = output_dir / "orders.csv"
        orders_fields = ["order_id", "customer_id", "order_date", "total_amount", "current_status", "updated_at"]
        write_csv(orders_csv_path, orders_fields, orders)
        print(f"      [OK] Saved: {orders_csv_path.name} ({orders_csv_path.stat().st_size:,} bytes)")

        # Export order_status_history.csv
        history_csv_path = output_dir / "order_status_history.csv"
        history_fields = ["history_id", "order_id", "status", "valid_from", "valid_until", "notes"]
        write_csv(history_csv_path, history_fields, history)
        print(f"      [OK] Saved: {history_csv_path.name} ({history_csv_path.stat().st_size:,} bytes)")

        # Export insert_data.sql
        sql_path = output_dir / "insert_data.sql"
        write_sql_script(sql_path, customers, orders, history)
        print(f"      [OK] Saved: {sql_path.name} ({sql_path.stat().st_size:,} bytes)")

        # Summary Breakdown
        status_distribution: Dict[str, int] = {}
        for h in history:
            status_distribution[h["status"]] = status_distribution.get(h["status"], 0) + 1

        active_status_distribution: Dict[str, int] = {}
        for o in orders:
            active_status_distribution[o["current_status"]] = active_status_distribution.get(o["current_status"], 0) + 1

        print("\n" + "=" * 70)
        print("GENERATION SUMMARY REPORT")
        print("=" * 70)
        print(f"{'Table Name':<25} | {'Records':<10} | {'Destination File':<25}")
        print("-" * 70)
        print(f"{'customers':<25} | {len(customers):<10} | {'customers.csv / SQL':<25}")
        print(f"{'orders':<25} | {len(orders):<10} | {'orders.csv / SQL':<25}")
        print(f"{'order_status_history':<25} | {len(history):<10} | {'order_status_history.csv / SQL':<25}")
        print("-" * 70)
        print(f"Total Rows Generated:     {len(customers) + len(orders) + len(history):,}")

        print("\nDistribution of Status Transitions in History (2,000 records):")
        for stat, count in sorted(status_distribution.items(), key=lambda x: -x[1]):
            print(f"  * {stat:<15}: {count:>4} events ({count / NUM_HISTORY_RECORDS * 100:.1f}%)")

        print("\nCurrent Orders Status Distribution (700 orders):")
        for stat, count in sorted(active_status_distribution.items(), key=lambda x: -x[1]):
            print(f"  * {stat:<15}: {count:>4} orders ({count / NUM_ORDERS * 100:.1f}%)")

        print("\nAll data files generated successfully and ready for PostgreSQL import!")
        print("=" * 70)

    except Exception as e:
        print(f"\n[ERROR] Unexpected error during dataset generation: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
