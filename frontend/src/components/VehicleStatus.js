import React from "react";
import { Cpu, ShieldAlert, RotateCcw } from "lucide-react";
import { useVehicleContext } from "../context/VehicleContext";
import { getConnectionMeta, getPredictionMeta } from "../utils/vehicleStatus";
import "./Css/VehicleStatus.css";
import "./Css/VehicleShared.css";

export default function VehicleStatus() {
  const { vehicleData, connectionStatus, resetCalibration } = useVehicleContext();

  const prediction = vehicleData?.prediction || {};
  const predictedStatus = prediction.status || "Unknown";
  const confidence = typeof prediction.confidence === "number" ? prediction.confidence : 0;
  const microsleep = prediction.microsleep_detected === true;
  const statusMeta = getPredictionMeta(predictedStatus, connectionStatus, Boolean(vehicleData));
  const connectionMeta = getConnectionMeta(connectionStatus);

  const confidencePct = (confidence * 100).toFixed(1);

  const handleReset = async () => {
    await resetCalibration();
  };

  return (
    <div className="vehicle-status-container">
      <div className="vehicle-status-header">
        <div className="vehicle-status-header-info">
          <div className="vehicle-status-model-icon">
            <Cpu size={16} color="#6366f1" />
            <span className="vehicle-status-model-label">VEHICLE_ML</span>
          </div>
        </div>
        <div className="vehicle-status-header-info">
          <span className={`vehicle-status-chip tone-${connectionMeta.tone}`}>{connectionMeta.label}</span>
          <button className="vehicle-reset-btn" onClick={handleReset} title="Reset vehicle calibration">
            <RotateCcw size={14} />
          </button>
        </div>
      </div>

      <div className={`vehicle-prediction-box ${statusMeta.tone}`}>
        <div className="vehicle-prediction-class-header">
          <span className="vehicle-prediction-class-label">DRIVER STATUS</span>
          <span className="vehicle-prediction-class-value">
            {statusMeta.label}
          </span>
        </div>

        {microsleep && (
          <div className="vehicle-microsleep-alert">
            <p>
              <ShieldAlert size={14} /> Microsleep event detected
            </p>
          </div>
        )}

        <div>
          <div className="vehicle-confidence-header">
            <span className="vehicle-confidence-label">MODEL CONFIDENCE</span>
            <span className="vehicle-confidence-value">{confidencePct}%</span>
          </div>
          <div className="vehicle-confidence-bar">
            <div
              className={`vehicle-confidence-fill ${statusMeta.tone}`}
              style={{ width: `${confidencePct}%` }}
            ></div>
          </div>
        </div>
      </div>

      <div className="vehicle-status-footnote">
        Vision-first inference running with temporal smoothing and hysteresis.
      </div>
    </div>
  );
}
