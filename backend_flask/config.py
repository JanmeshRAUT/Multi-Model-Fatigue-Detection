import os

class Config:
    """
    Central Configuration for the Backend Application
    """
    
    # --- Serial / Sensor Configuration ---
    # Defaulting to COM6 as per recent user diagnostics, but serial_reader will also auto-detect.
    ARDUINO_PORT = os.environ.get("ARDUINO_PORT", "COM6") 
    BAUD_RATE = int(os.environ.get("BAUD_RATE", 115200))
    MAX_HISTORY = 100 # Number of sensor readings to keep in memory
    SENSOR_TIMEOUT = 2.0 # Seconds before sensor data is considered "Stale"
    USE_MOCK_DATA = False # Set to True to enable random data generation when sensors are disconnected
    
    # --- ML Engine Configuration ---
    # Local model paths (fallback)
    MODEL_PATH = os.path.join(os.path.dirname(__file__), "ml", "models", "fatigue_model.pkl")
    LEGACY_VEHICLE_MODEL_PATH = os.path.join(os.path.dirname(__file__), "ml", "models", "vehicle_fatigue_model.pkl")
    VEHICLE_MODEL_PATH = os.path.join(os.path.dirname(__file__), "ml", "models", "xgboost_independent.joblib")
    VEHICLE_SCALER_PATH = os.path.join(os.path.dirname(__file__), "ml", "models", "xgb_scaler.joblib")
    VEHICLE_LABEL_ENCODER_PATH = os.path.join(os.path.dirname(__file__), "ml", "models", "xgb_label_encoder.joblib")
    
    # Hugging Face model repositories (primary)
    HF_FATIGUE_MODEL_REPO = os.environ.get("HF_FATIGUE_MODEL_REPO", "")
    HF_VEHICLE_MODEL_REPO = os.environ.get("HF_VEHICLE_MODEL_REPO", "")
    HF_SCALER_FILENAME = "xgb_scaler.joblib"
    HF_LABEL_ENCODER_FILENAME = "xgb_label_encoder.joblib"
    HF_VEHICLE_MODEL_FILENAME = "xgboost_independent.joblib"
    HF_TOKEN = os.environ.get("HF_TOKEN", None)  # For private repos
    
    # Hugging Face Inference API (primary for inference)
    HF_API_TOKEN = os.environ.get("HF_API_TOKEN", HF_TOKEN)  # API token for inference
    USE_HF_INFERENCE_API = os.environ.get("USE_HF_INFERENCE_API", "True").lower() == "true"
    
    ML_INTERVAL = 0.5 # Seconds between ML predictions to prevent CPU overload
    
    # --- Logging / Debug ---
    DEBUG = True

def get_config():
    return Config()
