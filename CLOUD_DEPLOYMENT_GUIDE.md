# Complete Cloud Deployment Guide
# Vercel + HF Space + Arduino Tunnel

This guide covers deploying your fatigue detection system fully to the cloud with local Arduino integration.

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         CLOUD                                    │
│                                                                  │
│  ┌─────────────────────────────┐   ┌──────────────────────────┐ │
│  │  Vercel Frontend ☁️          │   │  HF Space Backend ☁️    │ │
│  │  your-app.vercel.app        │◄─►│  backend.hf.space       │ │
│  │  • React app                │   │  • ML inference         │ │
│  │  • Dashboard UI             │   │  • Model loading        │ │
│  │  • Real-time charts         │   │  • Sensor processing    │ │
│  └─────────────────────────────┘   └──────────────────────────┘ │
│                                            ▲                     │
└────────────────────────────────────────────┼─────────────────────┘
                                             │
                                   ngrok tunnel HTTPS
                                             │
┌────────────────────────────────────────────┼─────────────────────┐
│                    LOCAL MACHINE                                  │
│                                             ▼                     │
│  ┌──────────────────────────────────────────────────┐           │
│  │  Arduino Bridge 🖥️  (arduino_bridge.py)         │           │
│  │  • Flask server port 5000                        │           │
│  │  • Reads Arduino USB data                        │           │
│  │  • Exposes /sensor-data endpoint                │           │
│  └──────────────────┬───────────────────────────────┘           │
│                     │ USB                                        │
│  ┌──────────────────▼───────────────────────────────┐           │
│  │  Arduino 🔌                                      │           │
│  │  • Heart Rate sensor                            │           │
│  │  • Temperature sensor                           │           │
│  │  • Other sensors (customizable)                 │           │
│  └─────────────────────────────────────────────────┘           │
└──────────────────────────────────────────────────────────────────┘
```

---

## Part 1: Frontend on Vercel

### 1.1 Prepare Frontend

Update `frontend/.env.production`:
```bash
REACT_APP_API_URL=https://your-username-fatigue-backend.hf.space
GENERATE_SOURCEMAPS=false
```

### 1.2 Deploy to Vercel

**Option A: GitHub Integration**
```bash
# 1. Push to GitHub
cd frontend
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main

# 2. Go to vercel.com
# 3. Import from GitHub
# 4. Set environment variables in Vercel dashboard
# 5. Deploy!
```

**Option B: Vercel CLI**
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod

# Your frontend URL: your-app.vercel.app
```

### 1.3 Verify Frontend
```bash
curl https://your-app.vercel.app
# Should return HTML of React app
```

---

## Part 2: Backend on HF Space

### 2.1 Create HF Space Repository

Go to [huggingface.co/spaces](https://huggingface.co/spaces):
- Click "Create new Space"
- **Space name**: `fatigue-backend`
- **License**: MIT
- **SDK**: Docker
- **Visibility**: Private (recommended)

Get your space URL format:
```
https://your-username-fatigue-backend.hf.space
```

### 2.2 Upload Backend Files

```bash
# Clone your HF Space repo
git clone https://huggingface.co/spaces/your-username/fatigue-backend
cd fatigue-backend

# Copy backend_flask files
cp -r ../backend_flask/* .

# Push to HF
git add .
git commit -m "Deploy fatigue backend to HF Space"
git push
```

### 2.3 Set HF Space Secrets

In HF Space → Settings → Repository secrets, add:

```
HF_FATIGUE_MODEL_REPO = your-username/fatigue-model
HF_VEHICLE_MODEL_REPO = your-username/vehicle-model
HF_TOKEN = hf_xxxxxxxxxxxxx (if private)
ARDUINO_TUNNEL_URL = (will update after ngrok setup)
```

### 2.4 Wait for Deployment

HF Space automatically builds Docker image (3-5 min). Check logs for:
```
✅ Model loaded successfully from Hugging Face Hub
✅ Vehicle ML Engine initialized
```

---

## Part 3: Arduino Bridge & Tunnel

### 3.1 Install Dependencies

```bash
cd e:\Fullstack
pip install flask pyserial python-dotenv
```

### 3.2 Start Arduino Bridge

**Terminal 1:**
```bash
python arduino_bridge.py

# Output:
# 🔌 Attempting to connect to Arduino on COM6...
# ✅ Connected to Arduino on COM6
# 📡 Arduino reader thread started
# ✅ Server ready!
```

### 3.3 Create ngrok Tunnel

**Terminal 2:**
```bash
# Install ngrok (if not already done)
ngrok config add-authtoken YOUR_AUTH_TOKEN

# Start tunnel
ngrok http 5000

# Output:
# Forwarding     https://abc-123-xyz.ngrok.io -> http://localhost:5000
# Copy the HTTPS URL above
```

### 3.4 Update HF Space with Tunnel URL

In HF Space Settings → Secrets:
```
ARDUINO_TUNNEL_URL = https://abc-123-xyz.ngrok.io
```

Redeploy HF Space for it to pick up the new URL.

---

## Part 4: Connect Frontend to Backend

### 4.1 Update Frontend API URL

Create `frontend/.env.production`:
```bash
REACT_APP_API_URL=https://your-username-fatigue-backend.hf.space
```

Or hardcode in `frontend/src/api.js`:
```javascript
const API_BASE = "https://your-username-fatigue-backend.hf.space";

export const predict = async (data) => {
  const response = await fetch(`${API_BASE}/api/predict`, {
    method: 'POST',
    body: JSON.stringify(data),
    headers: { 'Content-Type': 'application/json' }
  });
  return response.json();
};
```

### 4.2 Rebuild and Deploy Frontend

```bash
cd frontend
npm run build
vercel --prod
```

---

## Part 5: Testing

### 5.1 Test Arduino Bridge

```bash
# Check if bridge is running
curl http://localhost:5000
# Output: {"status": "Arduino Bridge Running", ...}

# Get sensor data
curl http://localhost:5000/sensor-data
# Output: {"hr": 75, "temperature": 36.5, "status": "connected"}
```

### 5.2 Test HF Space Backend

```bash
# Health check
curl https://your-username-fatigue-backend.hf.space/api/health
# Output: {"status": "ok", "timestamp": "..."}

# Make prediction
curl -X POST https://your-username-fatigue-backend.hf.space/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "vision_data": {
      "ear": 0.3,
      "perclos": 10,
      "head_angle_x": 5
    },
    "sensor_data": {
      "hr": 75,
      "temperature": 36.5
    }
  }'
```

### 5.3 Test Full Integration

1. Open `https://your-app.vercel.app` in browser
2. Dashboard should load
3. Start Arduino and bridge
4. Check if real-time data flows
5. See predictions updating

---

## Troubleshooting

### Frontend won't connect
```bash
# Check backend URL in browser console
# Should be https://your-username-fatigue-backend.hf.space

# Test with curl
curl https://your-username-fatigue-backend.hf.space/api/health
```

### Arduino bridge not connecting
```bash
# Check port and baud rate
python arduino_bridge.py

# Should see: ✅ Connected to Arduino on COM6
# If not, update ARDUINO_PORT environment variable
```

### ngrok tunnel keeps changing URL
```bash
# Use paid ngrok account for static URLs
# Or restart bridge/tunnel each time and update HF Space secret
```

### Models not loading in HF Space
```bash
# Check HF Space logs for errors
# Verify HF_FATIGUE_MODEL_REPO and HF_VEHICLE_MODEL_REPO are set
# Check HF_TOKEN is correct for private repos
```

### High latency (>2 seconds)
```bash
# First prediction downloads models (~1-2 min)
# Subsequent predictions should be <300ms
# Check network connectivity
```

---

## Monitoring & Logging

### HF Space Logs
- Check HF Space → Logs tab to see:
  - Model loading status
  - Prediction logs
  - Error messages
  - Request latency

### Arduino Bridge Logs
- Terminal output shows:
  - Arduino connection status
  - Sensor readings
  - Parse errors

### Frontend Errors
- Browser Console (F12) shows:
  - API call failures
  - Network errors
  - JavaScript errors

---

## Maintenance

### Daily
- Check Arduino bridge is running
- Verify tunnel is active
- Monitor HF Space logs

### Weekly
- Check model cache sizes
- Review error logs
- Update dependencies

### Monthly
- Retrain models if needed
- Update backend code
- Monitor API latency metrics

---

## Security Notes

⚠️ **Keep These Private:**
- HF_TOKEN
- Arduino connection string
- ngrok auth token

✅ **Best Practices:**
- Use private HF Space for backend
- Don't commit .env files
- Rotate ngrok token periodically
- Monitor access logs

---

## Complete Checklist

- [ ] Frontend deployed to Vercel
- [ ] Backend deployed to HF Space
- [ ] Models uploaded to HF Hub
- [ ] HF Space secrets configured
- [ ] Arduino bridge running locally
- [ ] ngrok tunnel active
- [ ] Frontend updated with backend URL
- [ ] All connections tested
- [ ] Predictions flowing end-to-end
- [ ] Logs monitored and clear

---

## Project URLs

Once deployed:

| Component | URL |
|-----------|-----|
| **Frontend** | `https://your-app.vercel.app` |
| **Backend** | `https://your-username-fatigue-backend.hf.space` |
| **Arduino Bridge** | `http://localhost:5000` (local only) |
| **ngrok Tunnel** | `https://abc-123-xyz.ngrok.io` (temporary) |
| **Models (HF Hub)** | `https://huggingface.co/your-username/fatigue-model` |

---

## Next Steps

After successful deployment:

1. **Monitor Performance**
   - Track latency metrics
   - Monitor error rates
   - Check model accuracy

2. **Scale Up**
   - Consider upgrading Vercel plan
   - Upgrade HF Space to faster GPU
   - Add caching layer

3. **Add Features**
   - Database for historical data
   - User authentication
   - Analytics dashboard
   - Mobile app

4. **Continuous Deployment**
   - Set up GitHub Actions CI/CD
   - Auto-deploy on commit
   - Run tests before deployment

---

For questions, check the individual README files:
- `frontend/README.md` - Frontend setup
- `backend_flask/README_HF_SPACE.md` - Backend on HF Space
- `backend_flask/HUGGINGFACE_SETUP.md` - HF Hub integration
