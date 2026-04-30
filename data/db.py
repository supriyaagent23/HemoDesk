import sqlite3

DB_NAME = "hemodesk.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Donors table
    c.execute("""
    CREATE TABLE IF NOT EXISTS donors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        blood_type TEXT NOT NULL,
        phone TEXT NOT NULL,
        gender TEXT DEFAULT '',
        last_donation TEXT DEFAULT '',
        total_donations INTEGER DEFAULT 0
    )
    """)

    # Stock table
    c.execute("""
    CREATE TABLE IF NOT EXISTS stock (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        blood_type TEXT NOT NULL UNIQUE,
        units INTEGER NOT NULL DEFAULT 0
    )
    """)

    # Requests table
    c.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT NOT NULL,
        blood_type TEXT NOT NULL,
        units INTEGER NOT NULL,
        urgency TEXT NOT NULL,
        status TEXT DEFAULT 'Pending',
        created_date TEXT DEFAULT '',
        fulfilled_date TEXT DEFAULT ''
    )
    """)

    # Donations table
    c.execute("""
    CREATE TABLE IF NOT EXISTS donations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        donor_id INTEGER NOT NULL,
        blood_type TEXT NOT NULL,
        units INTEGER NOT NULL,
        donation_date TEXT DEFAULT '',
        status TEXT DEFAULT 'Pending',
        lab_verified BOOLEAN DEFAULT 0,
        notes TEXT DEFAULT '',
        actual_blood_type TEXT,
        FOREIGN KEY (donor_id) REFERENCES donors(id)
    )
    """)

    # Thank you messages table
    c.execute("""
    CREATE TABLE IF NOT EXISTS thank_you_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        donor_id INTEGER NOT NULL,
        donation_id INTEGER NOT NULL,
        message_sent_date TEXT DEFAULT '',
        message_type TEXT DEFAULT 'donation',
        FOREIGN KEY (donor_id) REFERENCES donors(id),
        FOREIGN KEY (donation_id) REFERENCES donations(id)
    )
    """)

    # Add missing columns for existing tables (for backward compatibility)
    try:
        c.execute("ALTER TABLE donors ADD COLUMN total_donations INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        c.execute("ALTER TABLE donations ADD COLUMN lab_verified BOOLEAN DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    
    try:
        c.execute("ALTER TABLE donations ADD COLUMN notes TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    
    try:
        c.execute("ALTER TABLE donations ADD COLUMN actual_blood_type TEXT")
    except sqlite3.OperationalError:
        pass
    
    try:
        c.execute("ALTER TABLE requests ADD COLUMN fulfilled_date TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass

    # Seed blood types
    for bt in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]:
        c.execute(
            "INSERT OR IGNORE INTO stock (blood_type, units) VALUES (?, 0)", (bt,)
        )

    conn.commit()
    conn.close()