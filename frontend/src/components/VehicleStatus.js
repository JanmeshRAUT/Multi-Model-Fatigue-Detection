import React from "react";
import { Activity, Cpu, AlertCircle, CheckCircle } from "lucide-react";
import { useVehicleContext } from "../context/VehicleContext";
import "./Css/VehicleStatus.css";

export default function VehicleStatus() {
  const { vehicleData, connectionStatus } = useVehicleContext();

  // Safely extract prediction data with fallbacks
  const prediction = vehicleData?.prediction || {};
  const predictedStatus = prediction.status || "Unknown";
  const confidence = typeof prediction.confidence === "number" ? prediction.confidence : 0;
  const microsleep = prediction.microsleep_detected === true;
  const systemStatus = vehicleData?.status || "Unknown";

  // Determine color and label
  let statusColor = "offline";
  let statusLabel = "OFFLINE";
  let statusIcon = "⚪";

  if (connectionStatus === "offline" || !vehicleData) {
    statusColor = "offline";
    statusLabel = "OFFLINE";
    statusIcon = "⚪";
  } else if (connectionStatus === "connecting" || connectionStatus === "retrying") {
    statusColor = "connecting";
    statusLabel = "CONNECTING";
    statusIcon = "🔄";
  } else if (predictedStatus === "Fatigued") {
    statusColor = "danger";
    statusLabel = "FATIGUED";
    statusIcon = "🚨";
  } else if (predictedStatus === "Drowsy") {
    statusColor = "warning";
    statusLabel = "DROWSY";
    statusIcon = "⚠️";
  } else {
    statusColor = "safe";
    statusLabel = "ALERT";
    statusIcon = "✓";
  }

  const confidencePct = (confidence * 100).toFixed(1);

  return (
    <div className="vehicle-status-container">
      <div className="status-header">
        <div className="status-header-info">
          <div className="status-model-icon">
            <Cpu size={16} color="#6366f1" />
            <span className="status-model-label">VEHICLE_ML</span>
          </div>
        </div>
        <div className="status-header-info">
          <div className="status-indicator">
            <span
              className="status-dot"
              style={{
                background:
                  statusColor === "offline"
                    ? "#94a3b8"
                    : statusColor === "connecting"
                    ? "#3b82f6"
                    : statusColor === "danger"
                    ? "#dc2626"
                    : statusColor === "warning"
                    ? "#f59e0b"
                    : "#16a34a",
                boxShadow:
                  statusColor === "offline"
                    ? "none"
                    : statusColor === "connecting"
                    ? "0 0 8px #3b82f6"
                    : statusColor === "danger"
                    ? "0 0 8px #dc2626"
                    : statusColor === "warning"
                    ? "0 0 8px #f59e0b"
                    : "0 0 8px #16a34a",
              }}
            ></span>
          </div>
        </div>
      </div>

      <div className={`prediction-box ${statusColor}`}>
        <div className="prediction-class-header">
          <span className="prediction-class-label">DRIVER STATUS</span>
          <span className="prediction-class-value">
            <span style={{ marginRight: "8px" }}>{statusIcon}</span>
            {statusLabel}
          </span>
        </div>

        {microsleep && (
          <div
            style={{
              padding: "10px 12px",
              background: "linear-gradient(135deg, #fee2e2 0%, #fecaca 100%)",
              borderLeft: "3px solid #dc2626",
              borderRadius: "6px",
              marginBottom: "12px",
            }}
          >
            <p style={{ margin: 0, fontWeight: 700, color: "#dc2626", fontSize: "0.9rem" }}>
              🚨 MICROSLEEP EVENT DETECTED
            </p>
          </div>
        )}

        <div>
          <div className="confidence-header">
            <span className="confidence-label">MODEL CONFIDENCE</span>
            <span className="confidence-value">{confidencePct}%</span>
          </div>
          <div className="confidence-bar">
            <div
              className={`confidence-fill ${statusColor}`}
              style={{ width: `${confidencePct}%` }}
            ></div>
          </div>
        </div>
      </div>

      <div className="metrics-section">
        <div className="metrics-label">
          <Activity size={12} /> VEHICLE METRICS
        </div>

        <div className="metrics-grid">
          <div className="metric-card">
            <span className="metric-name">PERCLOS</span>
            <span className="metric-value">{((vehicleData?.perclos?.perclos || 0).toFixed(1))}%</span>
            <div className="metric-bar">
              <div
                className="metric-fill"
                style={{
                  width: `${Math.min((vehicleData?.perclos?.perclos || 0), 100)}%`,
                  background:
                    (vehicleData?.perclos?.perclos || 0) > 45
                      ? "#dc2626"
                      : (vehicleData?.perclos?.perclos || 0) > 25
                      ? "#f59e0b"
                      : "#10b981",
                }}
              ></div>
            </div>
          </div>

          <div className="metric-card">
            <span className="metric-name">EAR</span>
            <span className="metric-value">{((vehicleData?.perclos?.ear || 0).toFixed(3))}</span>
            <div className="metric-bar">
              <div
                className="metric-fill"
                style={{
                  width: `${Math.min(((vehicleData?.perclos?.ear || 0) / 0.4) * 100, 100)}%`,
                  background: (vehicleData?.perclos?.ear || 0) > 0.25 ? "#10b981" : "#f59e0b",
                }}
              ></div>
            </div>
          </div>

          <div className="metric-card">
            <span className="metric-name">HEAD X</span>
            <span className="metric-value">{((vehicleData?.head_position?.angle_x || 0).toFixed(1))}°</span>
            <div className="metric-bar">
              <div
                className="metric-fill"
                style={{
                  width: `${Math.min(Math.abs((vehicleData?.head_position?.angle_x || 0) / 40) * 100, 100)}%`,
                  background: "#3b82f6",
                }}
              ></div>
            </div>
          </div>

          <div className="metric-card">
            <span className="metric-name">HEAD Y</span>
            <span className="metric-value">{((vehicleData?.head_position?.angle_y || 0).toFixed(1))}°</span>
            <div className="metric-bar">
              <div
                className="metric-fill"
                style={{
                  width: `${Math.min(Math.abs((vehicleData?.head_position?.angle_y || 0) / 45) * 100, 100)}%`,
                  background: "#8b5cf6",
                }}
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
