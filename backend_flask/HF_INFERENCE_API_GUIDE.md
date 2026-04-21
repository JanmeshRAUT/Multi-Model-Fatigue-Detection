# HF Inference API + Local Fallback Pattern
## Complete Guide

Your system now uses **Hugging Face Inference API as primary** with **local model fallback** for robust predictions.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Vercel/Local)                  │
│                   Sends prediction request                  │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTPS
                 ↓
┌─────────────────────────────────────────────────────────────┐
│                  Backend (HF Space/Local)                   │
│                                                             │
│  ┌──────────────────────────────────────────────┐          │
│  │  MLEngine / VehicleMLEngine                  │          │
│  │                                              │          │
│  │  1️⃣  Try HF Inference API                   │          │
│  │      ├─ API_URL                             │          │
│  │      ├─ HF_API_TOKEN                        │          │
│  │      └─ Timeout: 10 seconds                 │          │
│  │         Success? ✅ Return probs             │          │
│  │         Timeout? ⏱️  Fall back               │          │
│  │         Error? ❌ Fall back                  │          │
│  │                                              │          │
│  │  2️⃣  Fallback to Local Model (if API fails) │          │
│  │      ├─ Load from HF Hub (cached)           │          │
│  │      ├─ Or load from local file             │          │
│  │      └─ Return predictions                  │          │
│  │                                              │          │
│  │  3️⃣  EMA Smoothing + State Machine          │          │
│  │      └─ Return final status                 │          │
│  └──────────────────────────────────────────────┘          │
│                                                             │
└────────────────┬────────────────────────────────────────────┘
                 │ Response with prediction
                 ↓
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Display result)                │
└─────────────────────────────────────────────────────────────┘
```

---

## Configuration

### 1. **Enable/Disable HF Inference API**

In `.env`:
```bash
# Use HF Inference API first
USE_HF_INFERENCE_API=True

# Your HF API token (from https://huggingface.co/settings/tokens)
HF_API_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx
```

### 2. **Fallback Strategy**

If HF Inference API:
- ✅ **Success** → Returns predictions immediately (~200-500ms)
- ⏱️ **Timeout** (>10s) → Falls back to local model
- ❌ **Error** (invalid token, 403, etc.) → Falls back to local model
- 🔌 **No token** → Skips API, uses local model

Local models:
1. Try to download from **HF Hub** (cached after first run)
2. Fall back to **local files** if download fails
3. Use **EMA smoothing + state machine** for stable predictions

---

## Performance Comparison

### HF Inference API (Primary)
| Metric | Value |
|--------|-------|
| **Latency** | 200-500ms |
| **Cost** | Free tier (rate limited) / Paid |
| **Uptime** | 99.9% (HF infrastructure) |
| **No local resource** | ✅ Yes |
| **Scaling** | Automatic (cloud) |

### Local Models (Fallback)
| Metric | Value |
|--------|-------|
| **Latency** | 100-300ms |
| **Cost** | $0 (no API calls) |
| **Uptime** | 100% (your machine) |
| **Local resource** | CPU usage |
| **Scaling** | Limited to machine |

---

## Usage Examples

### Example 1: API Succeeds
```
Request → API call (200ms) → Predictions returned
         ✅ "Inference source: HF Inference API"
```

### Example 2: API Times Out
```
Request → API call (10s timeout)
         ⏱️  No response → Local model
         (50ms) → Predictions returned
         ⚠️ "Inference source: Local:fatigue_model.pkl"
```

### Example 3: API Disabled
```
Request → Skip API (USE_HF_INFERENCE_API=False)
       → Local model directly
       (100ms) → Predictions returned
       ℹ️ "Inference source: Local:fatigue_model.pkl"
```

### Example 4: No Token
```
Request → Check HF_API_TOKEN (empty/None)
       → Skip API automatically
       → Local model
       (100ms) → Predictions returned
       ℹ️ "Inference source: Local:fatigue_model.pkl"
```

---

## Response Format

### Standard Response
```json
{
  "status": "Drowsy",
  "confidence": 0.75,
  "raw_probs": [0.15, 0.75, 0.10],
  "inference_source": "HF Inference API",
  "timestamp": "2026-04-20T14:30:45.123Z"
}
```

### With Fallback
```json
{
  "status": "Drowsy",
  "confidence": 0.72,
  "raw_probs": [0.18, 0.72, 0.10],
  "inference_source": "Local:fatigue_model.pkl",
  "note": "API timeout - using fallback model"
}
```

---

## Step-by-Step Setup

### Step 1: Get HF API Token

1. Go to https://huggingface.co/settings/tokens
2. Click "New token"
3. Name: `fatigue-api`
4. Type: `read`
5. Copy token

### Step 2: Set Environment Variables

**Local development:**
```bash
# In .env or system environment
HF_API_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx
USE_HF_INFERENCE_API=True
HF_FATIGUE_MODEL_REPO=your-username/fatigue-model
HF_VEHICLE_MODEL_REPO=your-username/vehicle-model
```

**HF Space deployment:**
```
Settings → Secrets → Add:
HF_API_TOKEN = hf_xxxxxxxxxxxxxxxxxxxxx
USE_HF_INFERENCE_API = True
HF_FATIGUE_MODEL_REPO = your-username/fatigue-model
HF_VEHICLE_MODEL_REPO = your-username/vehicle-model
```

**Vercel frontend:**
```
Settings → Environment Variables → Add:
HF_API_TOKEN = hf_xxxxxxxxxxxxxxxxxxxxx (if needed)
```

### Step 3: Test the Integration

```bash
# Test local backend
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "vision_data": {"ear": 0.3, "perclos": 10},
    "sensor_data": {"hr": 75, "temperature": 36.5}
  }'

# Should return with "inference_source"
```

### Step 4: Monitor Logs

Look for logs:
```
[ML] ✅ Prediction from HF Inference API       # API worked
[ML] ⚠️ API timeout, falling back to local     # API timeout
[ML] ⚠️ API call failed: ..., falling back     # API error
[ML] ✅ Prediction from local model            # Using fallback
```

---

## Troubleshooting

### Problem: API never gets called

**Check:**
```bash
# 1. Is HF_API_TOKEN set?
echo $HF_API_TOKEN

# 2. Is USE_HF_INFERENCE_API=True?
grep USE_HF_INFERENCE_API .env

# 3. Check backend logs for:
# "[ML] 🌐 Calling HF Inference API"
```

**Solution:**
- Set `HF_API_TOKEN=hf_xxxxx` in `.env`
- Ensure `USE_HF_INFERENCE_API=True`
- Restart backend

### Problem: Always falls back to local

**Possible causes:**
1. **Invalid token** → Check token at https://huggingface.co/settings/tokens
2. **API endpoint wrong** → Verify URL in code
3. **Network timeout** → Check internet connection
4. **Rate limited** → Wait or upgrade HF account

**Debug:**
```bash
# Test token directly
curl -H "Authorization: Bearer $HF_API_TOKEN" \
  https://huggingface.co/api/whoami

# Should return: {"name": "your-username"}
```

### Problem: Local model loads slowly

**Solution:**
- First prediction: ~2-5 seconds (downloads from HF Hub)
- Subsequent: ~100-300ms (uses cache)
- Cache location: `~/.cache/huggingface/`

---

## Cost Considerations

### Free Tier (HF Inference API)
- ✅ 30k API calls/month
- ✅ No billing required
- ⚠️ Rate limited (1 request/10 seconds)

### Paid Tier (HF Pro)
- ✅ Unlimited API calls
- ✅ Faster inference
- 💰 $9/month

### Local Models (No API)
- ✅ $0 cost
- ⚠️ CPU usage on your machine
- ✅ 100% uptime

**Recommendation:**
- **Development**: Use API for testing, local as fallback
- **Production**: Use local models (no API cost)
- **High volume**: Upgrade HF Pro or use local only

---

## Best Practices

### 1. Always Have Fallback
```python
# ✅ Good
result = try_api() or use_local_model()

# ❌ Bad
result = try_api()  # Fails if API down
```

### 2. Monitor Inference Source
```python
# Log which method was used
print(f"Inference from: {result['inference_source']}")
# Helps identify API issues

# Track metrics:
# - API success rate
# - API latency
# - Fallback frequency
```

### 3. Set Appropriate Timeout
```python
# Current: 10 seconds
# Good for: Most use cases
# Too low: < 5s → Too aggressive fallback
# Too high: > 15s → User perceives slowness
```

### 4. Handle Token Rotation
```bash
# If token expires:
# 1. Get new token from HF
# 2. Update HF_API_TOKEN
# 3. Restart backend
# 4. System automatically falls back if token invalid
```

---

## Advanced: Custom API Endpoints

You can modify the API URLs for different models:

```python
# In ml_engine.py
API_URL = "https://api-inference.huggingface.co/models/YOUR_MODEL"

# Or use custom endpoints:
API_URL = os.environ.get("CUSTOM_API_URL", default_url)
```

---

## Summary

| Component | Primary | Fallback |
|-----------|---------|----------|
| **Predictions** | HF Inference API | Local models |
| **Models** | Downloaded/cached | Local files |
| **Configuration** | `HF_API_TOKEN` | Local path |
| **Latency** | ~300ms | ~150ms |
| **Cost** | Free (limited) | $0 |
| **Uptime** | 99.9% | 100% |

**Result:** ✅ Robust, scalable, cost-effective predictions!

---

For questions or issues, check logs for `[ML]` prefix messages.
