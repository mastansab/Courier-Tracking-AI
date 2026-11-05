/**
 * app.js - Frontend Controller for Courier Tracking System.
 * Case 60: Courier Tracking | Student: MASTAN SAB (Roll No: 60, Class 5B)
 * Identifier: FR-01 / US-01 / TC-01
 */

const API_BASE = "";
let currentParcelData = null;

// Tab Switching
function switchTab(tabName) {
    document.querySelectorAll(".tab-content").forEach(el => el.classList.remove("active"));
    document.querySelectorAll(".tab-btn").forEach(el => el.classList.remove("active"));

    const targetTab = document.getElementById(`tab-${tabName}`);
    const targetBtn = document.getElementById(`tab-btn-${tabName}`);

    if (targetTab) targetTab.classList.add("active");
    if (targetBtn) targetBtn.classList.add("active");

    if (tabName === "parcels") {
        loadParcelsTable();
    } else if (tabName === "monitoring") {
        loadMetrics();
    }
}

// Alert notifications
function showAlert(message, type = "success") {
    const banner = document.getElementById("alert-banner");
    banner.className = `alert-banner alert-${type}`;
    banner.innerHTML = `<span>${message}</span><button style="background:none;border:none;cursor:pointer;font-size:1.1rem" onclick="hideAlert()">&times;</button>`;
    banner.classList.remove("hidden");
    setTimeout(() => hideAlert(), 6000);
}

function hideAlert() {
    const banner = document.getElementById("alert-banner");
    banner.classList.add("hidden");
}

// Search Parcel
async function searchParcel(trackingIdToSearch = null) {
    const input = document.getElementById("search-input");
    const trkId = (trackingIdToSearch || input.value).trim().toUpperCase();

    if (!trkId) {
        showAlert("Please enter a Tracking ID to search.", "danger");
        return;
    }

    try {
        const resp = await fetch(`/api/parcels/${encodeURIComponent(trkId)}`);
        const result = await resp.json();

        if (!resp.ok || !result.success) {
            showAlert(result.error || `Parcel '${trkId}' not found.`, "danger");
            document.getElementById("parcel-result").classList.add("hidden");
            return;
        }

        currentParcelData = result.data;
        renderParcel(currentParcelData);
        showAlert(`Tracking details loaded for ${trkId}.`, "success");
    } catch (err) {
        showAlert(`Network or server error: ${err.message}`, "danger");
    }
}

// Render Parcel Details
function renderParcel(parcel) {
    document.getElementById("parcel-result").classList.remove("hidden");
    document.getElementById("display-tracking-id").textContent = parcel.tracking_id;
    document.getElementById("display-recipient").textContent = parcel.recipient_name;
    document.getElementById("display-sender").textContent = parcel.sender_name;
    document.getElementById("display-weight").textContent = `${parcel.weight_kg} kg`;
    document.getElementById("display-origin").textContent = parcel.origin;
    document.getElementById("display-destination").textContent = parcel.destination;
    document.getElementById("display-location").textContent = parcel.current_location;
    document.getElementById("display-created").textContent = parcel.created_at;
    document.getElementById("display-updated").textContent = parcel.updated_at;

    // Status Badge
    const badge = document.getElementById("display-status-badge");
    badge.textContent = parcel.current_status;
    badge.className = `status-badge ${getStatusBadgeClass(parcel.current_status)}`;

    // AI Delay Risk (Task B)
    renderDelayRisk(parcel.delay_prediction);

    // Stepper progression
    renderStepper(parcel.current_status);

    // Timeline History
    renderTimeline(parcel.history || []);

    // Set default location in update box
    document.getElementById("update-location-input").value = parcel.current_location;
}

function getStatusBadgeClass(status) {
    switch (status) {
        case "Registered": return "status-registered";
        case "Picked Up": return "status-picked-up";
        case "In Transit": return "status-in-transit";
        case "Delivered": return "status-delivered";
        case "Delayed": return "status-delayed";
        case "Delivery Failed": return "status-delivery-failed";
        default: return "";
    }
}

// AI Delay Risk Widget (Task B)
function renderDelayRisk(prediction) {
    if (!prediction) return;
    const pill = document.getElementById("display-risk-level");
    const desc = document.getElementById("display-prediction-desc");

    pill.textContent = `${prediction.risk_level} RISK (${prediction.delay_probability}%)`;
    pill.className = `risk-pill risk-${prediction.risk_level.toLowerCase()}`;
    desc.innerHTML = `Delay Probability: <strong>${prediction.delay_probability}%</strong> &bull; Recommendation: <em>${prediction.recommendation}</em>`;
}

// Stepper
function renderStepper(status) {
    const states = ["Registered", "Picked Up", "In Transit", "Delivered"];
    const idx = states.indexOf(status);

    // Nodes
    const n1 = document.getElementById("step-node-registered");
    const n2 = document.getElementById("step-node-pickedup");
    const n3 = document.getElementById("step-node-intransit");
    const n4 = document.getElementById("step-node-delivered");
    const nodes = [n1, n2, n3, n4];

    // Connectors
    const c1 = document.getElementById("conn-1");
    const c2 = document.getElementById("conn-2");
    const c3 = document.getElementById("conn-3");
    const conns = [c1, c2, c3];

    nodes.forEach(n => { n.className = "step-node"; });
    conns.forEach(c => { c.className = "step-connector"; });

    const excBanner = document.getElementById("exception-banner");
    excBanner.className = "exception-badge hidden";

    if (status === "Delayed") {
        excBanner.textContent = "⚠️ Exception Alert: Parcel is currently DELAYED. Routing team alerted.";
        excBanner.className = "exception-badge exception-delayed";
        // Show up to In Transit completed
        n1.className = "step-node completed";
        n2.className = "step-node completed";
        n3.className = "step-node active";
        c1.className = "step-connector completed";
        c2.className = "step-connector completed";
        return;
    }

    if (status === "Delivery Failed") {
        excBanner.textContent = "❌ Exception Alert: Delivery Attempt FAILED. Awaiting customer contact & re-dispatch.";
        excBanner.className = "exception-badge exception-failed";
        n1.className = "step-node completed";
        n2.className = "step-node completed";
        n3.className = "step-node active";
        c1.className = "step-connector completed";
        c2.className = "step-connector completed";
        return;
    }

    if (idx >= 0) {
        for (let i = 0; i <= idx; i++) {
            if (i === idx) {
                nodes[i].className = (status === "Delivered") ? "step-node completed" : "step-node active";
            } else {
                nodes[i].className = "step-node completed";
            }
            if (i < idx && conns[i]) {
                conns[i].className = "step-connector completed";
            }
        }
    }
}

// Timeline Audit Trail
function renderTimeline(historyList) {
    const container = document.getElementById("timeline-list");
    container.innerHTML = "";

    if (!historyList || historyList.length === 0) {
        container.innerHTML = "<p style='color:#64748b;font-size:0.85rem'>No history recorded yet.</p>";
        return;
    }

    historyList.forEach(entry => {
        const item = document.createElement("div");
        item.className = "timeline-item";
        item.innerHTML = `
            <div class="timeline-dot"></div>
            <div class="timeline-time">${entry.timestamp}</div>
            <div class="timeline-title">${entry.from_status ? entry.from_status + " &rarr; " : ""}${entry.to_status} &bull; ${entry.location}</div>
            <div class="timeline-notes">${entry.notes ? entry.notes : "Workflow state logged"}</div>
        `;
        container.appendChild(item);
    });
}

// Update Parcel Status
async function updateParcelStatus() {
    if (!currentParcelData) {
        showAlert("No parcel selected for status update.", "danger");
        return;
    }

    const newStatus = document.getElementById("update-status-select").value;
    const location = document.getElementById("update-location-input").value.trim();
    const notes = document.getElementById("update-notes-input").value.trim();

    if (!newStatus) {
        showAlert("Please select a target status.", "danger");
        return;
    }

    try {
        const resp = await fetch(`/api/parcels/${currentParcelData.tracking_id}/status`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status: newStatus, location: location, notes: notes })
        });
        const result = await resp.json();

        if (!resp.ok || !result.success) {
            showAlert(`Transition Error: ${result.error}`, "danger");
            return;
        }

        showAlert(`Status successfully updated to '${newStatus}'!`, "success");
        // Re-fetch parcel details
        searchParcel(currentParcelData.tracking_id);
    } catch (err) {
        showAlert(`Error: ${err.message}`, "danger");
    }
}

// Register Parcel
async function handleRegisterParcel(e) {
    e.preventDefault();
    const payload = {
        sender_name: document.getElementById("reg-sender").value.trim(),
        recipient_name: document.getElementById("reg-recipient").value.trim(),
        origin: document.getElementById("reg-origin").value.trim(),
        destination: document.getElementById("reg-destination").value.trim(),
        weight_kg: parseFloat(document.getElementById("reg-weight").value),
        notes: document.getElementById("reg-notes").value.trim()
    };

    try {
        const resp = await fetch("/api/parcels", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const result = await resp.json();

        if (!resp.ok || !result.success) {
            showAlert(`Registration Failed: ${result.error}`, "danger");
            return;
        }

        const newId = result.data.tracking_id;
        showAlert(`Parcel successfully registered! Tracking ID: ${newId}`, "success");
        document.getElementById("parcel-form").reset();

        // Switch to tracking view and show newly created parcel
        switchTab("tracking");
        document.getElementById("search-input").value = newId;
        searchParcel(newId);
    } catch (err) {
        showAlert(`Network Error: ${err.message}`, "danger");
    }
}

// Load Random Parcel for quick demo
function loadRandomParcel() {
    const sampleIds = [
        "TRK-60-1006", "TRK-60-1011", "TRK-60-1016",
        "TRK-60-1018", "TRK-60-1001", "TRK-60-1020"
    ];
    const picked = sampleIds[Math.floor(Math.random() * sampleIds.length)];
    document.getElementById("search-input").value = picked;
    searchParcel(picked);
}

// Load Parcel Directory Table
async function loadParcelsTable() {
    const status = document.getElementById("filter-status").value;
    const url = status ? `/api/parcels?status=${encodeURIComponent(status)}` : "/api/parcels";

    try {
        const resp = await fetch(url);
        const result = await resp.json();
        const tbody = document.getElementById("parcels-table-body");
        tbody.innerHTML = "";

        if (!result.data || result.data.length === 0) {
            tbody.innerHTML = "<tr><td colspan='7' style='text-align:center'>No parcels found.</td></tr>";
            return;
        }

        result.data.forEach(p => {
            const tr = document.createElement("tr");
            tr.onclick = () => {
                switchTab("tracking");
                document.getElementById("search-input").value = p.tracking_id;
                searchParcel(p.tracking_id);
            };
            tr.innerHTML = `
                <td><code>${p.tracking_id}</code></td>
                <td><strong>${p.recipient_name}</strong></td>
                <td>${p.origin} &rarr; ${p.destination}</td>
                <td>${p.weight_kg} kg</td>
                <td><span class="status-badge ${getStatusBadgeClass(p.current_status)}">${p.current_status}</span></td>
                <td>${p.current_location}</td>
                <td><button class="btn btn-outline" style="padding:0.25rem 0.6rem;font-size:0.75rem">Track</button></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error("Failed to load table:", err);
    }
}

// Load Operational Monitoring Metrics (L4.5)
async function loadMetrics() {
    try {
        const resp = await fetch("/api/metrics");
        const data = await resp.json();
        const m = data.metrics;

        // Metric 1: Response Time
        document.getElementById("m-resp-time").textContent = m.api_response_time.value;
        setMetricStatus("m-resp-status", m.api_response_time.status);
        document.getElementById("tbl-m1").textContent = `${m.api_response_time.value} ms`;

        // Metric 2: Success Rate
        document.getElementById("m-success-rate").textContent = m.api_success_rate.value;
        setMetricStatus("m-success-status", m.api_success_rate.status);
        document.getElementById("tbl-m2").textContent = `${m.api_success_rate.value} %`;

        // Metric 3: Error Rate
        document.getElementById("m-error-rate").textContent = m.error_rate.value;
        setMetricStatus("m-error-status", m.error_rate.status);
        document.getElementById("tbl-m3").textContent = `${m.error_rate.value} %`;

        // Metric 4: DB Availability
        document.getElementById("m-db-avail").textContent = m.database_availability.value;
        document.getElementById("m-db-latency").textContent = m.database_availability.latency_ms;
        setMetricStatus("m-db-status", m.database_availability.status);
        document.getElementById("tbl-m4").textContent = `${m.database_availability.value} % (${m.database_availability.db_state})`;

        // Metric 5: Failed Parcel Updates
        document.getElementById("m-failed-updates").textContent = m.failed_parcel_updates.value;
        setMetricStatus("m-failed-status", m.failed_parcel_updates.status);
        document.getElementById("tbl-m5").textContent = `${m.failed_parcel_updates.value} events`;

        // Metric 6: Processing Delay
        document.getElementById("m-processing-delay").textContent = m.status_update_processing_delay.value;
        setMetricStatus("m-delay-status", m.status_update_processing_delay.status);
        document.getElementById("tbl-m6").textContent = `${m.status_update_processing_delay.value} ms`;

    } catch (err) {
        console.error("Failed to load metrics:", err);
    }
}

function setMetricStatus(elemId, status) {
    const el = document.getElementById(elemId);
    el.textContent = status;
    el.className = `metric-status status-${status.toLowerCase()}`;
}

// Auto-load default parcel on page load
window.addEventListener("DOMContentLoaded", () => {
    searchParcel("TRK-60-1006");
});
