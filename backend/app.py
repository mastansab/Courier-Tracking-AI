"""
app.py - Main Flask REST API Server for Courier Tracking Prototype.
Identifier: FR-01 / US-01 / TC-01
Student: MASTAN SAB (Roll No: 60, Class 5B, Case 60)
Scenario: 30,000 parcels daily courier tracking workflow.
"""

import os
import time
import random
import string
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from backend.database import get_db_connection, init_db
from backend.workflow import (
    validate_transition,
    predict_delay_risk,
    ALL_STATUSES,
    STATUS_REGISTERED
)
from backend.monitoring import log_request_metric, get_current_metrics

app = Flask(__name__, static_folder="../frontend")

# Ensure database tables exist on startup
init_db(seed=True)


@app.before_request
def start_timer():
    request._start_time = time.time()


@app.after_request
def record_metrics(response):
    if hasattr(request, "_start_time"):
        duration_ms = (time.time() - request._start_time) * 1000.0
        is_update_fail = False
        if request.endpoint == "update_parcel_status" and response.status_code >= 400:
            is_update_fail = True
        log_request_metric(request.path, duration_ms, response.status_code, is_update_fail)
    return response


def generate_tracking_id() -> str:
    """Generates unique tracking ID formatted as TRK-60-XXXXXX."""
    chars = string.ascii_uppercase + string.digits
    suffix = "".join(random.choices(chars, k=6))
    return f"TRK-60-{suffix}"


# Frontend Static File Routes
@app.route("/")
def serve_frontend():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)


# REST API Endpoints
@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint for Docker / Jenkins / Monitoring."""
    return jsonify({
        "status": "UP",
        "service": "Courier-Tracking-API",
        "version": "1.0.0",
        "case": "Case 60 - Courier Tracking",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route("/api/parcels", methods=["POST"])
def register_parcel():
    """
    Feature 1 & 2: Register a new parcel with unique tracking ID.
    Identifier: FR-01 / US-01
    """
    data = request.get_json() or {}
    required_fields = ["sender_name", "recipient_name", "origin", "destination", "weight_kg"]
    missing = [f for f in required_fields if f not in data or not str(data[f]).strip()]
    if missing:
        return jsonify({
            "success": False,
            "error": f"Missing required fields: {', '.join(missing)}"
        }), 400

    try:
        weight = float(data["weight_kg"])
        if weight <= 0:
            return jsonify({"success": False, "error": "Weight must be greater than zero."}), 400
    except ValueError:
        return jsonify({"success": False, "error": "Invalid weight value."}), 400

    tracking_id = generate_tracking_id()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = STATUS_REGISTERED
    location = data.get("current_location") or data["origin"]

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO parcels (tracking_id, sender_name, recipient_name, origin, destination,
                            weight_kg, current_status, current_location, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        tracking_id,
        data["sender_name"].strip(),
        data["recipient_name"].strip(),
        data["origin"].strip(),
        data["destination"].strip(),
        weight,
        status,
        location,
        now_str,
        now_str
    ))

    cursor.execute("""
        INSERT INTO parcel_history (tracking_id, from_status, to_status, location, notes, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        tracking_id,
        None,
        status,
        location,
        data.get("notes") or "Shipment registered into tracking system",
        now_str
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Parcel registered successfully.",
        "data": {
            "tracking_id": tracking_id,
            "sender_name": data["sender_name"],
            "recipient_name": data["recipient_name"],
            "origin": data["origin"],
            "destination": data["destination"],
            "weight_kg": weight,
            "current_status": status,
            "current_location": location,
            "created_at": now_str
        }
    }), 201


@app.route("/api/parcels", methods=["GET"])
def list_parcels():
    """Lists parcels with optional search query by tracking ID, recipient, or status."""
    query = request.args.get("q", "").strip().lower()
    status_filter = request.args.get("status", "").strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    sql = "SELECT * FROM parcels WHERE 1=1"
    params = []

    if query:
        sql += " AND (LOWER(tracking_id) LIKE ? OR LOWER(recipient_name) LIKE ? OR LOWER(destination) LIKE ?)"
        wildcard = f"%{query}%"
        params.extend([wildcard, wildcard, wildcard])

    if status_filter and status_filter in ALL_STATUSES:
        sql += " AND current_status = ?"
        params.append(status_filter)

    sql += " ORDER BY updated_at DESC"
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()

    parcels = [dict(row) for row in rows]
    return jsonify({
        "success": True,
        "count": len(parcels),
        "data": parcels
    }), 200


@app.route("/api/parcels/<tracking_id>", methods=["GET"])
def get_parcel(tracking_id):
    """
    Feature 3, 4, 6, 7 & 9: Search for parcel by tracking ID.
    Returns parcel details, full history, and AI delay prediction.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM parcels WHERE tracking_id = ?", (tracking_id.strip(),))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify({
            "success": False,
            "error": f"Parcel with tracking ID '{tracking_id}' not found. Please verify the ID."
        }), 404

    parcel = dict(row)

    # Fetch audit history
    cursor.execute("""
        SELECT id, from_status, to_status, location, notes, timestamp
        FROM parcel_history
        WHERE tracking_id = ?
        ORDER BY id ASC
    """, (tracking_id.strip(),))
    history_rows = cursor.fetchall()
    conn.close()

    parcel["history"] = [dict(h) for h in history_rows]

    # AI delay prediction integration (Task B)
    delay_prediction = predict_delay_risk(
        distance_km=float(parcel.get("weight_kg", 2.0)) * 250.0,
        current_status=parcel["current_status"]
    )
    parcel["delay_prediction"] = delay_prediction

    return jsonify({
        "success": True,
        "data": parcel
    }), 200


@app.route("/api/parcels/<tracking_id>/status", methods=["PUT"])
def update_parcel_status(tracking_id):
    """
    Feature 5, 8 & 10: Update parcel status with strict FSM transition validation.
    Identifier: FR-01 / TC-01
    """
    data = request.get_json() or {}
    new_status = data.get("status")
    location = data.get("location")
    notes = data.get("notes") or ""

    if not new_status:
        return jsonify({"success": False, "error": "New status is required."}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM parcels WHERE tracking_id = ?", (tracking_id.strip(),))
    parcel = cursor.fetchone()

    if not parcel:
        conn.close()
        return jsonify({
            "success": False,
            "error": f"Parcel with tracking ID '{tracking_id}' not found."
        }), 404

    current_status = parcel["current_status"]

    # Validate transition using FSM business logic
    is_valid, err_msg = validate_transition(current_status, new_status)
    if not is_valid:
        conn.close()
        return jsonify({
            "success": False,
            "error": err_msg,
            "current_status": current_status,
            "attempted_status": new_status
        }), 400

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    update_location = location.strip() if location else parcel["current_location"]

    cursor.execute("""
        UPDATE parcels
        SET current_status = ?, current_location = ?, updated_at = ?
        WHERE tracking_id = ?
    """, (new_status, update_location, now_str, tracking_id.strip()))

    cursor.execute("""
        INSERT INTO parcel_history (tracking_id, from_status, to_status, location, notes, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (tracking_id.strip(), current_status, new_status, update_location, notes, now_str))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": f"Status updated from '{current_status}' to '{new_status}'.",
        "data": {
            "tracking_id": tracking_id,
            "previous_status": current_status,
            "current_status": new_status,
            "location": update_location,
            "updated_at": now_str
        }
    }), 200


@app.route("/api/metrics", methods=["GET"])
def get_metrics():
    """
    Feature L4.5: Operational monitoring metrics.
    Returns the 6 required metrics, thresholds, and alert states.
    """
    return jsonify(get_current_metrics()), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Courier Tracking Server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
