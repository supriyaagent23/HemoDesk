import sqlite3
from datetime import datetime, timedelta
from data.db import get_connection
from models.donor import Donor
from models.donation import Donation
from models.request import Request


# ═══════════════════════════════════════════════════════════════════
#  SETTINGS
# ═══════════════════════════════════════════════════════════════════

_settings = {
    "low_stock_threshold": 5,
    "max_stock_limit": 100,
    "donation_wait_days": 90,
    "expiry_warning_days": 14,
}


def get_settings() -> dict:
    return dict(_settings)


def update_setting(key: str, value):
    if key in _settings:
        _settings[key] = value


# ═══════════════════════════════════════════════════════════════════
#  DONORS
# ═══════════════════════════════════════════════════════════════════

def add_donor(donor: Donor):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO donors (name, age, blood_type, phone, gender) VALUES (?, ?, ?, ?, ?)",
        (donor.name, donor.age, donor.blood_type, donor.phone, donor.gender)
    )
    conn.commit()
    conn.close()


def get_all_donors():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, age, blood_type, phone, gender, last_donation FROM donors")
    rows = c.fetchall()
    conn.close()
    return [Donor(id=r[0], name=r[1], age=r[2], blood_type=r[3],
                  phone=r[4], gender=r[5], last_donation=r[6]) for r in rows]


def update_donor(donor: Donor):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE donors SET name=?, age=?, blood_type=?, phone=?, gender=? WHERE id=?",
        (donor.name, donor.age, donor.blood_type, donor.phone, donor.gender, donor.id)
    )
    conn.commit()
    conn.close()


def delete_donor(donor_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM donors WHERE id=?", (donor_id,))
    conn.commit()
    conn.close()


def update_donor_blood_type(donor_id: int, blood_type: str):
    """Update donor's blood type in donors table"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE donors SET blood_type = ? WHERE id = ?", (blood_type, donor_id))
    conn.commit()
    conn.close()


def is_eligible_to_donate(donor_id: int, wait_days: int = None):
    if wait_days is None:
        wait_days = get_settings().get("donation_wait_days", 90)

    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT last_donation, age FROM donors WHERE id=?", (donor_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        return False, "Donor not found."
    
    last_date_str = row[0]
    age = row[1]

    if age < 18:
        return False, "❌ Donor is under 18 years old."
    if age > 65:
        return False, "❌ Donor is over 65 years old."

    if not last_date_str:
        return True, "✅ Eligible to donate (no previous donations)"

    try:
        last = datetime.strptime(last_date_str, "%Y-%m-%d")
        days_since = (datetime.now() - last).days
        if days_since >= wait_days:
            return True, f"✅ Eligible ({days_since} days since last donation)"
        else:
            days_left = wait_days - days_since
            return False, f"❌ Need to wait {days_left} more days"
    except:
        return True, "✅ Eligible to donate"


def get_donor_donation_history(donor_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id, donation_date, units, blood_type
        FROM donations
        WHERE donor_id = ?
        ORDER BY donation_date DESC
    """, (donor_id,))
    rows = c.fetchall()
    conn.close()
    return rows


# ═══════════════════════════════════════════════════════════════════
#  DONATIONS
# ═══════════════════════════════════════════════════════════════════

def add_donation(donation: Donation, max_limit: int = 100):
    conn = get_connection()
    c = conn.cursor()

    eligible, message = is_eligible_to_donate(donation.donor_id)
    if not eligible:
        conn.close()
        return False, message

    if donation.blood_type != "Unknown":
        c.execute("SELECT units FROM stock WHERE blood_type=?", (donation.blood_type,))
        row = c.fetchone()
        if row and row[0] + donation.units > max_limit:
            conn.close()
            return False, f"❌ Stock limit reached for {donation.blood_type}"

    today = datetime.now().strftime("%Y-%m-%d")

    c.execute(
        "INSERT INTO donations (donor_id, blood_type, units, donation_date) VALUES (?, ?, ?, ?)",
        (donation.donor_id, donation.blood_type, donation.units, today)
    )
    c.execute(
        "UPDATE donors SET last_donation=? WHERE id=?",
        (today, donation.donor_id)
    )
    
    # If blood type is not Unknown, update stock and donor blood type
    if donation.blood_type != "Unknown":
        c.execute(
            "UPDATE stock SET units = units + ? WHERE blood_type=?",
            (donation.units, donation.blood_type)
        )
        # Also update donor's blood type if it was Unknown
        c.execute(
            "UPDATE donors SET blood_type = ? WHERE id = ? AND blood_type = 'Unknown'",
            (donation.blood_type, donation.donor_id)
        )
    
    conn.commit()
    conn.close()
    return True, f"✅ Recorded {donation.units} unit(s)"


def get_all_donations():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT donations.id, donors.id, donors.name, donations.blood_type,
               donations.units, donations.donation_date
        FROM donations
        JOIN donors ON donations.donor_id = donors.id
        ORDER BY donations.donation_date DESC
    """)
    rows = c.fetchall()
    conn.close()
    return rows


def get_pending_donations():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT donations.id, donors.name, donors.age, donors.gender, donors.phone,
               donations.units, donations.donation_date, donations.notes
        FROM donations
        JOIN donors ON donations.donor_id = donors.id
        WHERE donations.blood_type = 'Unknown'
          AND (donations.status = 'Pending' OR donations.status IS NULL)
        ORDER BY donations.donation_date DESC
    """)
    rows = c.fetchall()
    conn.close()
    return [
        {
            "id": r[0], "donor_name": r[1], "donor_age": r[2],
            "donor_gender": r[3], "donor_phone": r[4],
            "units": r[5], "donation_date": r[6], "notes": r[7],
        }
        for r in rows
    ]


def update_donation_blood_type(donation_id: int, blood_type: str, notes: str = ""):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT units, donor_id FROM donations WHERE id=?", (donation_id,))
    row = c.fetchone()
    if row:
        units, donor_id = row
        c.execute(
            "UPDATE donations SET blood_type=?, actual_blood_type=?, status='Completed', notes=? WHERE id=?",
            (blood_type, blood_type, notes or "", donation_id)
        )
        c.execute(
            "UPDATE stock SET units = units + ? WHERE blood_type=?",
            (units, blood_type)
        )
        # Update donor's blood type if it was Unknown
        c.execute(
            "UPDATE donors SET blood_type = ? WHERE id = ? AND blood_type = 'Unknown'",
            (blood_type, donor_id)
        )
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════════
#  REQUESTS
# ═══════════════════════════════════════════════════════════════════

def add_request(request: Request):
    conn = get_connection()
    c = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute(
        "INSERT INTO requests (patient_name, blood_type, units, urgency, status, created_date) "
        "VALUES (?, ?, ?, ?, 'Pending', ?)",
        (request.patient_name, request.blood_type, request.units, request.urgency, today)
    )
    conn.commit()
    conn.close()


def get_all_requests():
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT id, patient_name, blood_type, units, urgency, status, created_date "
        "FROM requests ORDER BY id DESC"
    )
    rows = c.fetchall()
    conn.close()
    return [
        Request(id=r[0], patient_name=r[1], blood_type=r[2],
                units=r[3], urgency=r[4], status=r[5], created_date=r[6])
        for r in rows
    ]


def get_pending_requests_unknown():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id, patient_name, blood_type, units, urgency, status, created_date
        FROM requests
        WHERE blood_type = 'Unknown' AND status = 'Pending'
        ORDER BY id DESC
    """)
    rows = c.fetchall()
    conn.close()
    return rows


def update_request_blood_type_and_units(request_id: int, blood_type: str, units: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE requests SET blood_type=?, units=? WHERE id=?",
        (blood_type, units, request_id)
    )
    conn.commit()
    conn.close()


def update_request_status(request_id: int, status: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE requests SET status=? WHERE id=?", (status, request_id))
    conn.commit()
    conn.close()


def delete_request(request_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM requests WHERE id=?", (request_id,))
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════════
#  STOCK
# ═══════════════════════════════════════════════════════════════════

def get_all_stock():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, blood_type, units FROM stock ORDER BY blood_type")
    rows = c.fetchall()
    conn.close()

    class StockItem:
        def __init__(self, id, blood_type, units):
            self.id = id
            self.blood_type = blood_type
            self.units = units

    return [StockItem(r[0], r[1], r[2]) for r in rows]


def get_stock_for_type(blood_type: str) -> int:
    if blood_type == "Unknown":
        return 0
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT units FROM stock WHERE blood_type=?", (blood_type,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0


def update_stock(blood_type: str, delta: int, max_limit: int = None):
    if blood_type == "Unknown":
        return False, "Cannot update stock for Unknown blood type"

    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT units FROM stock WHERE blood_type=?", (blood_type,))
    row = c.fetchone()

    if not row:
        conn.close()
        return False, f"Blood type {blood_type} not found"

    current = row[0]
    new_units = current + delta

    if new_units < 0:
        conn.close()
        return False, f"Not enough stock — only {current} unit(s) available"

    if max_limit is not None and new_units > max_limit:
        conn.close()
        return False, f"Exceeds maximum stock limit of {max_limit} units"

    c.execute("UPDATE stock SET units=? WHERE blood_type=?", (new_units, blood_type))
    conn.commit()
    conn.close()
    return True, f"Stock updated: {new_units} unit(s)"


# ═══════════════════════════════════════════════════════════════════
#  STATS
# ═══════════════════════════════════════════════════════════════════

def get_stats():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM donors")
    total_donors = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM donations")
    total_donations = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM requests WHERE status='Pending'")
    pending_requests = c.fetchone()[0]
    low_threshold = get_settings().get("low_stock_threshold", 5)
    c.execute("SELECT COUNT(*) FROM stock WHERE units < ?", (low_threshold,))
    low_stock = c.fetchone()[0]
    conn.close()
    return {
        "total_donors": total_donors,
        "total_donations": total_donations,
        "pending_requests": pending_requests,
        "low_stock": low_stock,
    }


def get_expiring_blood(days_ahead: int = 14):
    conn = get_connection()
    c = conn.cursor()
    cutoff = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
    c.execute("""
        SELECT blood_type, units, donation_date,
               CAST(julianday(donation_date, '+42 days') - julianday('now') AS INTEGER) AS days_left
        FROM donations
        WHERE donation_date IS NOT NULL
          AND blood_type != 'Unknown'
          AND julianday(donation_date, '+42 days') <= julianday(?)
        ORDER BY days_left ASC
    """, (cutoff,))
    rows = c.fetchall()
    conn.close()
    return [
        {"blood_type": r[0], "units": r[1], "donation_date": r[2], "days_left": r[3]}
        for r in rows
    ]


def get_expiry_stats():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT COUNT(*), COALESCE(SUM(units), 0)
        FROM donations
        WHERE blood_type != 'Unknown'
          AND julianday(donation_date, '+42 days') < julianday('now')
    """)
    row = c.fetchone()
    conn.close()
    return {
        "expired_count": row[0],
        "expired_units": row[1],
        "expiring_soon_units": row[1],
    }