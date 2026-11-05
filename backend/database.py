"""
database.py - SQLite Database Management and Seeding for Courier Tracking.
Identifier: FR-01 / US-01 / TC-01
Student: MASTAN SAB (Roll No: 60, Class 5B, Case 60)
"""

import os
import sqlite3
from datetime import datetime, timedelta

DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database"))
DB_PATH = os.path.join(DB_DIR, "courier_tracking.db")


def get_db_connection():
    """Establishes SQLite connection with row factory for dictionary-like access."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(seed: bool = True):
    """Creates database tables and inserts seed data if empty."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()

    # Parcels master table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS parcels (
        tracking_id TEXT PRIMARY KEY,
        sender_name TEXT NOT NULL,
        recipient_name TEXT NOT NULL,
        origin TEXT NOT NULL,
        destination TEXT NOT NULL,
        weight_kg REAL NOT NULL,
        current_status TEXT NOT NULL,
        current_location TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)

    # Audit History table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS parcel_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking_id TEXT NOT NULL,
        from_status TEXT,
        to_status TEXT NOT NULL,
        location TEXT NOT NULL,
        notes TEXT,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (tracking_id) REFERENCES parcels (tracking_id)
    );
    """)

    # Monitoring metrics log table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS metrics_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        endpoint TEXT NOT NULL,
        response_time_ms REAL NOT NULL,
        status_code INTEGER NOT NULL,
        is_success INTEGER NOT NULL,
        timestamp TEXT NOT NULL
    );
    """)

    conn.commit()

    if seed:
        cursor.execute("SELECT COUNT(*) FROM parcels")
        count = cursor.fetchone()[0]
        if count == 0:
            _seed_sample_data(conn)

    conn.close()


def _seed_sample_data(conn):
    """Seeds at least 20 realistic parcel records across all statuses."""
    cursor = conn.cursor()
    base_time = datetime.now() - timedelta(days=4)

    sample_parcels = [
        # (tracking_id, sender, recipient, origin, destination, weight, status, location, hours_ago)
        ("TRK-60-1001", "Acme Retail Ltd", "Rajesh Kumar", "Mumbai Hub", "Delhi North Hub", 2.5, "Delivered", "Delivered to recipient", 72),
        ("TRK-60-1002", "Nova Tech", "Pooja Sharma", "Bengaluru Central", "Hyderabad Hub", 1.2, "Delivered", "Delivered to recipient", 60),
        ("TRK-60-1003", "Apex Garments", "Amit Verma", "Surat Hub", "Pune Distribution", 3.8, "Delivered", "Delivered to recipient", 48),
        ("TRK-60-1004", "Sun Pharma", "Dr. S. Nair", "Ahmedabad", "Chennai Hub", 0.8, "Delivered", "Delivered to recipient", 36),
        ("TRK-60-1005", "BookWorld", "Deepa Patel", "Kolkata Hub", "Bhubaneswar Hub", 1.5, "Delivered", "Delivered to recipient", 24),
        ("TRK-60-1006", "ElectroKart", "Vikas Malhotra", "Gurugram Hub", "Jaipur Sorting", 4.2, "In Transit", "En route to Jaipur Hub", 18),
        ("TRK-60-1007", "Urban Crafts", "Neha Reddy", "Hyderabad Hub", "Vijayawada Center", 2.0, "In Transit", "National Highway Transit Point", 14),
        ("TRK-60-1008", "BioGenix Lab", "K. R. Rao", "Bengaluru Central", "Coimbatore Hub", 0.5, "In Transit", "Salem Transit Hub", 10),
        ("TRK-60-1009", "Zenith Sports", "Sanjay Gupta", "Ludhiana Hub", "Chandigarh Office", 5.5, "In Transit", "Ambala Express Route", 8),
        ("TRK-60-1010", "FashionWave", "Priya Sen", "Mumbai Hub", "Indore Delivery Center", 1.8, "In Transit", "Nashik Sorting Facility", 6),
        ("TRK-60-1011", "Modern Footwear", "Rahul Roy", "Agra Hub", "Lucknow Hub", 2.2, "Picked Up", "Origin Pickup Warehouse", 12),
        ("TRK-60-1012", "Green Agro Seeds", "M. K. Joshi", "Nagpur Hub", "Bhopal Center", 8.0, "Picked Up", "Courier Sorting Center", 8),
        ("TRK-60-1013", "Zen Mobile Care", "Anand Kulkarni", "Pune Hub", "Goa Distribution", 0.4, "Picked Up", "Parcel Scan Facility", 5),
        ("TRK-60-1014", "Silver Jewellers", "Meena Iyer", "Jaipur Hub", "Jodhpur Center", 0.3, "Picked Up", "Regional Sorting Depot", 4),
        ("TRK-60-1015", "Office Supplies Co", "T. Narayanan", "Chennai Hub", "Madurai Center", 6.0, "Picked Up", "Warehouse Bay 3", 3),
        ("TRK-60-1016", "Cloud Kitchen", "Faizan Ahmed", "Delhi Central", "Noida Sector 62", 1.1, "Delayed", "Fog alert at Yamuna Expressway", 15),
        ("TRK-60-1017", "Heavy Machinery Ltd", "Om Prakash", "Jamshedpur Hub", "Ranchi Hub", 14.5, "Delayed", "Vehicle breakdown - mechanic dispatched", 20),
        ("TRK-60-1018", "Optics Direct", "Sneha Chawla", "Bengaluru Central", "Mysuru Branch", 0.6, "Delivery Failed", "Customer premises locked - 1st attempt", 16),
        ("TRK-60-1019", "Global Auto Parts", "Suresh Menon", "Chennai Hub", "Kochi Hub", 9.2, "Registered", "Shipment label generated", 2),
        ("TRK-60-1020", "Organic Naturals", "Anjali Deshmukh", "Mumbai Hub", "Thane East Hub", 1.4, "Registered", "Shipment awaiting courier pickup", 1)
    ]

    for item in sample_parcels:
        trk_id, sender, recipient, origin, dest, weight, status, loc, hours_ago = item
        created = (base_time + timedelta(hours=hours_ago)).strftime("%Y-%m-%d %H:%M:%S")
        updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
        INSERT INTO parcels (tracking_id, sender_name, recipient_name, origin, destination,
                            weight_kg, current_status, current_location, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (trk_id, sender, recipient, origin, dest, weight, status, loc, created, updated))

        # Insert initial history record
        cursor.execute("""
        INSERT INTO parcel_history (tracking_id, from_status, to_status, location, notes, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (trk_id, None, "Registered", origin, "Shipment booked and registered into system", created))

        # Insert progressive history if status advanced
        if status in ["Picked Up", "In Transit", "Delayed", "Delivered", "Delivery Failed"]:
            cursor.execute("""
            INSERT INTO parcel_history (tracking_id, from_status, to_status, location, notes, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (trk_id, "Registered", "Picked Up", origin, "Parcel received at origin collection depot",
                  (datetime.strptime(created, "%Y-%m-%d %H:%M:%S") + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")))

        if status in ["In Transit", "Delayed", "Delivered", "Delivery Failed"]:
            cursor.execute("""
            INSERT INTO parcel_history (tracking_id, from_status, to_status, location, notes, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (trk_id, "Picked Up", "In Transit", "Transit Corridor", "Dispatched on transit route",
                  (datetime.strptime(created, "%Y-%m-%d %H:%M:%S") + timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S")))

        if status == "Delayed":
            cursor.execute("""
            INSERT INTO parcel_history (tracking_id, from_status, to_status, location, notes, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (trk_id, "In Transit", "Delayed", loc, "Transit delay encountered", updated))

        if status == "Delivery Failed":
            cursor.execute("""
            INSERT INTO parcel_history (tracking_id, from_status, to_status, location, notes, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (trk_id, "In Transit", "Delivery Failed", loc, "Recipient unavailable on first attempt", updated))

        if status == "Delivered":
            cursor.execute("""
            INSERT INTO parcel_history (tracking_id, from_status, to_status, location, notes, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (trk_id, "In Transit", "Delivered", dest, "Handed over to recipient with signature", updated))

    conn.commit()


if __name__ == "__main__":
    init_db(seed=True)
    print("Database initialized and 20 sample parcels seeded successfully at:", DB_PATH)
