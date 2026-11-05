"""
test_workflow.py - Unit Tests for Finite State Machine Workflow Transitions.
Identifier: TC-01 / FR-01 / US-01
Student: MASTAN SAB (Roll No: 60, Class 5B, Case 60)
"""

import pytest
import sys
import os

# Ensure backend module can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.workflow import (
    validate_transition,
    predict_delay_risk,
    STATUS_REGISTERED,
    STATUS_PICKED_UP,
    STATUS_IN_TRANSIT,
    STATUS_DELIVERED,
    STATUS_DELAYED,
    STATUS_DELIVERY_FAILED
)


class TestWorkflowTransitions:
    """Test suite for parcel status state transitions (TC-01)."""

    def test_tc01_registered_to_picked_up_valid(self):
        """TC-01.1: Verify valid transition from Registered to Picked Up."""
        valid, msg = validate_transition(STATUS_REGISTERED, STATUS_PICKED_UP)
        assert valid is True
        assert "Valid transition" in msg

    def test_tc01_picked_up_to_in_transit_valid(self):
        """TC-01.2: Verify valid transition from Picked Up to In Transit."""
        valid, msg = validate_transition(STATUS_PICKED_UP, STATUS_IN_TRANSIT)
        assert valid is True

    def test_tc01_in_transit_to_delivered_valid(self):
        """TC-01.3: Verify valid transition from In Transit to Delivered."""
        valid, msg = validate_transition(STATUS_IN_TRANSIT, STATUS_DELIVERED)
        assert valid is True

    def test_tc01_in_transit_to_delayed_exceptional(self):
        """TC-01.4: Verify valid transition from In Transit to Delayed exception state."""
        valid, msg = validate_transition(STATUS_IN_TRANSIT, STATUS_DELAYED)
        assert valid is True

    def test_tc01_delayed_to_in_transit_recovery(self):
        """TC-01.5: Verify recovery transition from Delayed back to In Transit."""
        valid, msg = validate_transition(STATUS_DELAYED, STATUS_IN_TRANSIT)
        assert valid is True

    def test_tc01_in_transit_to_delivery_failed_exceptional(self):
        """TC-01.6: Verify transition to Delivery Failed on unreached recipient."""
        valid, msg = validate_transition(STATUS_IN_TRANSIT, STATUS_DELIVERY_FAILED)
        assert valid is True

    def test_tc01_delivery_failed_to_in_transit_retry(self):
        """TC-01.7: Verify re-attempt transition from Delivery Failed to In Transit."""
        valid, msg = validate_transition(STATUS_DELIVERY_FAILED, STATUS_IN_TRANSIT)
        assert valid is True

    def test_tc01_invalid_direct_jump_registered_to_delivered(self):
        """TC-01.8: Reject illegal skip from Registered directly to Delivered."""
        valid, msg = validate_transition(STATUS_REGISTERED, STATUS_DELIVERED)
        assert valid is False
        assert "Invalid status transition" in msg

    def test_tc01_invalid_terminal_modification(self):
        """TC-01.9: Reject any modification once parcel is Delivered (terminal)."""
        valid, msg = validate_transition(STATUS_DELIVERED, STATUS_IN_TRANSIT)
        assert valid is False
        assert "terminal" in msg.lower()

    def test_tc01_invalid_identical_state_transition(self):
        """TC-01.10: Reject transition to the same state."""
        valid, msg = validate_transition(STATUS_IN_TRANSIT, STATUS_IN_TRANSIT)
        assert valid is False
        assert "already in" in msg


class TestAIDelayPrediction:
    """Test suite for AI Delay Risk calculation (Task B)."""

    def test_delay_prediction_delivered_parcel(self):
        pred = predict_delay_risk(distance_km=500, current_status=STATUS_DELIVERED)
        assert pred["risk_level"] == "LOW"
        assert pred["delay_probability"] <= 10.0

    def test_delay_prediction_delayed_parcel(self):
        pred = predict_delay_risk(distance_km=500, current_status=STATUS_DELAYED)
        assert pred["risk_level"] == "HIGH"
        assert pred["delay_probability"] >= 90.0

    def test_delay_prediction_long_transit(self):
        pred = predict_delay_risk(distance_km=2000, current_status=STATUS_IN_TRANSIT, weather_factor=1.5)
        assert pred["risk_level"] in ["MEDIUM", "HIGH"]
        assert "recommendation" in pred
