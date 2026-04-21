# Quick Deployment Reference
## Vercel → HF Space → Arduino Tunnel

### Quick Setup (5 minutes to live)

#### 1️⃣ Frontend → Vercel (2 min)
```bash
# Update env
echo "REACT_APP_API_URL=https://your-username-fatigue-backend.hf.space" > frontend/.env.production

# Deploy
cd frontend
vercel --prod

# Get URL: your-app.vercel.app
```

#### 2️⃣ Backend → HF Space (2 min)
```bash
# Create space at huggingface.co/spaces
# Name: fatigue-backend, SDK: Docker

# Upload files
git clone https://huggingface.co/spaces/your-username/fatigue-backend
cp -r backend_flask/* ./
git add . && git commit -m "Deploy" && git push

# Set secrets in HF Space:
# HF_FATIGUE_MODEL_REPO = your-username/fatigue-model
# HF_VEHICLE_MODEL_REPO = your-username/vehicle-model
# HF_TOKEN = hf_xxxxx (if private)
```

#### 3️⃣ Arduino Bridge → Tunnel (1 min)
```bash
# Terminal 1: Start bridge
python arduino_bridge.py

# Terminal 2: Create tunnel
ngrok http 5000

# Copy HTTPS URL from ngrok output
# Set in HF Space: ARDUINO_TUNNEL_URL = https://abc-123-xyz.ngrok.io
```

---

### Testing

```bash
# Test bridge
curl http://localhost:5000/sensor-data

# Test backend
curl https://your-username-fatigue-backend.hf.space/api/health

# Test frontend
open https://your-app.vercel.app
```

---

### Environment Variables Summary

**Frontend (.env.production)**
```
REACT_APP_API_URL=https://your-username-fatigue-backend.hf.space
```

**HF Space Secrets**
```
HF_FATIGUE_MODEL_REPO=your-username/fatigue-model
HF_VEHICLE_MODEL_REPO=your-username/vehicle-model
HF_TOKEN=hf_xxxxxxxxxxxxx
ARDUINO_TUNNEL_URL=https://abc-123-xyz.ngrok.io
```

**Arduino Bridge (.env)**
```
ARDUINO_PORT=COM6
BAUD_RATE=115200
```

---

### Key Files

| File | Purpose |
|------|---------|
| `frontend/vercel.json` | Vercel config |
| `backend_flask/Dockerfile.hf` | HF Space docker |
| `backend_flask/README_HF_SPACE.md` | HF Space docs |
| `arduino_bridge.py` | Local Arduino bridge |
| `CLOUD_DEPLOYMENT_GUIDE.md` | Full guide |

---

### Troubleshooting Checklist

- [ ] Frontend loads at vercel.app URL
- [ ] Backend responds to /api/health
- [ ] Arduino bridge shows connected status
- [ ] ngrok tunnel shows forwarding
- [ ] Frontend can call backend API
- [ ] Sensor data flowing from Arduino
- [ ] Predictions returning successfully

---

### URLs After Deployment

```
Frontend:    https://your-app.vercel.app
Backend:     https://your-username-fatigue-backend.hf.space
Bridge:      http://localhost:5000
Tunnel:      https://abc-123-xyz.ngrok.io
```

---

### Daily Operation

```bash
# Start Arduino bridge
python arduino_bridge.py

# Start ngrok tunnel (keep running)
ngrok http 5000

# Frontend auto-updates from Vercel
# Backend auto-updates on git push to HF Space
```

---

For complete details, see: `CLOUD_DEPLOYMENT_GUIDE.md`
