import requests
import time
import sys

print("🔍 Searching for active Ngrok tunnel...")

for i in range(5):
    try:
        response = requests.get("http://localhost:4040/api/tunnels", timeout=2)
        if response.status_code == 200:
            data = response.json()
            tunnels = data.get('tunnels', [])
            if tunnels:
                public_url = tunnels[0]['public_url']
                print(f"\n==================================================")
                print(f"✅ NGROK PUBLIC URL: {public_url}")
                print(f"==================================================\n")
                sys.exit(0)
    except requests.exceptions.ConnectionError:
        pass
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(1)

print("\n❌ Ngrok is not running.")
print("👉 Please run 'Start Fatigue System' shortcut or START_SYSTEM.bat first.")
