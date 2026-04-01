from dataclasses import dataclass

@dataclass
class Donation:
    donor_id: int
    blood_type: str
    units: int
    donation_date: str = ""
    id: int | None = None