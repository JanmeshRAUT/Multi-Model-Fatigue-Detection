#!/usr/bin/env python3
"""
Quick setup script to configure Hugging Face model integration.
This script helps you set up the necessary environment variables.
"""

import os
import sys
from pathlib import Path

def create_env_file(fatigue_repo, vehicle_repo, hf_token=None):
    """Create .env file with HF configuration."""
    backend_dir = Path(__file__).parent
    env_path = backend_dir / ".env"
    
    env_content = f"""# ==========================================
# Hugging Face Model Configuration
# ==========================================
HF_FATIGUE_MODEL_REPO={fatigue_repo}
HF_VEHICLE_MODEL_REPO={vehicle_repo}

# Optional: HF Token for private repositories
HF_TOKEN={hf_token or ""}

# ==========================================
# Arduino/Serial Configuration
# ==========================================
ARDUINO_PORT=COM6
BAUD_RATE=115200

# ==========================================
# Backend Configuration
# ==========================================
DEBUG=True
USE_MOCK_DATA=False
ML_INTERVAL=0.5
MAX_HISTORY=100
SENSOR_TIMEOUT=2.0
"""
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"✅ .env file created at {env_path}")
    return env_path

def install_dependencies():
    """Install required Python packages."""
    import subprocess
    
    backend_dir = Path(__file__).parent
    req_file = backend_dir / "requirements.txt"
    
    print("📦 Installing dependencies from requirements.txt...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(req_file)])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def main():
    """Main setup wizard."""
    print("=" * 60)
    print("🚀 Hugging Face Model Integration Setup")
    print("=" * 60)
    print()
    
    # Get user inputs
    print("Please provide your Hugging Face model repositories.")
    print("Format: username/repository-name")
    print()
    
    fatigue_repo = input("Fatigue Model Repository (e.g., janmesh/fatigue-model): ").strip()
    vehicle_repo = input("Vehicle Model Repository (e.g., janmesh/vehicle-model): ").strip()
    
    hf_token = input("HF Token for private repos (press Enter to skip): ").strip()
    
    if not fatigue_repo or not vehicle_repo:
        print("❌ Repository names are required!")
        return False
    
    # Create .env file
    print("\n📝 Creating .env file...")
    create_env_file(fatigue_repo, vehicle_repo, hf_token if hf_token else None)
    
    # Offer to install dependencies
    print("\n📦 Would you like to install dependencies now? (y/n): ", end="")
    if input().lower() == 'y':
        if not install_dependencies():
            print("⚠️  Please run: pip install -r requirements.txt")
    
    print("\n" + "=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Verify your .env file: backend_flask/.env")
    print("2. Ensure models are uploaded to HF Hub with correct filenames")
    print("3. Start the backend: python app.py")
    print("\nFor more details, see: HUGGINGFACE_SETUP.md")
    print()

if __name__ == "__main__":
    main()
