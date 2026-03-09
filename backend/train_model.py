
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# 1. SETUP
# Points to the RICH features dataset (~40MB)
DATA_FILE = r"e:\Fullstack\ml_model\Dataset.csv"
# Start a new version to preserve the old model
MODEL_FILE = "ml/models/fatigue_model_v2.pkl" 
WINDOW_SIZE = 20  # Matches MLEngine window

print(f"Loading data from {DATA_FILE}...")
try:
    df = pd.read_csv(DATA_FILE)
except FileNotFoundError:
    print(f"❌ {DATA_FILE} not found!")
    exit()

# 2. PREPROCESSING
print("Preprocessing & Label Encoding...")

# Map Text Labels to Numbers if 'condition' exists
if 'condition' in df.columns:
    label_map = {'Alert': 0, 'Drowsy': 1, 'Fatigue': 2}
    # Filter out any labels not in our map (safety)
    df = df[df['condition'].isin(label_map.keys())].copy()
    df['fatigue_label'] = df['condition'].map(label_map)
    print(f"✅ Mapped labels: {label_map}")
else:
    # Fallback to existing label if 'condition' missing
    if 'fatigue_label' not in df.columns:
        print("❌ No 'condition' or 'fatigue_label' column found.")
        exit()

# Sort by session/timestamp to ensure rolling window works correctly
# Using 'timestamp' or index if timestamp is string
if 'timestamp' in df.columns:
    df = df.sort_values(by=['session_id', 'timestamp'])

# 3. FEATURE ENGINEERING (Calculate Rolling Stats)
print("Generating temporal features (Rolling statistics)...")

# Features available in the new Dataset.csv
# We include 'head_roll' and 'blink_rate' which were missing in v1
base_features = ['ear', 'mar', 'head_pitch', 'head_yaw', 'head_roll', 'curr_blink_rate', 'hr', 'temperature']

# Rename 'blink_rate' -> 'curr_blink_rate' if necessary or just use it
# Check if 'blink_rate' exists
if 'blink_rate' in df.columns:
    base_features = [f if f != 'curr_blink_rate' else 'blink_rate' for f in base_features]
else:
    # If generic blink rate missing, remove it from base
    if 'curr_blink_rate' in base_features:
        base_features.remove('curr_blink_rate')

if 'head_roll' not in df.columns:
    print("⚠️ 'head_roll' missing in dataset, skipping.")
    base_features.remove('head_roll')

print(f"Base Features for Rolling: {base_features}")

for col in base_features:
    # Rolling Mean & Std
    df[f'{col}_mean'] = df.groupby('session_id')[col].transform(lambda x: x.rolling(window=WINDOW_SIZE, min_periods=1).mean())
    df[f'{col}_std'] = df.groupby('session_id')[col].transform(lambda x: x.rolling(window=WINDOW_SIZE, min_periods=1).std())

df = df.fillna(0)

# 4. DEFINE FEATURE VECTOR
# This must match what MLEngine v2 expects
features = [
    'perclos', 
    'ear_mean', 'ear_std', 
    'mar_mean', 'mar_std', 
    'head_pitch_mean', 'head_pitch_std',
    'head_yaw_mean', 'head_yaw_std',
    'head_roll_mean', 'head_roll_std',
    'blink_rate_mean', 'blink_rate_std',  # Added missing blink features
    'hr_mean', 'hr_std',
    'temperature_mean'
]

# Provide fallback if cols filter failed
features = [f for f in features if f in df.columns]

target = 'fatigue_label'

print(f"Final Feature Vector ({len(features)}): {features}")

X = df[features]
y = df[target]

# 5. TRAINING
print("Training V2 Random Forest (Rich Dataset)...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

model = RandomForestClassifier(n_estimators=300, max_depth=20, random_state=42, class_weight='balanced')
model.fit(X_train, y_train)

# 6. EVALUATION
preds = model.predict(X_test)
acc = accuracy_score(y_test, preds)
print(f"✅ Accuracy using New Dataset: {acc:.4f}")
print("\nClassification Report:\n", classification_report(y_test, preds))

# 7. SAVE without overwriting old model
joblib.dump(model, MODEL_FILE)
print(f"✅ V2 Model saved to {MODEL_FILE}")
print(f"⚠️ NOTE: You must update 'ml_engine.py' to use this new file and feature vector.")
