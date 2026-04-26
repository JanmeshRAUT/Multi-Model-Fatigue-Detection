import serial
import serial.tools.list_ports
import requests
import time
import json
import os

# --- CONFIGURATION ---
# The bridge will try to find your Arduino automatically, or use COM6 as fallback
DEFAULT_PORT = 'COM6'
BAUD_RATE = 115200
# YOUR HUGGING FACE SPACE URL
HF_API_URL = "https://jerryjr1705-fatiguepred.hf.space/api/sensor_data/ingest"

# UNIQUE IDENTIFIER FOR THIS VEHICLE (Sync this with your Owner App)
VEHICLE_ID = "TRUCK-770-PRO" 

def find_arduino():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if 'CH340' in p.description or 'Arduino' in p.description or 'USB' in p.description:
            return p.device
    return DEFAULT_PORT

def run_bridge():
    port = find_arduino()
    print(f"🚀 FatigueGuard Sensor Bridge")
    print(f"🔗 Local Port: {port}")
    print(f"🌐 Cloud URL:  {HF_API_URL}")
    print("-" * 40)

    try:
        ser = serial.Serial(port, BAUD_RATE, timeout=1)
        time.sleep(2) # Wait for Arduino reset
        print(f"✅ Connected to Arduino on {port}")
    except Exception as e:
        print(f"❌ ERROR: Could not open {port}. Is it in use by another app?")
        return

    success_count = 0
    fail_count = 0

    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if not line: continue
                
                # Format: "T:36.5, HR:72, SPO2:98, AX:0.1, AY:0.2, AZ:9.8"
                print(f"📥 Data: {line}")
                
                try:
                    # POST to Hugging Face
                    payload = {
                        "raw_sensor_data": line,
                        "vehicle_id": VEHICLE_ID
                    }
                    resp = requests.post(HF_API_URL, json=payload, timeout=3)
                    if resp.status_code == 200:
                        success_count += 1
                        print(f"📤 Sync OK ({success_count})")
                    else:
                        fail_count += 1
                        print(f"⚠️ Sync Failed ({resp.status_code})")
                except Exception as net_e:
                    print(f"🌐 Network Error: {net_e}")
            
            time.sleep(0.1) # Prevent CPU hogging
            
    except KeyboardInterrupt:
        print("\n👋 Closing bridge...")
    finally:
        ser.close()

if __name__ == "__main__":
    run_bridge()
