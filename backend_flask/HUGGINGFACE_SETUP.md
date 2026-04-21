# Hugging Face Integration Guide

This backend now supports loading ML models from Hugging Face Hub with automatic fallback to local models.

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

This includes:
- `huggingface-hub` - For downloading models from HF Hub
- `xgboost` - Required for vehicle model inference
- `joblib` - For model serialization

### 2. Configure Environment Variables

Set these in your `.env` file or system environment:

```bash
# Hugging Face Repository Information
HF_FATIGUE_MODEL_REPO="your-username/fatigue-model"      # e.g., "janmesh/fatigue-model"
HF_VEHICLE_MODEL_REPO="your-username/vehicle-model"      # e.g., "janmesh/vehicle-model"

# Optional: HF Token (for private repositories)
HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxx"
```

### 3. Prepare HF Hub Repositories

Your Hugging Face repositories should contain:

**For Fatigue Model (HF_FATIGUE_MODEL_REPO):**
- `fatigue_model.pkl` - The trained fatigue detection model

**For Vehicle Model (HF_VEHICLE_MODEL_REPO):**
- `xgboost_independent.joblib` - The XGBoost vehicle model
- `xgb_scaler.joblib` - Feature scaler (optional)
- `xgb_label_encoder.joblib` - Label encoder (optional)

### 4. Model Loading Priority

The backend follows this priority:

1. **Hugging Face Hub** (if `HF_*_MODEL_REPO` is configured)
   - Automatically downloads from the specified repository
   - Useful for cloud deployment and model versioning
   
2. **Local Fallback** (if HF loading fails or repo not configured)
   - Uses local model files in `ml/models/` directory
   - Ensures zero downtime if HF is unavailable

### 5. Running the Backend

```bash
# Set environment variables (Windows PowerShell)
$env:HF_FATIGUE_MODEL_REPO = "your-username/fatigue-model"
$env:HF_VEHICLE_MODEL_REPO = "your-username/vehicle-model"

# Start the Flask server
python app.py
```

Or using `.env` file:
```bash
# Create .env file with your config
python -m python-dotenv && python app.py
```

## Monitoring Model Source

When the backend starts, check the logs to see which models are loaded:

```
[ML] 🌐 Attempting to load from Hugging Face Hub: janmesh/fatigue-model
[ML] ✅ Model loaded successfully from Hugging Face Hub: janmesh/fatigue-model

[VehicleML] 🌐 Attempting to load from Hugging Face Hub: janmesh/vehicle-model
[VehicleML] ✅ Model loaded successfully from Hugging Face Hub: janmesh/vehicle-model
```

Or if falling back to local:
```
[ML] 🔄 Falling back to local model at ./ml/models/fatigue_model.pkl
[ML] ✅ Model loaded successfully from local path: ./ml/models/fatigue_model.pkl
```

## API Health Check

To verify which models are loaded, use the health endpoint:

```bash
curl http://localhost:5000/api/health
```

The response will include model source information.

## Troubleshooting

### HF Download Fails
- **Issue**: `huggingface_hub not installed`
  - **Solution**: Run `pip install huggingface-hub`

- **Issue**: `Repository not found`
  - **Solution**: Verify the repository name matches your HF Hub account

- **Issue**: `403 Forbidden` for private repos
  - **Solution**: Set `HF_TOKEN` environment variable with a valid token

### Local Models Not Found
- **Issue**: `Model file not found`
  - **Solution**: Ensure model files exist in `backend_flask/ml/models/` directory

## Best Practices

1. **Version Control**: Use HF Hub for versioning different model iterations
2. **Private Repos**: Use private HF repositories for proprietary models
3. **Bandwidth**: First load downloads ~50-200MB; subsequent loads use cache
4. **Fallback**: Always keep local models as backup
5. **Updates**: Update `HF_TOKEN` if repository permissions change

## Example Configuration

```bash
# .env file
HF_FATIGUE_MODEL_REPO=janmesh/fatigue-detection-v2
HF_VEHICLE_MODEL_REPO=janmesh/vehicle-drowsiness-v1
HF_TOKEN=hf_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
ARDUINO_PORT=COM6
BAUD_RATE=115200
DEBUG=True
```

## Support

For issues with Hugging Face integration:
- Check HF Hub repository: https://huggingface.co/your-username
- Review model file structure in the repository
- Ensure `xgboost` and `joblib` versions are compatible
