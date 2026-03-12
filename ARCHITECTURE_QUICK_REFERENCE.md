# Fatigue Detection System - Architecture Quick Reference

## Component Dependency Map

```
Frontend Layer:
├── App.js (Main Dashboard)
│   └── DashboardContent
│       ├── Header (Brand + Status)
│       ├── Charts Grid
│       │   ├── HeartRateChart ← useHeartRate() ← FatigueContext
│       │   ├── BodyTemperatureChart ← useFatigueData() ← FatigueContext
│       │   ├── HRVChart ← useFatigueData() ← FatigueContext
│       │   └── HeadPositionChart ← useHeadPosition() ← FatigueContext
│       └── Side Panel
│           ├── CameraModule
│           │   ├── WebSocket (send frames)
│           │   └── Updates: setFullData() ← FatigueContext
│           └── FatigueStatus
│               └── useFatigueData() ← FatigueContext

FatigueContext (Central State):
├── fullData (from WebSocket OR polling)
├── heartRateHistory
└── tempHistory
   ↓ (polling every 500ms if WS unavailable)
   api.js: GET /api/combined_data

Backend Layer:
app.py (Flask):
├── POST /api/reset_calibration
├── GET /api/combined_data
├── GET /api/sensor_data
├── GET /api/sensor_data/history
├── POST /api/sensor_data/ingest
└── WS /ws/detect
    │
    ├─→ perclos.py: process_face_mesh()
    │   ├─ MediaPipe face detection
    │   ├─ eye_aspect_ratio() → EAR
    │   ├─ mouth_aspect_ratio() → MAR
    │   ├─ PERCLOS calculation (temporal)
    │   ├─ Yawn detection
    │   └─ Calls: head_pose.py
    │
    ├─→ head_pose.py: calculate_cv_head_pose()
    │   ├─ PnP estimation
    │   ├─ Euler angle decomposition
    │   └─ Auto-calibration (first 30 frames)
    │
    ├─→ serial_reader.py (background thread)
    │   ├─ Arduino serial communication
    │   ├─ Temperature, HR, SpO2
    │   ├─ Accelerometer (ax, ay, az)
    │   ├─ Gyroscope (gx, gy, gz)
    │   └─ calculate_head_position() [IMU fallback]
    │
    └─→ ml_engine.py: predict()
        ├─ Feature aggregation
        ├─ Temporal smoothing
        ├─ Safety-critical checks
        │   ├─ Microsleep detection
        │   ├─ High PERCLOS override
        │   └─ Head yaw compensation
        └─ ML model inference → status, confidence, flag
```

---

## Data Structure Reference

### Backend Global State Objects

**perclos_data** (from `perclos.py`):
```python
{
    "status": "Open" | "Closed" | "No Face" | "Unstable",
    "perclos": float,                    # % eye closure
    "ear": float,                        # Eye aspect ratio (0-1)
    "yawn_status": "Closed" | "Opening" | "Yawning",
    "mar": float,                        # Mouth aspect ratio
    "closed_frames": int,                # Consecutive frame count
    "timestamp": int,                    # Unix seconds
    "is_calibrating": bool               # During 30-frame calibration
}
```

**latest_sensor_data** (from `serial_reader.py`):
```python
{
    "temperature": float,                # °C
    "ax": float, "ay": float, "az": float,  # Accelerometer (m/s² or g)
    "gx": float, "gy": float, "gz": float,  # Gyroscope (deg/s)
    "hr": float,                         # Heart rate (bpm)
    "spo2": float,                       # Blood oxygen (%)
    "timestamp": int                     # Unix seconds
}
```

**cv_head_angles** (from `head_pose.py`):
```python
{
    "pitch": float,          # Rotation X-axis (up/down), degrees [-90,90]
    "yaw": float,           # Rotation Y-axis (left/right), degrees [-90,90]
    "roll": float,          # Rotation Z-axis (tilt), degrees [-90,90]
    "is_calibrated": bool   # Calibration complete flag
}
```

**head_position_data** (derived from IMU):
```python
{
    "position": "Center" | "Up" | "Down" | "Left" | "Right" | "Up-Left" | ...,
    "angle_x": float,       # Pitch from accelerometer
    "angle_y": float,       # Yaw from accelerometer
    "angle_z": float,       # Roll from accelerometer
    "timestamp": int
}
```

**ML Prediction Output**:
```python
{
    "status": "Alert" | "Drowsy" | "Fatigued" | "Unknown",
    "confidence": float,                 # 0.0-1.0
    "raw_probs": [p_alert, p_drowsy, p_fatigued],
    "flag": "MICROSLEEP" | "HIGH_PERCLOS" | "SKIPPED_NO_FACE" | ... | None
}
```

### Frontend Data Flow Objects

**FatigueContext.fullData**:
```javascript
{
    sensor: {temperature, hr, spo2, ax, ay, az, gx, gy, gz, timestamp},
    perclos: {status, perclos, ear, yawn_status, mar, timestamp},
    head_position: {position, angle_x, angle_y, angle_z, source, calibrated, timestamp},
    prediction: {status, confidence, raw_probs, flag},
    server_time: int,
    system_status: "Active" | "Initializing" | "Offline"
}
```

**useFatigueData output**:
```javascript
{
    temperature, hr, spo2,           // Physical sensors
    perclos, ear, mar,               // Vision metrics
    status, yawn_status,             // Vision status
    ml_fatigue_status, ml_confidence, ml_flag,  // ML output
    system_status, timestamp
}
```

---

## Processing Pipelines Timing

### WebSocket Path (Real-time)
```
Camera Frame (30fps)
    ↓
CameraModule.js: Encode to JPEG base64
    ↓ [Network RTT ~10-50ms]
    ↓
app.py: /ws/detect
    ↓
process_face_mesh() [20-30ms for MediaPipe]
    ↓
calculate_cv_head_pose() [5-10ms for PnP]
    ↓
ml_engine.predict() [every 0.5s, 10-20ms]
    ↓
get_combined_data_internal() [5ms]
    ↓
WebSocket send (JSON stringify/serialize ~1ms)
    ↓ [Network RTT ~10-50ms]
    ↓
CameraModule.js: onmessage
    ↓
FatigueContext: setFullData() [React state update ~1ms]
    ↓
Component re-renders [5-20ms]

Total latency: ~100-200ms end-to-end (camera to displayed inference)
```

### Polling Path (Fallback)
```
FatigueContext polling loop (every 500ms)
    ↓
GET /api/combined_data (REST)
    ↓ [Network RTT ~10-50ms]
    ↓
get_combined_data_internal() [reuses cached perclos_data]
    ↓
JSON response
    ↓ [Network RTT ~10-50ms]
    ↓
FatigueContext: setFullData()
    ↓
Component re-renders

Total latency: ~500ms base + network RTT
```

---

## Sensor Priority & Fallback Chain

### Head Position:
1. **Prefer:** IMU (accelerometer) from Arduino
   - Faster, more stable
   - Less affected by lighting/occlusion
   
2. **Fallback:** Computer vision (MediaPipe landmarks + PnP)
   - When Arduino unavailable
   - When sensor data stale (>2 seconds)
   - Labeled as "Vision (Fallback)" in UI

### EAR (Eye Closure):
1. **Use:** Personal calibration threshold
   - Learned from first 30 frames
   - User-specific (glasses, eyelid, etc.)
   
2. **Fallback:** Default threshold 0.30
   - If calibration not yet complete

### ML Prediction:
1. **Active:** When face detected + stable
   
2. **Cached:** When face not detected briefly
   - Returns previous prediction
   - Prevents flickering
   
3. **Reset:** When face absent > 5 seconds
   - Returns "Unknown" status
   - Confidence → 0

---

## Sensor Reliability Metrics

| Sensor | Availability | Latency | Reliability |
|--------|--------------|---------|------------|
| Camera (Vision) | Always ON | 20-30ms | 95% (lighting dependent) |
| Arduino (IMU) | Background thread | ~5ms | 90% (hardware dependent) |
| Temperature | Via Arduino | 100ms (buffered) | 85% (sensor drift) |
| Heart Rate | Via Arduino | 100ms (buffered) | 88% (motion artifact) |
| SpO2 | Via Arduino | 100ms (buffered) | 80% (poor contact) |

---

## Key Thresholds & Parameters

| Parameter | Value | What it Means |
|-----------|-------|--------------|
| Window size (temporal) | 20 frames | Smooth ML features over 0.67s |
| Microsleep threshold | 10 frames | ~0.33s of eye closure → Alert |
| High PERCLOS threshold | 55% | > 55% closure in last 6 frames → Fatigue |
| Head yaw EAR correction | 0.2 factor | Boost EAR by 20% max when looking away |
| Sensor stale timeout | 2 seconds | No data for 2s → mark data invalid |
| Sensor frozen threshold | 50 frames | HR stuck for 1.67s → mark unreliable |
| Frame stability check | 5% screen | Motion > 5% width → ignore frame |
| Head calibration frames | 30 frames | Learn baseline in first 1 second |
| Eye calibration frames | 30 frames | Learn personal EAR threshold in 1 second |
| State persistence | 5 frames | Hold current state 0.17s before switch |
| ML inference frequency | 0.5s interval | One prediction every 500ms |
| Frontend polling | 500ms | Refresh data every 0.5s if no WebSocket |
| Frame processing throttle | Every 3rd frame | Process 1 of 3 camera frames |
| WebSocket send frequency | 30fps | Send processed frame response at camera rate |

---

## State Machine: Fatigue Status

```
                    ┌─────────────┐
                    │   ALERT     │
                    │ (Confident) │
                    └──────┬──────┘
                           │
         [High PERCLOS]    │    [Microsleep]
         [Yawning+Low EAR] │    [Closed > 10 frames]
                           │
                    ┌──────▼──────┐
                    │   DROWSY    │
                    │ (Moderate)  │
                    └──────┬──────┘
                           │
         [Persistent Yawning]│ [Recovery: Return to Alert]
         [Maintained Low EAR]│
         [ML scores high]    │
                           │
                    ┌──────▼───────┐
                    │   FATIGUED   │
                    │ (Critical)   │
                    └──────────────┘

Hysteresis:
- Hold state for 5 frames before transition
- Prevents rapid flickering
- Smooth user experience
```

---

## Key Files to Modify for Enhancements

| File | Current Role | Potential Enhancements |
|------|--------------|----------------------|
| `ml_engine.py` | ML inference | Add LSTM for temporal, new safety rules |
| `perclos.py` | Vision processing | Add blink frequency, gaze direction |
| `head_pose.py` | Head estimation | Add 6D head tracking, stabilization |
| `serial_reader.py` | Sensor input | Add more sensor types, IMU fusion |
| `app.py` | Flask server | Add authentication, data logging, cloud sync |
| `FatigueContext.js` | State management | Add local storage, offline support |
| `CameraModule.js` | Video streaming | Add canvas overlay visualization |
| `FatigueStatus.js` | Results display | Add history, trend analysis, alerts |

