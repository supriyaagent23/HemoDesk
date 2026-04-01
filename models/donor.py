from dataclasses import dataclass

@dataclass
class Donor:
    name: str
    age: int
    blood_type: str
    phone: str
    last_donation: str = ""
    id: int | None = None