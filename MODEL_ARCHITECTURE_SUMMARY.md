# Fatigue Detection Model Architecture Summary

## Overview
The fatigue detection system is a full-stack application that combines **computer vision (physical sensors)** and **physiological sensors (psychological/biometric)** to detect driver fatigue in real-time. The backend uses a **Random Forest V3 model** with multi-modal data fusion and safety-critical fallbacks.

---

## 1. CURRENT MODEL FILES AND STRUCTURE

### Backend Architecture
```
backend_flask/
├── app.py                          # Flask server with WebSocket endpoint
├── config.py                       # Configuration management
├── ml/
│   ├── ml_engine.py                # Main ML inference engine (Random Forest V3)
│   └── models/
│       └── lstm_fatigue_model.h5   # Legacy LSTM model (present but not used)
├── cv/
│   ├── head_pose.py                # Head pose estimation (PnP + calibration)
│   └── perclos.py                  # Eye closure detection (MediaPipe + EAR/MAR)
└── sensors/
    └── serial_reader.py             # Arduino serial communication & IMU data

Frontend Architecture
src/
├── api.js                          # HTTP/WebSocket API client
├── App.js                          # Main dashboard component
├── context/
│   ├── FatigueContext.js           # Global data state management (polling)
│   └── ThemeContext.js              # Theme management (light/dark mode)
├── hooks/
│   ├── useFatigueData.js           # Extract ML prediction + sensor data
│   ├── useHeartRate.js              # Heart rate history management
│   ├── useHeadPosition.js           # Head position smoothing animation
│   ├── useCombinedData.js           # Combined data aggregation
│   ├── useSensorData.js             # Sensor data extraction
│   └── useTemperature.js            # Temperature history management
└── components/
    ├── FatigueStatus.js            # ML prediction display + confidence
    ├── CameraModule.js             # WebSocket video stream & processing
    ├── HeartRateChart.js           # HR trend visualization
    ├── BodyTemperatureChart.js     # Temperature trend visualization
    ├── HeadPositionChart.js        # 3D head position visualization
    ├── HRVChart.js                 # Heart rate variability
    ├── DrowsinessIndicators.js     # Feature importance display
    └── ThemeToggle.js              # Light/dark mode toggle
```

### ML Model Files (Training/Offline)
```
ml_model/
├── random_forest_v2_model.py       # RF V2 training script (public version)
├── random_forest_v2_test.py        # Offline testing
├── QUICK_START_RF_V2.py            # Quick training runner
├── random_forest_v2_integration.py # Integration code
└── models/
    └── (trained .pkl model files)
```

---

## 2. SENSOR TYPES: PSYCHOLOGICAL vs PHYSICAL

### **Physical Sensors** (Hardware-based, from Arduino)
Collected via `serial_reader.py`:
- **Temperature**: Thermistor on chest strap
  - Units: °C (Celsius)
  - Range: ~36-38°C normal, <35°C or >39°C abnormal
  - **Purpose**: Physiological stress indicator
  
- **Heart Rate (HR)**: Pulse sensor / Optical PPG
  - Units: bpm (beats per minute)
  - Range: 60-100 bpm normal, >120 or <50 critical
  - **Purpose**: Autonomic nervous system activity, stress/fatigue indicator
  
- **SpO2 (Blood Oxygen)**: Pulse oximeter
  - Units: % saturation
  - Range: 95-99% normal, <90% critical
  - **Purpose**: Respiratory/systemic adequacy
  
- **Accelerometer (ax, ay, az)**: 3-axis IMU on chest
  - Units: g (gravitational units)
  - **Purpose**: Head position estimation (Pitch, Yaw, Roll)
  - Used in: `calculate_head_position()` in `serial_reader.py`
  
- **Gyroscope (gx, gy, gz)**: 3-axis rotation sensor
  - Units: deg/s
  - **Purpose**: Head motion detection (unused in current model but available)

### **Computer Vision Sensors** (Camera-based, from Webcam)
Processed via `perclos.py` + `head_pose.py`:

- **EAR (Eye Aspect Ratio)**
  - Computed from 6 eye landmark coordinates (MediaPipe FaceMesh)
  - Range: 0.0-1.0 (higher = eyes more open)
  - **Threshold**: Personal calibration (default 0.30)
  - **Purpose**: Instant eye closure detection
  - Function: `eye_aspect_ratio()` in `perclos.py`
  
- **PERCLOS (Percentage Eye Closure over Time)**
  - Computed as: % of frames where EAR < threshold
  - Window: 6-frame rolling history
  - Range: 0-100%
  - **Threshold**: >55% indicates fatigue
  - **Purpose**: Temporal eye closure pattern detection
  
- **MAR (Mouth Aspect Ratio)**
  - Computed from 4 mouth landmark coordinates
  - **Purpose**: Yawn detection (combined with temporal analysis)
  - Function: `mouth_aspect_ratio()` in `perclos.py`
  
- **Yawn Status**: Classified as "Closed", "Opening", or "Yawning"
  - Detected when: High MAR + temporal mouth opening pattern
  - **Purpose**: Behavioral fatigue indicator
  
- **Head Pose** (Pitch, Yaw, Roll):
  - Estimated via: PnP (Perspective-n-Point) algorithm
  - Source 1: Camera-based (MediaPipe landmarks) see `head_pose.py`
  - Source 2: Accelerometer-based fallback from IMU
  - Units: Degrees (-90 to +90)
  - **Purpose**: Detect head nodding, looking away (fatigue behavior)
  - Auto-calibration: First 30 frames establish baseline

---

## 3. DATA BEING PROCESSED

### Input Features to ML Model (from `ml_engine.py.predict()`)

**Vision Data Object:**
```python
{
    "status": "Open",           # Face detection status
    "perclos": 15.5,            # % eye closure
    "ear": 0.42,                # Eye aspect ratio
    "mar": 0.18,                # Mouth aspect ratio
    "closed_frames": 2,         # Consecutive frame count with eyes closed
    "yawn_status": "Closed",    # "Closed" / "Opening" / "Yawning"
    "head_angle_x": 5.2,        # Pitch (up/down)
    "head_angle_y": -8.1        # Yaw (left/right)
}
```

**Sensor Data Object:**
```python
{
    "temperature": 37.3,    # °C
    "hr": 78,              # beats per minute
    "spo2": 97,            # % O2 saturation
    "ax": 0.12,            # Accelerometer X
    "ay": -0.05,           # Accelerometer Y
    "az": 9.81,            # Accelerometer Z
    "timestamp": 1710074321
}
```

### Feature Engineering & Temporal Processing

**In MLEngine:**
- `calculate_temporal_features()`: Rolling mean/std over window of 20 frames
  - Computes: `ear_mean`, `ear_std`, `mar_mean`, `mar_std`, `pitch_mean`, `hr_mean`, etc.
  - Purpose: Capture trends and variability

**Adaptive Calibration (Auto-tuning):**
- `base_ear`: Running baseline for "Alert" state (user-specific)
- `PERSONAL_EAR_THRESH`: Personal eye closure threshold (trained from first 30 frames)
- `calibration_frames`: Counter for learning phase

**Safety-Critical Logic:**
1. **Microsleep Detection**: If `closed_frames > 10` (~0.33s) → Force "FATIGUED"
2. **High PERCLOS**: If `perclos > 55%` → Force "FATIGUED"
3. **Head Yaw Correction**: EAR adjusted by yaw angle to prevent false positives when looking away
4. **Sensor Stagnation**: Detect frozen sensors (HR stuck for 50+ frames) → Mark unreliable
5. **Face Stability**: Detect camera shake via nose position tracking → Ignore unreliable frames

---

## 4. DATA FLOW: BACKEND TO FRONTEND

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          BACKEND (Flask + Python)                       │
│                                                                          │
│  ┌──────────────────┐      ┌──────────────────┐      ┌────────────────┐│
│  │   Arduino/IMU    │─────▶│  serial_reader   │─────▶│ latest_sensor  ││
│  │  (Serial Port)   │      │  (Thread-safe)   │      │      data      ││
│  └──────────────────┘      └──────────────────┘      └────────────────┘│
│                                                                          │
│  ┌──────────────────┐      ┌──────────────────┐      ┌────────────────┐│
│  │   WebCamera      │─────▶│  perclos.py      │─────▶│  perclos_data  ││
│  │  (Video Stream)  │      │ (MediaPipe)      │      │   (EAR/MAR)    ││
│  └──────────────────┘      └──────────────────┘      └────────────────┘│
│                                                                          │
│  ┌──────────────────┐      ┌──────────────────┐      ┌────────────────┐│
│  │   MediaPipe      │─────▶│  head_pose.py    │─────▶│  cv_head_      ││
│  │   FaceMesh       │      │  (PnP Estimation)│      │   angles       ││
│  └──────────────────┘      └──────────────────┘      └────────────────┘│
│                                                                          │
│                              ▼                                           │
│                      ┌──────────────────┐                               │
│                      │  app.py: WebSocket│                             │
│                      │  /ws/detect      │                             │
│                      │  (receives frames)                              │
│                      └────────┬─────────┘                              │
│                               │                                         │
│                      ┌────────▼─────────┐                              │
│                      │ get_combined_    │                              │
│                      │ data_internal()  │                              │
│                      └────────┬─────────┘                              │
│                               │                                         │
│              ┌────────────────┼────────────────┐                       │
│              │                │                │                       │
│        ┌─────▼─────┐  ┌──────▼──────┐  ┌─────▼─────┐                 │
│        │ ML Engine │  │  Head Pose  │  │  Sensor   │                 │
│        │ (predict) │  │  Fallback   │  │  + PERCLOS│                 │
│        └─────┬─────┘  └──────┬──────┘  └─────┬─────┘                 │
│              │                │              │                         │
│              └────────────────▼──────────────┘                         │
│                               │                                         │
│                      ┌────────▼───────────┐                            │
│                      │ Combined Response  │                            │
│                      │ {sensor, perclos,  │                            │
│                      │  head_position,    │                            │
│                      │  prediction}       │                            │
│                      └────────┬───────────┘                            │
│                               │                                         │
│              ┌────────────────▼─────────────────┐                      │
│              │  WebSocket: send(JSON.dumps())   │                      │
│              │  OR REST: GET /api/combined_data │                      │
│              └────────────────┬─────────────────┘                      │
└───────────────────────────────┼──────────────────────────────────────────┘
                                │
┌───────────────────────────────▼──────────────────────────────────────────┐
│                      FRONTEND (React + JavaScript)                        │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │ CameraModule.js (WebSocket Connection)                              │ │
│  │  - Captures camera frames                                           │ │
│  │  - Sends via WebSocket: {image_data: base64}                       │ │
│  │  - Receives: {sensor, perclos, head_position, prediction, ...}     │ │
│  │  - Updates: setFullData(result) → FatigueContext                   │ │
│  └────────────────────┬────────────────────────────────────────────────┘ │
│                       │                                                    │
│  ┌────────────────────▼────────────────────────────────────────────────┐ │
│  │ FatigueContext.js (Global Data State + Polling Backup)              │ │
│  │  - Maintains: fullData (sensor, perclos, head_position, prediction) │ │
│  │  - Polling: GET /api/combined_data every 500ms (fallback)           │ │
│  │  - Maintains: heartRateHistory, tempHistory                         │ │
│  └────────────────────┬────────────────────────────────────────────────┘ │
│                       │                                                    │
│       ┌───────────────┼─────────────────────┐                            │
│       │               │                     │                            │
│  ┌────▼──────┐  ┌────▼──────┐        ┌────▼──────┐                      │
│  │ Hooks:    │  │ Hooks:    │        │ Hooks:    │                      │
│  │useFatigueData│useFatigueData│        │useHeadPosition
│  │(extract ML │  │ (HR/Temp  │        │(smooth 3D │                      │
│  │ prediction)│  │ history)  │        │animation) │                      │
│  └────┬──────┘  └────┬──────┘        └────┬──────┘                      │
│       │               │                    │                             │
│  ┌────▼──────────────▼────────────────────▼─────┐                       │
│  │           Display Components                   │                       │
│  │ ┌──────────────────────────────────────────┐  │                       │
│  │ │ FatigueStatus: ML predictions + confidence│  │                       │
│  │ │ HeartRateChart: HR trends (sparkline)    │  │                       │
│  │ │ BodyTemperatureChart: Temp trends        │  │                       │
│  │ │ HeadPositionChart: 3D head orientation   │  │                       │
│  │ │ DrowsinessIndicators: Feature breakdown  │  │                       │
│  │ │ CameraModule: Live video display         │  │                       │
│  │ └──────────────────────────────────────────┘  │                       │
│  └──────────────────────────────────────────────┘                        │
└──────────────────────────────────────────────────────────────────────────┘
```

### Detailed Data Flow Steps

**1. Camera Frame Capture & Processing:**
```
Browser → CameraModule.js
→ navigator.mediaDevices.getUserMedia()
→ Capture frame at ~30fps
→ Compress to JPEG (quality 0.5, 480px width)
→ Encode to Base64
→ Send via WebSocket: {image_data: "data:image/jpeg;base64,..."}
```

**2. Backend Processing (WebSocket):**
```
Flask /ws/detect endpoint
→ Receive {image_data: base64}
→ Decode base64 → np.ndarray
→ process_face_mesh(frame) [perclos.py]
  ├─ Detect face landmarks with MediaPipe
  ├─ Calculate EAR, MAR
  ├─ Detect yawning pattern
  ├─ Call calculate_cv_head_pose() [head_pose.py]
  └─ Update global: perclos_data, cv_head_angles
→ get_combined_data_internal()
  ├─ Read: latest_sensor_data (from serial thread)
  ├─ Calculate head_position from IMU OR fallback to cv_head_angles
  ├─ Call ml_engine.predict(sensor_data, vision_data) [ml_engine.py]
  │  └─ Returns: {status, confidence, raw_probs, flag}
  └─ Assemble: {sensor, perclos, head_position, prediction, ...}
→ WebSocket send(JSON.dumps(combined_data))
```

**3. Frontend State Update:**
```
CameraModule.js
→ ws.onmessage(event)
→ Parse JSON: result = JSON.parse(event.data)
→ Update context: setFullData(result)
→ FatigueContext triggers useEffect
  ├─ Update: heartRateHistory
  ├─ Update: tempHistory
  └─ Triggers re-renders in subscribed components
```

**4. Component Consumption (via Hooks):**
```
FatigueStatus.js
→ useFatigueData() hook
  └─ Extract from FatigueContext.fullData:
     ├─ sensor.temperature, sensor.hr, sensor.spo2
     ├─ perclos.perclos, perclos.ear, perclos.yawn_status
     └─ prediction.status, prediction.confidence, prediction.flag
→ Render ML status + confidence bars + feature breakdown

HeartRateChart.js
→ useHeartRate() hook
  └─ Get heartRateHistory from FatigueContext
→ Plot as sparkline/trend chart

HeadPositionChart.js
→ useHeadPosition() hook
  ├─ Get angle_x, angle_y, angle_z from FatigueContext
  ├─ Apply smoothing animation (10% LERP factor)
  ├─ Clamp to anatomical limits (±40° pitch, ±45° yaw)
  └─ Render 3D visualization
```

### Fallback Polling Mechanism
If WebSocket disconnects:
```javascript
FatigueContext.js:
- usePolling(): GET /api/combined_data every 500ms
- Falls back to REST API
- Updates fullData state same way as WebSocket
- Maintains data continuity
```

---

## 5. KEY FUNCTION SIGNATURES & METHODS

### Backend (Python)

#### `ml_engine.py` - MLEngine Class
```python
class MLEngine:
    def __init__(self, model_path="fatigue_model.pkl"):
        # Load trained Random Forest model
        
    def load_model(self):
        """Load .pkl model from disk"""
        
    def reset_calibration(self):
        """Reset adaptive EAR baseline and state machine"""
        
    def calculate_temporal_features(self, current_data):
        """Compute rolling mean/std over window"""
        → Returns: {ear_mean, ear_std, mar_mean, mar_std, pitch_mean, hr_mean, ...}
        
    def predict(self, sensor_data, vision_data):
        """Main ML inference function"""
        Input:
            sensor_data = {"hr": float, "temperature": float, ...}
            vision_data = {"ear": float, "perclos": float, "mar": float, ...}
        Output:
            {
                "status": "Alert" | "Drowsy" | "Fatigued",
                "confidence": float (0-1),
                "raw_probs": [p_alert, p_drowsy, p_fatigued],
                "flag": optional safety flag
            }
        
        Safety Checks:
        1. Microsleep: closed_frames > 10 → Force "Fatigued"
        2. High PERCLOS: perclos > 55% → Force "Fatigued"
        3. Head Yaw Correction: EAR *= (1 + yaw/90 * 0.2)
        4. Sensor Integrity: Track frozen HR values
        5. Face Stability: Ignore shaky camera frames
```

#### `perclos.py` - PERCLOS & EAR Detection
```python
def eye_aspect_ratio(eye):
    """Calculate EAR from 6 eye landmark points"""
    Input: eye = [(x1,y1), (x2,y2), ..., (x6,y6)]
    Output: float (0-1)
    Formula: (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
    
def mouth_aspect_ratio(mouth):
    """Calculate MAR for yawn detection"""
    Input: mouth = [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]
    Output: float
    Formula: vertical_dist / horizontal_dist
    
def reset_eye_calibration():
    """Initiate personal EAR threshold calculation"""
    - Collects 30 frames of open-eye EAR values
    - Sets PERSONAL_EAR_THRESH = median(EAR) * 0.80
    
def process_face_mesh(frame):
    """Main face processing pipeline"""
    Input: frame (numpy BGR image)
    1. Detect face landmarks with MediaPipe
    2. Calculate EAR & MAR
    3. Calculate eye status history (6-frame rolling)
    4. Detect PERCLOS (% closed frames)
    5. Detect yawning pattern (temporal MAR analysis)
    6. Call calculate_cv_head_pose()
    Output: Updates global perclos_data dict
    
Global State Updated:
    perclos_data = {
        "status": "Open" | "Closed" | "No Face",
        "perclos": float,
        "ear": float,
        "yawn_status": "Closed" | "Opening" | "Yawning",
        "timestamp": int
    }
```

#### `head_pose.py` - Head Pose Estimation
```python
def calculate_cv_head_pose(landmarks, img_w, img_h):
    """Estimate head pitch, yaw, roll using PnP"""
    Input:
        landmarks: MediaPipe face landmarks
        img_w, img_h: image dimensions
    Output:
        (pitch, yaw, roll, is_calibrated) - all in degrees
        
    Algorithm:
    1. Select 6 3D model points (nose, chin, eyes, mouth corners)
    2. Extract corresponding 2D image points from landmarks
    3. Solve PnP (Perspective-n-Point) → Rotation matrix
    4. Decompose: RQDecomp3x3() → Euler angles
    5. Apply calibration offset (learned from first 30 frames)
    6. Clamp to anatomical limits: pitch [-90,90], yaw [-90,90], roll [-90,90]
    
Calibration:
    - CALIBRATION_FRAMES_TARGET = 30
    - Learn: pitch_offset, yaw_offset, roll_offset
    - User-specific: Handles camera tilt, laptop position, etc.
```

#### `serial_reader.py` - Sensor Thread
```python
def start_serial_thread():
    """Launch background thread for Arduino serial communication"""
    - Continuously reads from serial port
    - Parses sensor data (temperature, HR, SpO2, IMU)
    - Updates global: latest_sensor_data (thread-safe with lock)
    
def calculate_head_position(ax, ay, az):
    """Convert accelerometer to head position angles"""
    Input: ax, ay, az (accelerometer G values)
    Output:
        (position: str, angle_x: float, angle_y: float, angle_z: float)
        position ∈ {"Center", "Up", "Down", "Left", "Right", "Up-Left", ...}
        
    Algorithm:
        pitch = atan2(ax, sqrt(ay²+az²))
        yaw = atan2(ay, sqrt(ax²+az²))
        roll = atan2(ay, az)
        Compare to thresholds: ±10° for vertical, ±10° for horizontal
        
def parse_raw_sensor_string(raw: str):
    """Parse comma-separated sensor data"""
    Example input: "T:36.5, HR:75, SPO2:97.5, AX:0.1,..."
    Output: {"temperature": 36.5, "hr": 75, "spo2": 97.5, ...}
```

#### `app.py` - Flask Server
```python
def initialize_systems():
    """Startup: Initialize serial thread + ML engine"""
    
@app.route("/api/combined_data", methods=['GET'])
def get_combined_data():
    """REST endpoint for data polling"""
    Returns: {sensor, perclos, head_position, prediction, server_time, system_status}
    
@sock.route('/ws/detect')
def websocket_endpoint(ws):
    """WebSocket endpoint for real-time video processing"""
    1. Receive: {image_data: base64}
    2. Decode & process frame
    3. Call process_face_mesh()
    4. Call get_combined_data_internal()
    5. Send: JSON response
    Process: Every 3rd frame (throttle for performance)
    
def get_combined_data_internal():
    """Assemble combined response object"""
    1. Read sensor data (with lock)
    2. Calculate head position (sensor OR vision fallback)
    3. Call ml_engine.predict() (if not calibrating)
    4. Return: {sensor, perclos, head_position, prediction, ...}
    
@app.route("/api/reset_calibration", methods=['POST'])
def reset_calibration_endpoint():
    """Reset ML engine + eye calibration"""
```

### Frontend (JavaScript/React)

#### `FatigueContext.js` - Global State Management
```javascript
export const FatigueProvider = ({ children }) => {
    // State
    const [fullData, setFullData] = useState(null);
    const [heartRateHistory, setHeartRateHistory] = useState([]);
    const [tempHistory, setTempHistory] = useState([]);
    
    // Polling Effect (500ms interval)
    useEffect(() => {
        fetch(`${API_BASE}/api/combined_data`)
            → Update fullData, heartRateHistory, tempHistory
    }, []);
    
    // Export via context
    const value = { fullData, setFullData, heartRateHistory, tempHistory };
    return <FatigueContext.Provider value={value}>{children}</FatigueContext.Provider>
}
```

#### `useFatigueData.js` - Hook for ML Extraction
```javascript
export const useFatigueData = () => {
    const { fullData } = useFatigueContext();
    
    Returns: {
        temperature: number,
        hr: number,
        spo2: number,
        perclos: number,        // from perclos_data
        ear: number,            // Eye aspect ratio
        mar: number,            // Mouth aspect ratio
        status: string,         // "Open" | "Closed" | "No Face"
        yawn_status: string,    // "Closed" | "Opening" | "Yawning"
        ml_fatigue_status: string,      // "Alert" | "Drowsy" | "Fatigued"
        ml_confidence: number,          // 0-1
        ml_flag: string,               // Safety flag from ML
        system_status: string   // "Active" | "Initializing"
    }
}
```

#### `useHeadPosition.js` - Smoothing & Animation
```javascript
export const useHeadPosition = () => {
    // Retrieve raw angles from context
    const {targetX, targetY, targetZ} = fullData.head_position;
    
    // Apply smoothing animation:
    // 1. CLAMPING: Anatomical limits (pitch [-40,40], yaw [-45,45], roll [-20,20])
    // 2. DEADZONE: Ignore micro-movements < 1°
    // 3. LERP: currentX += (targetX - currentX) * 0.1
    // 4. SETTLE: Stop when < 0.1° away
    
    Returns: {
        position: string,    // "Center" | "Up" | "Down" | ...
        angle_x: number,     // Smoothed pitch
        angle_y: number,     // Smoothed yaw
        angle_z: number,     // Smoothed roll
        source: string,      // "Sensor" | "Vision (Fallback)"
        calibrated: boolean
    }
}
```

#### `CameraModule.js` - Video Stream
```javascript
function CameraModule() {
    // WebSocket initialization
    useEffect(() => {
        navigator.mediaDevices.getUserMedia({ video: true })
            → Capture to <video> element
        
        ws = new WebSocket(API_BASE.replace(/^http/, 'ws') + '/ws/detect')
        
        ws.onmessage = (event) => {
            result = JSON.parse(event.data)
            setFullData(result)  // Update global context
        }
    }, []);
    
    // Frame sending loop (via requestAnimationFrame)
    function startSendingFrames() {
        - Draw video → canvas (downscale to 480px width)
        - Compress to JPEG (quality 0.5)
        - Send: ws.send({image_data: base64})
        - Throttle: ~30fps via animation frame
    }
}
```

#### `FatigueStatus.js` - ML Prediction Display
```javascript
export default function FatigueStatus() {
    const data = useFatigueData();
    
    // Extract ML results
    const {
        ml_fatigue_status,          // "Alert" | "Drowsy" | "Fatigued"
        ml_confidence,              // 0-1
        ml_flag,                    // Safety flag
        perclos, yawn_status, hr, temperature
    } = data;
    
    // Feature breakdown (for user understanding)
    const features = [
        { label: "PERCLOS", value: normPerclos, raw: "15.3%" },
        { label: "Yawn_Seq", value: normYawn, raw: "None" },
        { label: "HR_Var", value: normHR, raw: "75 bpm" },
        { label: "Temp_Delta", value: normTemp, raw: "37.1°C" }
    ];
    
    // Render
    - Display panel showing predicted class + confidence
    - Bar chart for feature importance
    - Reset calibration button
    - Status indicator (green/yellow/red)
}
```

---

## 6. CURRENT CONFIGURATION

From `backend_flask/config.py`:
```python
class Config:
    ARDUINO_PORT = "COM6"               # Serial port for Arduino
    BAUD_RATE = 115200
    MAX_HISTORY = 100                   # Sensor history buffer
    SENSOR_TIMEOUT = 2.0 seconds
    USE_MOCK_DATA = False               # Disable mock data in production
    
    MODEL_PATH = "ml/models/fatigue_model.pkl"
    ML_INTERVAL = 0.5 seconds          # Prediction frequency
    DEBUG = True
```

---

## 7. DATA PROCESSING PIPELINE SUMMARY

```
┌────────────────────────────────────────────────────────────────┐
│ REAL-TIME DATA FUSION PIPELINE (1 iteration @ ~30 FPS)         │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│ INPUT (Parallel streams):                                       │
│  • Video frame from camera                                      │
│  • Serial sensor data (Arduino)                                 │
│                                                                 │
│ VISION PIPELINE:                                                │
│  1. MediaPipe: Detect face landmarks (468 points)              │
│  2. Calculate: EAR (eye aspect), MAR (mouth aspect)            │
│  3. Calculate: Head Pose (Pitch/Yaw/Roll via PnP)              │
│  4. Temporal: EAR history → PERCLOS (% closure)                │
│  5. Behavior: Yawn detection (high MAR + temporal)             │
│  Output: perclos_data {ear, perclos, status, ...}              │
│                                                                 │
│ SENSOR PIPELINE:                                                │
│  1. Arduino: Temperature, HR, SpO2, IMU (ax,ay,az,gx,gy,gz)   │
│  2. When unavailable: Calculate head position from accelerometer│
│  3. Fallback: Use camera-based head pose instead               │
│  Output: latest_sensor_data + head_position                    │
│                                                                 │
│ ML PREDICTION PIPELINE (every 0.5s):                            │
│  1. Assemble features: EAR, PERCLOS, MAR, HR, Temp, Pitch, Yaw │
│  2. Apply temporal aggregation (rolling 20-frame window)        │
│  3. Safety checks: Microsleep? High PERCLOS? Face stable?      │
│  4. ML Model: Random Forest classifier                          │
│  5. Output: {status, confidence, raw_probs, flag}              │
│                                                                 │
│ OUTPUT (Combined):                                              │
│  {                                                              │
│    sensor: {hr, temperature, spo2, timestamp},                │
│    perclos: {ear, perclos, yawn_status, status},              │
│    head_position: {position, angle_x,_y,_z, source},         │
│    prediction: {status, confidence, flag},                    │
│    system_status: "Active" | "Initializing"                   │
│  }                                                              │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## 8. SAFETY-CRITICAL FEATURES

1. **Microsleep Detection**
   - If eyes closed > 10 frames (~0.33s) → Immediate "FATIGUED" alert
   - No ML inference needed (hard rule)

2. **High PERCLOS Override**
   - If PERCLOS > 55% → Immediate "FATIGUED"
   - Indicates persistent eye closure despite blinks

3. **Head Yaw Compensation**
   - When user looks away, EAR naturally decreases
   - Applied correction: `EAR *= 1.0 + (yaw/90) * 0.2`
   - Prevents false fatigue detection during head turn

4. **Sensor Integrity Checks**
   - Detect frozen HR (same value for 50+ frames)
   - Mark as unreliable
   - Use historical average instead

5. **Face Stability Monitoring**
   - Track nose position frame-to-frame
   - If motion > 5% screen width → Likely camera shake
   - Ignore unreliable EAR reading

6. **State Hysteresis**
   - Hold state for 5 frames before switching
   - Prevents flickering between Alert/Drowsy
   - Smooth state transitions

---

## 9. MODEL INFORMATION

**Current ML Model:** Random Forest V3 (fatigue_model.pkl)
- **Type:** Classification (3 classes)
- **Classes:** Alert (0), Drowsy (1), Fatigued (2)
- **Input Features:** EAR, PERCLOS, MAR + temporal derivatives
- **Training Data:** DDD (Driver Drowsiness Dataset)
- **Framework:** scikit-learn RandomForestClassifier
- **Inference Time:** ~10-20ms per prediction

**Legacy Model:** LSTM (lstm_fatigue_model.h5)
- Status: Present but not actively used
- Can be revived for sequence-based predictions if needed

---

## 10. TESTING & CALIBRATION

**Initial Setup (User's First Session):**
1. Eye Calibration: 30 frames of "looking at camera normally"
   - Computes personal EAR threshold
   - Auto-adjusts for glasses, eyelid shape, lighting, etc.

2. Head Pose Calibration: 30 frames of "head straight ahead"
   - Learns offset for camera tilt and mounting angle
   - Handles any hardware configuration

3. ML Reset: `/api/reset_calibration` endpoint
   - Clears history
   - Resets adaptive baselines
   - Useful if switching users or environmental change

---

## 11. DEPLOYMENT & CONNECTION

**Backend:**
- Flask server on `http://0.0.0.0:5000`
- WebSocket: `ws://0.0.0.0:5000/ws/detect`
- REST fallback: `/api/combined_data` (polling)
- ngrok support for remote access

**Frontend:**
- React SPA (single-page app)
- Polling interval: 500ms (if WebSocket unavailable)
- Browser camera permission required
- Works on localhost + public URLs (ngrok)

---

**End of Report**
