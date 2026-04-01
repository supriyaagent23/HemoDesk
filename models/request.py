from dataclasses import dataclass

@dataclass
class Request:
    patient_name: str
    blood_type: str
    units: int
    urgency: str
    status: str = "Pending"
    created_date: str = ""
    id: int | None = None