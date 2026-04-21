---
title: Fatigue Detection Backend
emoji: 🧠
colorFrom: indigo
colorTo: purple
sdk: docker
pinned: false
---

# Fatigue Detection Backend - HF Space

Production backend for fatigue detection system deployed to Hugging Face Spaces.

## Features

- ✅ Real-time ML inference
- ✅ Automatic model loading from HF Hub
- ✅ WebSocket support for live streaming
- ✅ Sensor data processing (Arduino via tunnel)
- ✅ Comprehensive logging

## Configuration

Set these environment variables in HF Space Secrets:

```bash
# HF Hub Model Repositories
HF_FATIGUE_MODEL_REPO=your-username/fatigue-model
HF_VEHICLE_MODEL_REPO=your-username/vehicle-model
HF_TOKEN=hf_xxxxxxxxxxxxx  # Optional, for private repos

# Arduino Tunnel (from local machine)
ARDUINO_TUNNEL_URL=https://abc-123-xyz.ngrok.io

# Backend Configuration
FLASK_ENV=production
DEBUG=False
```

## API Endpoints

### Health Check
```bash
GET /api/health
```

### Predict
```bash
POST /api/predict
Content-Type: application/json

{
  "vision_data": {
    "ear": 0.3,
    "mar": 0.5,
    "perclos": 10,
    "head_angle_x": 5,
    "head_angle_y": 10
  },
  "sensor_data": {
    "hr": 75,
    "temperature": 36.5
  }
}
```

## Deployment Steps

1. **Create HF Space**
   - Name: `fatigue-backend`
   - SDK: Docker
   - Private: Yes (recommended)

2. **Upload Files**
   ```bash
   git clone https://huggingface.co/spaces/your-username/fatigue-backend
   cp -r backend_flask/* .
   git add .
   git commit -m "Deploy backend"
   git push
   ```

3. **Set Secrets** in HF Space Settings:
   - HF_FATIGUE_MODEL_REPO
   - HF_VEHICLE_MODEL_REPO
   - HF_TOKEN

4. **Get Space URL**: `https://your-username-fatigue-backend.hf.space`

## Local Arduino Bridge

To connect Arduino via tunnel:

```bash
# Terminal 1: Start Arduino bridge
python arduino_bridge.py

# Terminal 2: Create tunnel
ngrok http 5000
```

Then update backend configuration with tunnel URL.

## Monitoring

Check logs in HF Space for:
- Model loading status
- Prediction latency
- Error messages
- Request logs

## Troubleshooting

### Models not found
- Verify HF repository names
- Check HF_TOKEN for private repos

### Connection timeout
- Check Arduino bridge is running
- Verify tunnel URL in configuration
- Check network connectivity

### High latency
- Models are downloading first time (~1-2 min)
- Subsequent requests faster (~100-300ms)

---

See main project for full architecture documentation.
