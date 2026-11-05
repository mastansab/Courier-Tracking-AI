"""
models.py - Domain Models for Courier Tracking.
Identifier: FR-01 / US-01 / TC-01
Student: MASTAN SAB (Roll No: 60, Class 5B, Case 60)
"""

from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any


@dataclass
class ParcelHistoryEntry:
    id: Optional[int]
    tracking_id: str
    from_status: Optional[str]
    to_status: str
    location: str
    notes: Optional[str]
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Parcel:
    tracking_id: str
    sender_name: str
    recipient_name: str
    origin: str
    destination: str
    weight_kg: float
    current_status: str
    current_location: str
    created_at: str
    updated_at: str
    history: Optional[List[Dict[str, Any]]] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if self.history is None:
            data.pop("history", None)
        return data
