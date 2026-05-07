import sqlite3
from datetime import datetime, timedelta
from data.db import get_connection
from models.donor import Donor
from models.donation import Donation
from models.request import Request

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

def add_donor(donor: Donor):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO donors (name, age, blood_type, phone, passport_no, gender, total_donations) VALUES (?, ?, ?, ?, ?, ?, 0)",
        (donor.name, donor.age, donor.blood_type, donor.phone, donor.passport_no, donor.gender)
    )
    conn.commit()
    conn.close()


def get_all_donors():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, age, blood_type, phone, passport_no, gender, last_donation, total_donations FROM donors")
    rows = c.fetchall()
    conn.close()
    return [Donor(id=r[0], name=r[1], age=r[2], blood_type=r[3],
                  phone=r[4], passport_no=r[5], gender=r[6], 
                  last_donation=r[7], total_donations=r[8] or 0) for r in rows]


def update_donor(donor: Donor):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE donors SET name=?, age=?, blood_type=?, phone=?, passport_no=?, gender=? WHERE id=?",
        (donor.name, donor.age, donor.blood_type, donor.phone, donor.passport_no, donor.gender, donor.id)
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


def add_donation(donation: Donation, max_limit: int = 100):
    conn = get_connection()
    c = conn.cursor()

    try:
        # Check eligibility
        eligible, message = is_eligible_to_donate(donation.donor_id)
        if not eligible:
            return False, message

        today = datetime.now().strftime("%Y-%m-%d")

        # Insert donation
        c.execute(
            "INSERT INTO donations (donor_id, blood_type, units, donation_date) VALUES (?, ?, ?, ?)",
            (donation.donor_id, donation.blood_type, donation.units, today)
        )
        donation_id = c.lastrowid
        
        # Update donor's last donation date and total donations
        c.execute(
            "UPDATE donors SET last_donation=?, total_donations = total_donations + 1 WHERE id=?",
            (today, donation.donor_id)
        )
        
        # Update stock
        c.execute(
            "UPDATE stock SET units = units + ? WHERE blood_type=?",
            (donation.units, donation.blood_type)
        )
        
        conn.commit()
        return True, f"Recorded {donation.units} unit(s)"
        
    except Exception as e:
        return False, f"Error: {str(e)}"
    finally:
        conn.close()


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


def get_pending_lab_donations():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id, name, age, gender, phone, last_donation
        FROM donors
        WHERE blood_type = 'Unknown'
        ORDER BY id DESC
    """)
    rows = c.fetchall()
    conn.close()
    return [
        {
            "id": r[0], "donor_name": r[1], "donor_age": r[2],
            "donor_gender": r[3], "donor_phone": r[4], "donation_date": r[5] or "Never",
            "units": 0, "notes": "",
        }
        for r in rows
    ]



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
        "SELECT id, patient_name, blood_type, units, urgency, status, created_date, fulfilled_date "
        "FROM requests ORDER BY id DESC"
    )
    rows = c.fetchall()
    conn.close()
    return [
        Request(id=r[0], patient_name=r[1], blood_type=r[2],
                units=r[3], urgency=r[4], status=r[5], created_date=r[6], fulfilled_date=r[7] or "")
        for r in rows
    ]


def update_request_status(request_id: int, status: str):
    conn = get_connection()
    c = conn.cursor()
    fulfilled_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if status == "Fulfilled" else None
    c.execute("UPDATE requests SET status=?, fulfilled_date=? WHERE id=?", (status, fulfilled_date, request_id))
    conn.commit()
    conn.close()


def delete_request(request_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM requests WHERE id=?", (request_id,))
    conn.commit()
    conn.close()



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
    
    # Add thank_you_messages count
    try:
        c.execute("SELECT COUNT(*) FROM thank_you_messages")
        thank_you_sent = c.fetchone()[0]
    except:
        thank_you_sent = 0
    
    conn.close()
    return {
        "total_donors": total_donors,
        "total_donations": total_donations,
        "pending_requests": pending_requests,
        "low_stock": low_stock,
        "thank_you_sent": thank_you_sent,
    }