from dataclasses import dataclass

@dataclass
class Stock:
    blood_type: str
    units: int
    id: int | None = None