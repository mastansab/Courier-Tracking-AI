"""
test_api.py - Integration Tests for Courier Tracking Flask REST API.
Identifier: TC-01 / FR-01 / US-01
Student: MASTAN SAB (Roll No: 60, Class 5B, Case 60)
"""

import sys
import os
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app import app
from backend.database import init_db


@pytest.fixture
def client():
    app.config["TESTING"] = True
    init_db(seed=True)
    with app.test_client() as client:
        yield client


class TestCourierAPI:
    """Integration test suite for Flask REST API endpoints."""

    def test_health_check(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "UP"
        assert "Courier-Tracking" in data["service"]

    def test_list_parcels(self, client):
        resp = client.get("/api/parcels")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert data["count"] >= 20

    def test_search_parcel_found(self, client):
        resp = client.get("/api/parcels/TRK-60-1006")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert data["data"]["tracking_id"] == "TRK-60-1006"
        assert len(data["data"]["history"]) >= 1

    def test_search_parcel_not_found(self, client):
        resp = client.get("/api/parcels/TRK-INVALID-999")
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["success"] is False
        assert "not found" in data["error"].lower()

    def test_register_parcel_success(self, client):
        payload = {
            "sender_name": "Test Sender Ltd",
            "recipient_name": "Mastan Sab",
            "origin": "Bangalore Central Hub",
            "destination": "Mumbai Hub",
            "weight_kg": 2.5,
            "notes": "Automated integration test parcel"
        }
        resp = client.post("/api/parcels", json=payload)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["success"] is True
        new_id = data["data"]["tracking_id"]
        assert new_id.startswith("TRK-60-")
        assert data["data"]["current_status"] == "Registered"

    def test_register_parcel_validation_error(self, client):
        # Missing required fields
        resp = client.post("/api/parcels", json={"sender_name": "Incomplete"})
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["success"] is False
        assert "Missing" in data["error"]

    def test_update_status_valid_transition(self, client):
        # Register a fresh parcel to guarantee state independence
        reg_resp = client.post("/api/parcels", json={
            "sender_name": "Transition Test Ltd",
            "recipient_name": "Test User",
            "origin": "Hub A",
            "destination": "Hub B",
            "weight_kg": 1.5
        })
        trk_id = reg_resp.get_json()["data"]["tracking_id"]
        # Transition Registered -> Picked Up
        client.put(f"/api/parcels/{trk_id}/status", json={"status": "Picked Up", "location": "Hub A"})
        # Transition Picked Up -> In Transit
        payload = {
            "status": "In Transit",
            "location": "Expressway Toll Plaza",
            "notes": "Departed for destination hub"
        }
        resp = client.put(f"/api/parcels/{trk_id}/status", json=payload)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert data["data"]["current_status"] == "In Transit"

    def test_update_status_invalid_transition_rejected(self, client):
        # Registered parcel TRK-60-1019 attempting illegal jump to Delivered
        payload = {
            "status": "Delivered",
            "location": "Destination Doorstep"
        }
        resp = client.put("/api/parcels/TRK-60-1019/status", json=payload)
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["success"] is False
        assert "Invalid status transition" in data["error"]

    def test_operational_metrics_endpoint(self, client):
        resp = client.get("/api/metrics")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "metrics" in data
        assert "api_response_time" in data["metrics"]
        assert "api_success_rate" in data["metrics"]
        assert "database_availability" in data["metrics"]
