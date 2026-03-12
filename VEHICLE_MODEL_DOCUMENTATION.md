# Vehicle Fatigue Detection Model 🚗

## Overview

The **Vehicle Model** is a lightweight, **vision-only fatigue detection system** specifically designed for real-world vehicle driver monitoring. Unlike the standard model which uses multiple psychological sensors (HR, Temperature, IMU), the Vehicle Model focuses exclusively on **head position, eye detection (PERCLOS), and yawning** analysis through camera input.

### Key Features

✅ **Vision-Only Processing** - No health sensors required  
✅ **Fast & Lightweight** - Optimized for real-time vehicle monitoring  
✅ **Head Position Tracking** - Detects head pose changes (up, down, left, right)  
✅ **Eye Closure Detection (PERCLOS)** - Measures eye closure percentage  
✅ **Yawning Detection** - Monitors mouth aspect ratio (MAR) for yawning  
✅ **Microsleep Detection** - Triggers alerts for critical drowsiness events  

---

## Architecture

### Component Stack

```
Frontend (React)
    ↓
VehicleContext (State Management)
    ↓
Vehicle API Endpoints (/api/vehicle/*)
    ↓
Backend (Flask)
    ↓
VehicleMLEngine (Vision-Only ML)
    ↓
Vision Processing (Head Pose + PERCLOS + Yawning)
```

---

## Backend Implementation

### Files Created/Modified

#### 1. **`backend_flask/ml/vehicle_ml_engine.py`** (NEW)
Vision-only ML engine without psychological sensors.

**Key Classes:**
- `VehicleMLEngine`: Main prediction engine

**Key Methods:**
- `predict(vision_data)`: Single prediction from vision input
- `calculate_temporal_features(current_data)`: Rolling statistics for smoothing
- `reset_calibration()`: Personalize EAR baseline for user

**Input Structure:**
```python
vision_data = {
    'ear': float,           # Eye Aspect Ratio (0.0-1.0)
    'mar': float,           # Mouth Aspect Ratio (0.0-0.5)
    'pitch': float,         # Head angle X (-90 to 90)
    'yaw': float,           # Head angle Y (-90 to 90)
    'roll': float,          # Head angle Z (-90 to 90)
    'perclos': float,       # Percentage of eye closure (0.0-1.0)
    'status': str           # "OK", "No Face", "Unstable"
}
```

**Output Structure:**
```python
{
    'status': "Alert|Drowsy|Fatigued",
    'confidence': float,                    # 0.0-1.0
    'raw_probs': [p_alert, p_drowsy, p_fatigued],
    'microsleep_detected': bool
}
```

#### 2. **`backend_flask/app.py`** (MODIFIED)
Added vehicle model routes and endpoints.

**New Global Variables:**
```python
vehicle_ml_engine      # VehicleMLEngine instance
vehicle_ml_lock        # Thread lock for vehicle model
last_vehicle_ml_time   # Timing for ML predictions
cached_vehicle_prediction  # Cached results
```

**New Functions:**
- `get_vehicle_combined_data_internal()`: Aggregates vision data for vehicle model
- `vehicle_websocket_endpoint()`: WebSocket endpoint for camera frames
- `get_vehicle_combined_data()`: REST endpoint for vehicle data

**New Routes:**
```
POST   /api/vehicle/reset_calibration     → Reset calibration
GET    /api/vehicle/combined_data         → Get vehicle data
WS     /ws/vehicle/detect                 → WebSocket for camera frames
```

#### 3. **`backend_flask/config.py`** (MODIFIED)
Added vehicle model path configuration.

```python
VEHICLE_MODEL_PATH = os.path.join(os.path.dirname(__file__), "ml", "models", "vehicle_fatigue_model.pkl")
```

---

## Frontend Implementation

### Files Created/Modified

#### 1. **`frontend/src/context/VehicleContext.js`** (NEW)
Global state management for vehicle model data.

**Exported Functions:**
- `useVehicleContext()`: Hook to access vehicle context
- `VehicleProvider`: Context provider component

**State Management:**
- `vehicleData`: Current vision & prediction data
- `headPositionHistory`: Array of head position samples
- `predictionHistory`: Array of prediction history

#### 2. **`frontend/src/components/VehicleDashboard.js`** (NEW)
Main vehicle dashboard component.

**Features:**
- Live camera feed
- Vision metrics (PERCLOS, EAR, MAR)
- Head position tracking (pitch, yaw, roll)
- Fatigue status indicator
- Head position trend chart
- Drowsiness indicators
- Calibration reset button

**WebSocket Connection:**
- Connects to `/ws/vehicle/detect`
- Sends camera frames at ~30 FPS
- Receives predictions at ~2 Hz

#### 3. **`frontend/src/hooks/useVehicleData.js`** (NEW)
Convenience hook for accessing vehicle data in components.

**Returns:**
```javascript
{
    vehicleData,
    perclos,
    headPosition,
    prediction,
    status,
    confidence,
    microsleepDetected,
    headPositionHistory,
    predictionHistory,
    isFatigued,
    isDrowsy,
    isAlert,
    isInitializing,
    isOffline
}
```

#### 4. **`frontend/src/api.js`** (MODIFIED)
Added vehicle model API endpoints.

**New Functions:**
- `getVehicleCombinedData()`: Fetch vehicle data via REST
- `resetVehicleCalibration()`: Reset vehicle model calibration

#### 5. **`frontend/src/App.js`** (MODIFIED)
Added model switcher for selecting between standard and vehicle models.

**New Components:**
- `ModelSwitcher`: Toggle button between models
- `StandardModelWithSwitcher`: Wrapper for standard model
- `VehicleModelWithSwitcher`: Wrapper for vehicle model

---

## Vision Processing

### Shared Components (Used by Both Models)

The vehicle model reuses the standard vision processing pipeline:

#### **Head Pose Estimation** (`cv/head_pose.py`)
- MediaPipe FaceMesh with 468 face landmarks
- PnP (Perspective n-Point) algorithm for 3D pose
- Fallback to IMU when vision fails

#### **PERCLOS Detection** (`cv/perclos.py`)
- Eye Aspect Ratio (EAR) calculation
- Mouth Aspect Ratio (MAR) for yawning
- Personal calibration for EAR baseline
- PERCLOS = fraction of frames with eyes closed

---

## Data Flow

### Standard Model Pipeline
```
Camera Frame
    ↓
[MediaPipe FaceMesh] → Head Pose + EAR + MAR
    ↓
[Sensor] → HR + Temperature + IMU
    ↓
[MLEngine.predict(sensor_data, vision_data)]
    ↓
Prediction: Alert|Drowsy|Fatigued
```

### Vehicle Model Pipeline
```
Camera Frame
    ↓
[MediaPipe FaceMesh] → Head Pose + EAR + MAR + PERCLOS
    ↓
[VehicleMLEngine.predict(vision_data)]
    ↓
Prediction: Alert|Drowsy|Fatigued + Microsleep Detection
```

---

## Usage

### Switching Models

Users can toggle between models using the **Model Switcher** button in the top-right corner:

- **🧠 Standard Model** - Full fatigue detection with health sensors
- **🚗 Vehicle Model** - Vision-only detection for vehicles

### API Endpoints

#### Get Vehicle Data (REST)
```bash
curl http://localhost:5000/api/vehicle/combined_data
```

#### Reset Vehicle Calibration
```bash
curl -X POST http://localhost:5000/api/vehicle/reset_calibration
```

#### WebSocket Connection
```javascript
ws = new WebSocket('ws://localhost:5000/ws/vehicle/detect');
ws.send(JSON.stringify({ image_data: base64_encoded_frame }));
```

---

## Configuration

### Model Paths
```python
# backend_flask/config.py
VEHICLE_MODEL_PATH = "backend_flask/ml/models/vehicle_fatigue_model.pkl"
```

### ML Interval
```python
ML_INTERVAL = 0.5  # Predictions every 500ms (2 Hz)
```

### Feature Window
```python
window_size = 20  # Temporal smoothing over 20 frames
```

---

## Performance

| Metric | Value |
|--------|-------|
| **Input Frame Rate** | ~30 FPS (camera) |
| **Prediction Frequency** | ~2 Hz (500ms interval) |
| **Feature Latency** | ~10-20ms (head pose + PERCLOS) |
| **ML Inference Time** | ~5-10ms |
| **Total Latency** | ~50-100ms |
| **Model Size** | ~TBD (scikit-learn Random Forest) |
| **Vision-Only Processing** | ✅ No network sensors needed |

---

## Features Tracked

### Vision Features (Vehicle Model)

| Feature | Range | Purpose |
|---------|-------|---------|
| **EAR** (Eye Aspect Ratio) | 0.0 - 1.0 | Primary drowsiness indicator |
| **MAR** (Mouth Aspect Ratio) | 0.0 - 0.5 | Yawning detection |
| **Head Pitch** | -90° to 90° | Forward/backward head tilt |
| **Head Yaw** | -90° to 90° | Left/right head turn |
| **Head Roll** | -90° to 90° | Head rotation |
| **PERCLOS** | 0.0 - 1.0 | Percentage of eye closure |

### Removed Features (VS Standard Model)

❌ Heart Rate (HR)  
❌ Body Temperature  
❌ IMU Accelerometer Data  

---

## Safety & Thresholds

### Microsleep Detection
- **Triggered By:**
  - PERCLOS > 80% (sustained eye closure)
  - EAR < 0.15 (very low eye opening)
- **Action:** Force "Fatigued" state and alert

### PERCLOS Override
- **Threshold:** > 55%
- **Action:** Override model prediction, force "Fatigued" state

### State Persistence
- **Required Persistence:** 5 frames
- **Effect:** Prevents jittery state changes, requires sustained signal

---

## Calibration

### Personalization
The vehicle model adapts to each user:

1. **Initial 100 Frames** - Learn personally normal EAR
2. **Base EAR Calculation** - Average EAR during open-eye frames
3. **Feature Normalization** - All EAR values normalized against personal baseline
4. **Dynamic Adjustment** - Baseline can be reset via `/api/vehicle/reset_calibration`

### Calibration Button
- Located in Vehicle Dashboard
- Resets all personalization baselines
- Good practice: Perform before starting monitoring

---

## Future Enhancements

📌 **Possible Extensions:**
- [ ] Multi-face detection (co-passengers)
- [ ] Driver distraction detection (eye gaze)
- [ ] Hands-on-wheel validation
- [ ] Voice-based alerting
- [ ] Cloud telemetry for fleet management
- [ ] Integration with vehicle CAN bus

---

## Support & Debugging

### Check Vehicle Model Status
```javascript
const data = await fetch('http://api/vehicle/combined_data').then(r => r.json());
console.log(data.system_status);    // "Active" or "Initializing"
console.log(data.model_type);       // "Vehicle"
```

### Common Issues

**Issue:** Model stuck in "Initializing"
- **Solution:** Check camera connection, ensure face is visible

**Issue:** Predictions not updating
- **Solution:** Check WebSocket connection, verify `/ws/vehicle/detect` is receiving frames

**Issue:** Head position jumping around
- **Solution:** Reset calibration, ensure proper lighting

---

## Summary

The **Vehicle Model** provides a practical, **lightweight alternative** to the standard fatigue detector—designed specifically for **real-world vehicle environments** where:

✓ Health sensors may not be available  
✓ Simplicity & robustness are prioritized  
✓ Only visual cues (head position, eye closure, yawning) matter  
✓ Fast, low-latency detection is critical  

**Use the Vehicle Model for:** 🚗 Driver monitoring, ride-sharing, fleet management  
**Use the Standard Model for:** 🧠 Clinical fatigue studies, comprehensive health analysis
