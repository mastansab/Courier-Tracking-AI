"""
workflow.py - Business Logic and State Transition Engine for Courier Tracking.
Identifier: FR-01 / US-01 / TC-01
Student: MASTAN SAB (Roll No: 60, Class 5B, Case 60)
"""

from typing import Tuple, List, Dict, Any

# Valid workflow statuses
STATUS_REGISTERED = "Registered"
STATUS_PICKED_UP = "Picked Up"
STATUS_IN_TRANSIT = "In Transit"
STATUS_DELIVERED = "Delivered"
STATUS_DELAYED = "Delayed"
STATUS_DELIVERY_FAILED = "Delivery Failed"

ALL_STATUSES = [
    STATUS_REGISTERED,
    STATUS_PICKED_UP,
    STATUS_IN_TRANSIT,
    STATUS_DELIVERED,
    STATUS_DELAYED,
    STATUS_DELIVERY_FAILED
]

# Strict Finite State Machine (FSM) Transition Rules
ALLOWED_TRANSITIONS: Dict[str, List[str]] = {
    STATUS_REGISTERED: [STATUS_PICKED_UP],
    STATUS_PICKED_UP: [STATUS_IN_TRANSIT, STATUS_DELAYED, STATUS_DELIVERY_FAILED],
    STATUS_IN_TRANSIT: [STATUS_DELIVERED, STATUS_DELAYED, STATUS_DELIVERY_FAILED],
    STATUS_DELAYED: [STATUS_IN_TRANSIT, STATUS_DELIVERY_FAILED],
    STATUS_DELIVERY_FAILED: [STATUS_IN_TRANSIT],  # Re-attempt delivery
    STATUS_DELIVERED: []  # Terminal state
}


def validate_transition(current_status: str, new_status: str) -> Tuple[bool, str]:
    """
    Validates whether transition from current_status to new_status is permitted.
    Returns (is_valid, error_message).
    """
    if current_status not in ALLOWED_TRANSITIONS:
        return False, f"Invalid current status: '{current_status}'"

    if new_status not in ALL_STATUSES:
        return False, f"Invalid target status: '{new_status}'"

    if current_status == STATUS_DELIVERED:
        return False, "Parcel has already been Delivered. Status is terminal and cannot be changed."

    if current_status == new_status:
        return False, f"Parcel is already in '{current_status}' state."

    allowed = ALLOWED_TRANSITIONS.get(current_status, [])
    if new_status in allowed:
        return True, "Valid transition."
    else:
        return False, (
            f"Invalid status transition from '{current_status}' to '{new_status}'. "
            f"Allowed next states: {', '.join(allowed) if allowed else 'None (Terminal)'}"
        )


def predict_delay_risk(distance_km: float, current_status: str, weather_factor: float = 1.0) -> Dict[str, Any]:
    """
    AI-Assisted Delay Prediction heuristic for Kanban board (Case 60 Task B).
    Estimates probability of delay based on transit parameters.
    """
    if current_status in [STATUS_DELIVERED, STATUS_REGISTERED]:
        risk_score = 0.05
    elif current_status == STATUS_DELAYED:
        risk_score = 0.95
    else:
        # Distance baseline + weather multiplier
        base = min(distance_km / 1500.0, 0.6)
        risk_score = min(max(base * weather_factor, 0.05), 0.90)

    category = "LOW"
    if risk_score > 0.60:
        category = "HIGH"
    elif risk_score > 0.30:
        category = "MEDIUM"

    return {
        "delay_probability": round(risk_score * 100, 1),
        "risk_level": category,
        "recommendation": "Priority dispatch via express route" if category == "HIGH" else "Standard workflow"
    }
