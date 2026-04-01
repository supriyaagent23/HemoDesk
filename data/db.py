import sqlite3

DB_NAME = "hemodesk.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS donors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        blood_type TEXT NOT NULL,
        phone TEXT NOT NULL,
        last_donation TEXT DEFAULT ''
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS stock (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        blood_type TEXT NOT NULL UNIQUE,
        units INTEGER NOT NULL DEFAULT 0
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT NOT NULL,
        blood_type TEXT NOT NULL,
        units INTEGER NOT NULL,
        urgency TEXT NOT NULL,
        status TEXT DEFAULT 'Pending',
        created_date TEXT DEFAULT ''
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS donations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        donor_id INTEGER NOT NULL,
        blood_type TEXT NOT NULL,
        units INTEGER NOT NULL,
        donation_date TEXT DEFAULT '',
        FOREIGN KEY (donor_id) REFERENCES donors(id)
    )""")

    blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    for bt in blood_types:
        c.execute("INSERT OR IGNORE INTO stock (blood_type, units) VALUES (?, 0)", (bt,))

    conn.commit()
    conn.close()