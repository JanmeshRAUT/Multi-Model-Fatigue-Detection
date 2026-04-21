#!/usr/bin/env python3
"""
Arduino Bridge for Cloud Deployment
=====================================

Reads Arduino sensor data locally and makes it available to cloud backend via HTTP.
This allows local Arduino to work with cloud-deployed backend.

Usage:
    python arduino_bridge.py

Then expose port 5000 with ngrok:
    ngrok http 5000

Set the ngrok URL as ARDUINO_TUNNEL_URL in HF Space backend.
"""

from flask import Flask, jsonify
import serial
import threading
import json
import os
import logging
from datetime import datetime

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
ARDUINO_PORT = os.environ.get("ARDUINO_PORT", "COM6")
BAUD_RATE = int(os.environ.get("BAUD_RATE", 115200))

# Global state
sensor_data = {
    "hr": 0,
    "temperature": 0,
    "spo2": 98,
    "timestamp": None,
    "status": "disconnected"
}
serial_lock = threading.Lock()

def parse_sensor_data(raw_line):
    """Parse sensor data from Arduino."""
    try:
        # Expected format: "HR:75,TEMP:36.5,SPO2:98"
        parts = raw_line.strip().split(',')
        data = {}
        for part in parts:
            if ':' in part:
                key, value = part.split(':')
                data[key.strip().lower()] = float(value.strip())
        return data
    except Exception as e:
        logger.error(f"Failed to parse sensor data: {e}")
        return None

def read_arduino():
    """Background thread: Read data from Arduino."""
    global sensor_data
    
    logger.info(f"🔌 Attempting to connect to Arduino on {ARDUINO_PORT}...")
    
    try:
        ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=2)
        logger.info(f"✅ Connected to Arduino on {ARDUINO_PORT}")
        
        with serial_lock:
            sensor_data['status'] = 'connected'
        
        while True:
            try:
                if ser.in_waiting > 0:
                    raw_line = ser.readline().decode('utf-8', errors='ignore')
                    parsed = parse_sensor_data(raw_line)
                    
                    if parsed:
                        with serial_lock:
                            sensor_data.update(parsed)
                            sensor_data['timestamp'] = datetime.now().isoformat()
                            sensor_data['status'] = 'connected'
                        
                        logger.debug(f"📊 Received: {parsed}")
            
            except Exception as e:
                logger.error(f"Error reading from Arduino: {e}")
                with serial_lock:
                    sensor_data['status'] = 'error'
    
    except Exception as e:
        logger.error(f"❌ Failed to connect to Arduino: {e}")
        logger.info("⚠️  Arduino will remain unavailable. Check port and baud rate.")
        with serial_lock:
            sensor_data['status'] = 'disconnected'

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "Arduino Bridge Running",
        "arduino_port": ARDUINO_PORT,
        "baud_rate": BAUD_RATE,
        "version": "1.0"
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    with serial_lock:
        status = sensor_data['status']
    
    return jsonify({
        "status": "ok",
        "arduino": status,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/sensor-data', methods=['GET'])
def get_sensor_data():
    """Get latest sensor data from Arduino."""
    with serial_lock:
        data = sensor_data.copy()
    
    return jsonify(data)

@app.route('/heartrate', methods=['GET'])
def get_heartrate():
    """Get heart rate only."""
    with serial_lock:
        hr = sensor_data['hr']
    
    return jsonify({"heart_rate": hr})

@app.route('/temperature', methods=['GET'])
def get_temperature():
    """Get temperature only."""
    with serial_lock:
        temp = sensor_data['temperature']
    
    return jsonify({"temperature": temp})

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": [
            "GET /",
            "GET /health",
            "GET /sensor-data",
            "GET /heartrate",
            "GET /temperature"
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": str(error)}), 500

def main():
    """Start Arduino bridge server."""
    logger.info("=" * 60)
    logger.info("🚀 Arduino Bridge for Cloud Deployment")
    logger.info("=" * 60)
    logger.info(f"ARDUINO_PORT: {ARDUINO_PORT}")
    logger.info(f"BAUD_RATE: {BAUD_RATE}")
    
    # Start Arduino reading thread
    arduino_thread = threading.Thread(target=read_arduino, daemon=True)
    arduino_thread.start()
    logger.info("📡 Arduino reader thread started")
    
    logger.info("\n🌐 Exposing bridge with ngrok:")
    logger.info("   ngrok http 5000")
    logger.info("\n📋 Then update HF Space with tunnel URL:")
    logger.info("   ARDUINO_TUNNEL_URL=https://your-ngrok-url.ngrok.io")
    logger.info("\n✅ Server ready!")
    logger.info("=" * 60 + "\n")
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    main()
