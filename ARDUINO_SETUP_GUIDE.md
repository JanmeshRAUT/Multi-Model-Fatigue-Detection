# Arduino Integration with HuggingFace Backend

Connect your local Arduino sensors to the cloud-deployed HuggingFace Space backend via ngrok tunnel.

---

## Architecture

```
Arduino (USB)
    ↓
Arduino Bridge (localhost:5000) - Local Flask app
    ↓
ngrok tunnel (https://xxx.ngrok.io)
    ↓
HuggingFace Space Backend (fatiguepred)
    ↓
Frontend (React on Vercel or localhost)
```

---

## Setup Steps

### 1️⃣ Run Arduino Bridge Locally

```bash
# In terminal 1
cd e:\Fullstack

# Start Arduino Bridge
python arduino_bridge.py

# Output:
# ✅ Connected to Arduino on COM6
# 📊 Sensor data arriving...
```

**The bridge now listens on:** `http://localhost:5000`

Available endpoints:
- `GET /sensor_data` - Get latest sensor readings
- `GET /` - Health check

---

### 2️⃣ Create ngrok Tunnel

```bash
# In terminal 2
# Install ngrok if needed:
# - Download from https://ngrok.com/download
# - OR: choco install ngrok

# Create tunnel to expose Arduino Bridge
ngrok http 5000

# Output:
# Session Status                online
# Version                       3.x.x
# Forwarding                    https://abc-123-xyz.ngrok.io -> http://localhost:5000
# Web Interface                 http://localhost:4040
```

**Copy the HTTPS URL:** `https://abc-123-xyz.ngrok.io`

---

### 3️⃣ Configure HuggingFace Space

Go to your HF Space settings and add secret:

```
ARDUINO_TUNNEL_URL = https://abc-123-xyz.ngrok.io
```

**Path:** https://huggingface.co/spaces/JerryJR1705/fatiguepred/settings

---

### 4️⃣ Test the Connection

#### Test Arduino Bridge locally:
```bash
curl http://localhost:5000/sensor_data
```

Response:
```json
{
  "hr": 75,
  "temperature": 36.5,
  "spo2": 98,
  "status": "connected",
  "timestamp": "2026-04-21T15:30:00"
}
```

#### Test ngrok tunnel:
```bash
curl https://abc-123-xyz.ngrok.io/sensor_data
```

#### Test HF Space Arduino status:
```bash
curl https://JerryJR1705-fatiguepred.hf.space/api/arduino-status
```

Response:
```json
{
  "status": "connected",
  "message": "Arduino bridge is accessible",
  "tunnel_url": "https://abc-123-xyz.ngrok.io",
  "last_data": {...}
}
```

#### Make prediction with Arduino data:
```bash
curl -X POST https://JerryJR1705-fatiguepred.hf.space/predict \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "standard",
    "ear": 0.3,
    "mar": 0.5,
    "perclos": 10,
    "heart_rate": 0,  # Will be overridden by Arduino
    "temperature": 0   # Will be overridden by Arduino
  }'
```

The backend will:
1. Fetch real HR, SpO2, Temp from Arduino Bridge
2. Use your vision data (EAR, MAR, etc.)
3. Return prediction using HF models

---

## ⚙️ Configuration Files

### Local Arduino Bridge (.env)
```bash
ARDUINO_PORT=COM6          # Your Arduino port
BAUD_RATE=115200          # Arduino baud rate
```

### HF Space Environment
```bash
HF_FATIGUE_MODEL_REPO=JerryJR1705/fatiguemodel
HF_VEHICLE_MODEL_REPO=JerryJR1705/fatiguemodel
ARDUINO_TUNNEL_URL=https://abc-123-xyz.ngrok.io
```

---

## 🔄 Workflow

1. **Start locally:**
   ```bash
   # Terminal 1: Arduino Bridge
   python arduino_bridge.py
   
   # Terminal 2: ngrok tunnel
   ngrok http 5000
   
   # Terminal 3: Frontend (if testing locally)
   cd frontend && npm start
   ```

2. **Update HF Space** with ngrok URL in secrets

3. **Frontend points to:** `https://JerryJR1705-fatiguepred.hf.space`

4. **Flow:**
   - Frontend sends vision data to HF Space
   - HF Space fetches sensor data from Arduino Bridge via ngrok
   - HF Space predicts using both vision + sensor data
   - Results returned to frontend

---

## 🐛 Troubleshooting

### Arduino Bridge not connecting
```bash
# Check Arduino port
python -m serial.tools.list_ports

# Update ARDUINO_PORT in .env if different
ARDUINO_PORT=COM3  # or /dev/ttyUSB0 on Linux
```

### ngrok tunnel not working
```bash
# Check ngrok is running and port 5000 is free
netstat -an | findstr 5000

# Restart ngrok with new URL
ngrok http 5000
```

### HF Space can't reach tunnel
```bash
# Test tunnel manually
curl https://your-ngrok-url/sensor_data

# Check HF Space logs for errors
# https://huggingface.co/spaces/JerryJR1705/fatiguepred/logs

# Make sure ARDUINO_TUNNEL_URL includes https://
```

### No sensor data in predictions
```bash
# Check Arduino Bridge is running
curl http://localhost:5000/sensor_data

# Check ngrok tunnel is working
curl https://your-ngrok-url/sensor_data

# Check HF Space environment variable
# Go to Settings → Repository secrets → ARDUINO_TUNNEL_URL
```

---

## 📊 Data Flow Example

**Request:**
```json
{
  "mode": "standard",
  "ear": 0.35,
  "mar": 0.45,
  "perclos": 15,
  "heart_rate": 0
}
```

**HF Space Process:**
1. Receives request with vision data
2. Calls `fetch_arduino_sensor_data()` → Gets actual HR=78, Temp=36.6
3. Combines: vision data + Arduino sensor data
4. Predicts using HF models
5. Returns: `{status: "Alert", confidence: 0.92, ...}`

**Response:**
```json
{
  "status": "Alert",
  "confidence": 0.92,
  "raw_probs": {"Alert": 0.92, "Drowsy": 0.07, "Fatigued": 0.01},
  "model_source": "HuggingFace:JerryJR1705/fatiguemodel"
}
```

---

## 🎯 Best Practices

1. **Keep ngrok running** while using the system
2. **Update HF Space URL** if ngrok restarts (new URL each time)
3. **Monitor Arduino connection** - logs show `status: connected/disconnected`
4. **Use `/api/arduino-status`** to debug connection issues
5. **Test locally first** before deploying to HF Space

---

## 📝 Summary

| Component | Local | Cloud |
|---|---|---|
| **Arduino Bridge** | `localhost:5000` | N/A (runs locally) |
| **ngrok Tunnel** | Exposes bridge | `https://xxx.ngrok.io` |
| **HF Space Backend** | Calls bridge via tunnel | Receives requests |
| **Frontend** | Calls HF Space | Same HF Space endpoint |

Your Arduino data now flows seamlessly to the cloud!
