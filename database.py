import sqlite3
from datetime import datetime

DB_NAME = "nobat.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS businesses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        owner_name TEXT NOT NULL,
        phone TEXT NOT NULL,
        address TEXT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        subscription_end TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        business_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        price INTEGER NOT NULL,
        duration INTEGER NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS working_hours (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        business_id INTEGER NOT NULL,
        day_of_week INTEGER NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        is_closed INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        business_id INTEGER NOT NULL,
        service_id INTEGER NOT NULL,
        customer_name TEXT NOT NULL,
        customer_phone TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

def add_business(name, owner_name, phone, address, username, password):
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO businesses (name, owner_name, phone, address, username, password, subscription_end, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, owner_name, phone, address, username, password,
              datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

def get_business(username, password):
    conn = get_connection()
    row = conn.execute("SELECT * FROM businesses WHERE username = ? AND password = ?",
                       (username, password)).fetchone()
    conn.close()
    return row

def get_business_by_username(username):
    conn = get_connection()
    row = conn.execute("SELECT * FROM businesses WHERE username = ?", (username,)).fetchone()
    conn.close()
    return row

def get_business_by_id(business_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM businesses WHERE id = ?", (business_id,)).fetchone()
    conn.close()
    return row

def get_all_businesses():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM businesses ORDER BY id DESC").fetchall()
    conn.close()
    return rows

def add_service(business_id, name, price, duration):
    conn = get_connection()
    conn.execute("INSERT INTO services (business_id, name, price, duration) VALUES (?, ?, ?, ?)",
                 (business_id, name, price, duration))
    conn.commit()
    conn.close()

def get_services(business_id):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM services WHERE business_id = ?", (business_id,)).fetchall()
    conn.close()
    return rows

def delete_service(business_id, service_id):
    conn = get_connection()
    conn.execute("DELETE FROM services WHERE id = ? AND business_id = ?", (service_id, business_id))
    conn.commit()
    conn.close()

def set_working_hours(business_id, day_of_week, start_time, end_time, is_closed):
    conn = get_connection()
    existing = conn.execute("SELECT id FROM working_hours WHERE business_id = ? AND day_of_week = ?",
                            (business_id, day_of_week)).fetchone()
    if existing:
        conn.execute("""UPDATE working_hours SET start_time = ?, end_time = ?, is_closed = ?
                        WHERE business_id = ? AND day_of_week = ?""",
                     (start_time, end_time, is_closed, business_id, day_of_week))
    else:
        conn.execute("""INSERT INTO working_hours (business_id, day_of_week, start_time, end_time, is_closed)
                        VALUES (?, ?, ?, ?, ?)""",
                     (business_id, day_of_week, start_time, end_time, is_closed))
    conn.commit()
    conn.close()

def get_working_hours(business_id):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM working_hours WHERE business_id = ? ORDER BY day_of_week",
                        (business_id,)).fetchall()
    conn.close()
    return rows

def add_appointment(business_id, service_id, customer_name, customer_phone, date, time):
    conn = get_connection()
    conn.execute("""INSERT INTO appointments (business_id, service_id, customer_name, customer_phone, date, time, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)""",
                 (business_id, service_id, customer_name, customer_phone, date, time,
                  datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()

def get_appointments(business_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT a.*, s.name as service_name
        FROM appointments a
        JOIN services s ON a.service_id = s.id
        WHERE a.business_id = ?
        ORDER BY a.date DESC, a.time DESC
    """, (business_id,)).fetchall()
    conn.close()
    return rows

def get_appointments_by_date(business_id, date):
    conn = get_connection()
    rows = conn.execute("""
        SELECT a.*, s.name as service_name
        FROM appointments a
        JOIN services s ON a.service_id = s.id
        WHERE a.business_id = ? AND a.date = ?
        ORDER BY a.time
    """, (business_id, date)).fetchall()
    conn.close()
    return rows

def update_appointment_status(appointment_id, status):
    conn = get_connection()
    conn.execute("UPDATE appointments SET status = ? WHERE id = ?", (status, appointment_id))
    conn.commit()
    conn.close()

def get_today_appointments(business_id):
    today = datetime.now().strftime("%Y-%m-%d")
    return get_appointments_by_date(business_id, today)
