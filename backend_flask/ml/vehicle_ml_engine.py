import os
import joblib
import numpy as np
import pandas as pd
from collections import deque
import time

class VehicleMLEngine:
    """
    Vehicle Fatigue Model - Vision-Only Sensors
    Uses only: Head Position, Camera, Perclos, Yawning
    NO psychological sensors (HR, Temperature, IMU)
    """
    def __init__(self, model_path="vehicle_fatigue_model.pkl", scaler_path=None, label_encoder_path=None):
        self.model = None
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.label_encoder_path = label_encoder_path
        self.scaler = None
        self.label_encoder = None
        self.use_xgb_pipeline = False
        self.labels = {0: "Alert", 1: "Drowsy", 2: "Fatigued"}
        
        # INDUSTRIAL UPGRADE: Feature Window
        self.window_size = 20  # WIDE window for smooth transitions
        self.history = deque(maxlen=self.window_size)
        
        # ADVANCED SMOOTHING: Exponential Moving Average (EMA)
        self.ema_probs = None 
        self.alpha = 0.15  # VERY LOW = Slow, smooth transitions
        
        # SAFETY CRITICAL: Microsleep Detection
        self.microsleep_max_frames = 10   # ~0.33s
        
        # STATE MACHINE: Hysteresis (Sticky States)
        self.current_state = 0  # Default Alert
        self.state_persistence = 0
        self.required_persistence = 5  # Frames to hold before switching
        
        self.debug_counter = 0

        # ROBUSTNESS: Adaptive Calibration
        self.base_ear = 0.32   # Dynamic baseline
        self.calibration_frames = 0
        self.max_calibration = 100  # Frames to learn 'Normal' EAR
        
        # Vision-only sensor data
        self.last_vision_values = {"ear": 0.3, "mar": 0}
        
        self.load_model()
    

    def load_model(self):
        """Loads the trained ML model from disk."""
        if not os.path.exists(self.model_path):
            print(f"[VehicleML] ⚠️ Model file not found at {self.model_path}.")
            return

        try:
            self.model = joblib.load(self.model_path)
            if self.scaler_path and os.path.exists(self.scaler_path):
                self.scaler = joblib.load(self.scaler_path)
            if self.label_encoder_path and os.path.exists(self.label_encoder_path):
                self.label_encoder = joblib.load(self.label_encoder_path)

            self.use_xgb_pipeline = self.scaler is not None
            if self.use_xgb_pipeline:
                print(f"[VehicleML] ✅ XGBoost pipeline loaded: {self.model_path}")
            else:
                print(f"[VehicleML] ✅ Legacy model loaded: {self.model_path}")
        except Exception as e:
            print(f"[VehicleML] ❌ Failed to load model: {e}")

    def reset_calibration(self):
        """Resets the adaptive baseline for a new user/session."""
        self.base_ear = 0.32
        self.calibration_frames = 0
        self.history.clear()
        self.ema_probs = None
        self.current_state = 0
        print("[VehicleML] 🔄 Calibration Reset!")

    def calculate_temporal_features(self, current_data):
        """
        Computes rolling mean/std from history.
        Vehicle model data: [ear, mar, pitch, yaw, roll]
        """
        self.history.append(current_data)
        data_matrix = np.array(self.history)
        
        if len(self.history) < 2:
            return {
                'ear_mean': current_data[0], 'ear_std': 0,
                'mar_mean': current_data[1], 'mar_std': 0,
                'pitch_mean': current_data[2], 'pitch_std': 0,
                'yaw_mean': current_data[3], 'yaw_std': 0,
                'roll_mean': current_data[4], 'roll_std': 0,
            }

        means = np.mean(data_matrix, axis=0)
        stds = np.std(data_matrix, axis=0)
        
        return {
            'ear_mean': means[0], 'ear_std': stds[0],
            'mar_mean': means[1], 'mar_std': stds[1],
            'pitch_mean': means[2], 'pitch_std': stds[2],
            'yaw_mean': means[3], 'yaw_std': stds[3],
            'roll_mean': means[4], 'roll_std': stds[4],
        }

    def _build_xgb_features(self, vision_data, sensor_data):
        ear = float(vision_data.get('ear', 0.3) or 0.3)
        mar = float(vision_data.get('mar', 0.0) or 0.0)
        pitch = float(vision_data.get('pitch', 0.0) or 0.0)
        yaw = float(vision_data.get('yaw', 0.0) or 0.0)
        roll = float(vision_data.get('roll', 0.0) or 0.0)
        perclos = float(vision_data.get('perclos', 0.0) or 0.0)

        # Keep scale consistent with training data (0-1 for PERCLOS)
        if perclos > 1.0:
            perclos = perclos / 100.0

        heart_rate = float(sensor_data.get('hr', 75.0) or 75.0)
        spo2 = float(sensor_data.get('spo2', 98.0) or 98.0)
        temperature = float(sensor_data.get('temperature', 37.0) or 37.0)

        # Lightweight imputation and clipping for real-time robustness
        heart_rate = float(np.clip(heart_rate, 40.0, 180.0))
        spo2 = float(np.clip(spo2, 80.0, 100.0))
        temperature = float(np.clip(temperature, 34.0, 41.0))

        eps = 1e-6
        ear_mar_ratio = ear / (mar + eps)
        perclos_blink_interaction = perclos * float(vision_data.get('blink_rate', 0.0) or 0.0)
        head_motion_sum = abs(pitch) + abs(yaw) + abs(roll)

        cols = [
            "EAR", "MAR", "PERCLOS", "blink_rate", "head_pitch", "head_yaw", "head_roll",
            "heart_rate", "spo2", "temperature", "ear_mar_ratio", "perclos_blink_interaction", "head_motion_sum"
        ]
        values = [
            ear, mar, perclos, float(vision_data.get('blink_rate', 0.0) or 0.0), pitch, yaw, roll,
            heart_rate, spo2, temperature, ear_mar_ratio, perclos_blink_interaction, head_motion_sum
        ]
        return pd.DataFrame([values], columns=cols)

    def predict(self, vision_data, sensor_data=None):
        """
        Vehicle Model Prediction - Vision Only
        
        Args:
            vision_data: {
                'ear': float,
                'mar': float,
                'pitch': float,
                'yaw': float,
                'roll': float,
                'perclos': float,
                'status': str
            }
        
        Returns:
            {
                'status': str,
                'confidence': float,
                'raw_probs': [p0, p1, p2],
                'microsleep_detected': bool
            }
        """
        if self.model is None:
            return {"status": "Unknown", "confidence": 0, "raw_probs": [0, 0, 0], "microsleep_detected": False}

        if sensor_data is None:
            sensor_data = {}

        # --- 0. VALIDITY CHECK (SAFETY FIRST) ---
        vision_status = vision_data.get("status", "Unknown")
        if vision_status in ["No Face", "Unstable"]:
            # If no face is visible, decay probability towards Alert
            if self.ema_probs is not None:
                self.ema_probs = self.ema_probs * 0.5 + np.array([1, 0, 0]) * 0.5
            else:
                self.ema_probs = np.array([1, 0, 0])
                
            return {
                "status": "No Face Detected",
                "confidence": 0.0,
                "raw_probs": self.ema_probs.tolist() if self.ema_probs is not None else [1, 0, 0],
                "microsleep_detected": False
            }

        # --- 1. EXTRACT VISION FEATURES ---
        ear = vision_data.get('ear', 0.3)
        mar = vision_data.get('mar', 0.0)
        pitch = vision_data.get('pitch', 0.0)
        yaw = vision_data.get('yaw', 0.0)
        roll = vision_data.get('roll', 0.0)
        perclos = vision_data.get('perclos', 0.0)
        perclos_ratio = perclos / 100.0 if perclos > 1.0 else perclos
        
        self.last_vision_values = {"ear": ear, "mar": mar}

        # --- 2. ADAPTIVE CALIBRATION ---
        # Personalize EAR threshold during first ~100 frames
        if self.calibration_frames < self.max_calibration and ear > 0.15:
            self.base_ear = (self.base_ear * self.calibration_frames + ear) / (self.calibration_frames + 1)
            self.calibration_frames += 1

        # Normalized EAR (relative to personal baseline)
        normalized_ear = ear / max(self.base_ear, 0.3)

        # --- 3. COMPOSE FEATURE VECTOR (VISION ONLY) ---
        current_features = np.array([
            normalized_ear,      # EAR (primary drowsiness indicator)
            mar,                 # MAR (yawning)
            pitch,               # Head Position - Pitch
            yaw,                 # Head Position - Yaw
            roll                 # Head Position - Roll
        ])

        # --- 4. TEMPORAL AGGREGATION ---
        temporal_features = self.calculate_temporal_features(current_features)

        # Assemble X for inference
        X = np.array([
            temporal_features['ear_mean'],
            temporal_features['ear_std'],
            temporal_features['mar_mean'],
            temporal_features['mar_std'],
            temporal_features['pitch_mean'],
            temporal_features['pitch_std'],
            temporal_features['yaw_mean'],
            temporal_features['yaw_std'],
            temporal_features['roll_mean'],
            temporal_features['roll_std'],
            perclos_ratio  # PERCLOS ratio
        ])

        # --- 5. ML INFERENCE ---
        try:
            if self.use_xgb_pipeline:
                xgb_df = self._build_xgb_features(vision_data, sensor_data)
                X_scaled = self.scaler.transform(xgb_df)
                probs = self.model.predict_proba(X_scaled)[0]
            else:
                probs = self.model.predict_proba([X])[0]
        except Exception as e:
            print(f"[VehicleML] Inference error: {e}")
            return {"status": "Error", "confidence": 0, "raw_probs": [0, 0, 0], "microsleep_detected": False}

        # --- 6. EXPONENTIAL MOVING AVERAGE (Smooth Transitions) ---
        if self.ema_probs is None:
            self.ema_probs = probs
        else:
            self.ema_probs = self.alpha * probs + (1 - self.alpha) * self.ema_probs

        # --- 7. STATE PERSISTENCE (Hysteresis) ---
        # Only switch states after `required_persistence` frames
        new_state = np.argmax(self.ema_probs)
        
        if new_state != self.current_state:
            self.state_persistence += 1
            if self.state_persistence >= self.required_persistence:
                self.current_state = new_state
                self.state_persistence = 0
        else:
            self.state_persistence = 0

        # --- 8. SAFETY: PERCLOS OVERRIDE ---
        # If PERCLOS > 55%, force "Fatigued" regardless of model output
        if perclos_ratio > 0.55:
            self.current_state = 2
            self.ema_probs = np.array([0, 0, 1])

        # --- 9. MICROSLEEP DETECTION ---
        # Triggered by sustained high PERCLOS and/or very low EAR
        microsleep_detected = False
        if (perclos_ratio > 0.80) or (ear < 0.15):
            microsleep_detected = True

        confidence = float(self.ema_probs[self.current_state])
        output_label = self.labels[self.current_state]
        if self.label_encoder is not None:
            try:
                decoded = self.label_encoder.inverse_transform([self.current_state])[0]
                output_label = self.labels.get(int(decoded), output_label)
            except Exception:
                pass

        return {
            "status": output_label,
            "confidence": round(confidence, 3),
            "raw_probs": [float(p) for p in self.ema_probs],
            "microsleep_detected": microsleep_detected
        }

    def get_debug_info(self):
        """Returns debug information for monitoring."""
        return {
            "model_loaded": self.model is not None,
            "calibration_progress": f"{min(self.calibration_frames, self.max_calibration)}/{self.max_calibration}",
            "base_ear": round(self.base_ear, 4),
            "current_state": self.labels.get(self.current_state, "Unknown"),
            "state_persistence": self.state_persistence,
            "window_size": len(self.history)
        }
