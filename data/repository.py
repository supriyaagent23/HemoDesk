from datetime import datetime
from models.donor import Donor
from models.stock import Stock
from models.request import Request
from models.donation import Donation
from data.db import get_connection

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

def today():
    return datetime.now().strftime("%Y-%m-%d")

# ── Donors ─────────────────────────────────────────
def get_all_donors():
    conn = get_connection()
    rows = conn.execute("SELECT id, name, age, blood_type, phone, last_donation FROM donors ORDER BY name").fetchall()
    conn.close()
    return [Donor(id=r[0], name=r[1], age=r[2], blood_type=r[3], phone=r[4], last_donation=r[5]) for r in rows]

def add_donor(d: Donor):
    conn = get_connection()
    conn.execute("INSERT INTO donors (name, age, blood_type, phone, last_donation) VALUES (?,?,?,?,?)",
                 (d.name, d.age, d.blood_type, d.phone, d.last_donation))
    conn.commit()
    conn.close()

def update_donor(d: Donor):
    conn = get_connection()
    conn.execute("UPDATE donors SET name=?, age=?, blood_type=?, phone=? WHERE id=?",
                 (d.name, d.age, d.blood_type, d.phone, d.id))
    conn.commit()
    conn.close()

def delete_donor(donor_id):
    conn = get_connection()
    conn.execute("DELETE FROM donors WHERE id=?", (donor_id,))
    conn.commit()
    conn.close()

def search_donors(query="", blood_type=None):
    conn = get_connection()
    sql = "SELECT id, name, age, blood_type, phone, last_donation FROM donors WHERE 1=1"
    params = []
    if query:
        sql += " AND (LOWER(name) LIKE ? OR phone LIKE ?)"
        v = f"%{query.strip().lower()}%"
        params += [v, v]
    if blood_type and blood_type != "All":
        sql += " AND blood_type=?"
        params.append(blood_type)
    sql += " ORDER BY name"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [Donor(id=r[0], name=r[1], age=r[2], blood_type=r[3], phone=r[4], last_donation=r[5]) for r in rows]

# ── Stock ──────────────────────────────────────────
def get_all_stock():
    conn = get_connection()
    rows = conn.execute("SELECT id, blood_type, units FROM stock ORDER BY blood_type").fetchall()
    conn.close()
    return [Stock(id=r[0], blood_type=r[1], units=r[2]) for r in rows]

def update_stock(blood_type, change):
    conn = get_connection()
    conn.execute("UPDATE stock SET units = MAX(0, units + ?) WHERE blood_type=?", (change, blood_type))
    conn.commit()
    conn.close()

def get_stock_for_type(blood_type):
    conn = get_connection()
    r = conn.execute("SELECT units FROM stock WHERE blood_type=?", (blood_type,)).fetchone()
    conn.close()
    return r[0] if r else 0

# ── Requests ───────────────────────────────────────
def get_all_requests():
    conn = get_connection()
    rows = conn.execute("SELECT id, patient_name, blood_type, units, urgency, status, created_date FROM requests ORDER BY id DESC").fetchall()
    conn.close()
    return [Request(id=r[0], patient_name=r[1], blood_type=r[2], units=r[3],
                    urgency=r[4], status=r[5], created_date=r[6]) for r in rows]

def add_request(r: Request):
    conn = get_connection()
    conn.execute("INSERT INTO requests (patient_name, blood_type, units, urgency, status, created_date) VALUES (?,?,?,?,?,?)",
                 (r.patient_name, r.blood_type, r.units, r.urgency, r.status, now()))
    conn.commit()
    conn.close()

def update_request_status(request_id, status):
    conn = get_connection()
    conn.execute("UPDATE requests SET status=? WHERE id=?", (status, request_id))
    conn.commit()
    conn.close()

def delete_request(request_id):
    conn = get_connection()
    conn.execute("DELETE FROM requests WHERE id=?", (request_id,))
    conn.commit()
    conn.close()

# ── Donations ──────────────────────────────────────
def get_all_donations():
    conn = get_connection()
    rows = conn.execute("""
        SELECT d.id, d.donor_id, dn.name, d.blood_type, d.units, d.donation_date
        FROM donations d JOIN donors dn ON d.donor_id = dn.id
        ORDER BY d.id DESC
    """).fetchall()
    conn.close()
    return rows  # (id, donor_id, donor_name, blood_type, units, date)

def add_donation(d: Donation):
    conn = get_connection()
    conn.execute("INSERT INTO donations (donor_id, blood_type, units, donation_date) VALUES (?,?,?,?)",
                 (d.donor_id, d.blood_type, d.units, today()))
    conn.execute("UPDATE donors SET last_donation=? WHERE id=?", (today(), d.donor_id))
    conn.commit()
    conn.close()
    update_stock(d.blood_type, d.units)

# ── Dashboard stats ────────────────────────────────
def get_stats():
    conn = get_connection()
    total_donors = conn.execute("SELECT COUNT(*) FROM donors").fetchone()[0]
    total_donations = conn.execute("SELECT COUNT(*) FROM donations").fetchone()[0]
    pending_requests = conn.execute("SELECT COUNT(*) FROM requests WHERE status='Pending'").fetchone()[0]
    low_stock = conn.execute("SELECT COUNT(*) FROM stock WHERE units < 5").fetchone()[0]
    conn.close()
    return {
        "total_donors": total_donors,
        "total_donations": total_donations,
        "pending_requests": pending_requests,
        "low_stock": low_stock,
    }