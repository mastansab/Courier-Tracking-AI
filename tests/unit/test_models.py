"""
test_models.py - Unit Tests for Data Models.
Identifier: TC-01 / FR-01
Student: MASTAN SAB (Roll No: 60, Class 5B, Case 60)
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.models import Parcel, ParcelHistoryEntry


def test_parcel_to_dict_serialization():
    p = Parcel(
        tracking_id="TRK-60-TEST01",
        sender_name="Alpha Sender",
        recipient_name="Beta Receiver",
        origin="City A",
        destination="City B",
        weight_kg=3.5,
        current_status="Registered",
        current_location="City A Warehouse",
        created_at="2026-11-05 10:00:00",
        updated_at="2026-11-05 10:00:00"
    )
    d = p.to_dict()
    assert d["tracking_id"] == "TRK-60-TEST01"
    assert d["weight_kg"] == 3.5
    assert "history" not in d


def test_parcel_history_entry():
    h = ParcelHistoryEntry(
        id=1,
        tracking_id="TRK-60-TEST01",
        from_status="Registered",
        to_status="Picked Up",
        location="Depot 1",
        notes="Loaded on van",
        timestamp="2026-11-05 12:00:00"
    )
    hd = h.to_dict()
    assert hd["to_status"] == "Picked Up"
    assert hd["id"] == 1
