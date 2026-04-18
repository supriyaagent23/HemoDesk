import sqlite3

DB_NAME = "hemodesk.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS donors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        blood_type TEXT NOT NULL,
        phone TEXT NOT NULL,
        gender TEXT DEFAULT '',
        last_donation TEXT DEFAULT ''
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS stock (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        blood_type TEXT NOT NULL UNIQUE,
        units INTEGER NOT NULL DEFAULT 0
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT NOT NULL,
        blood_type TEXT NOT NULL,
        units INTEGER NOT NULL,
        urgency TEXT NOT NULL,
        status TEXT DEFAULT 'Pending',
        created_date TEXT DEFAULT ''
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS donations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        donor_id INTEGER NOT NULL,
        blood_type TEXT NOT NULL,
        units INTEGER NOT NULL,
        donation_date TEXT DEFAULT '',
        FOREIGN KEY (donor_id) REFERENCES donors(id)
    )
    """)

    # Safe column additions for donations
    for col_def in [
        "ALTER TABLE donations ADD COLUMN status TEXT DEFAULT 'Pending'",
        "ALTER TABLE donations ADD COLUMN actual_blood_type TEXT",
        "ALTER TABLE donations ADD COLUMN notes TEXT DEFAULT ''",
    ]:
        try:
            c.execute(col_def)
        except sqlite3.OperationalError:
            pass

    # Seed confirmed blood types into stock
    for bt in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]:
        c.execute(
            "INSERT OR IGNORE INTO stock (blood_type, units) VALUES (?, 0)", (bt,)
        )

    conn.commit()
    conn.close()