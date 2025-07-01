#!/usr/bin/env python3
"""
Setup script for Cogit project development environment.
This script handles environment setup and dependency management.
"""

import subprocess
import sys
import os

def install_requirements():
    """Install project requirements."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "../../requirements.txt"])
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False
    return True

def check_environment():
    """Check if the development environment is properly configured."""
    required_files = [
        "../../config.yaml",
        "../../requirements.txt",
        "../../Cogit/app-cogit.py"
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Missing required file: {file}")
            return False
        else:
            print(f"✅ Found: {file}")
    
    return True

def main():
    """Main setup function."""
    print("🚀 Setting up Cogit development environment...")
    
    if not check_environment():
        print("❌ Environment check failed")
        sys.exit(1)
    
    if install_requirements():
        print("🎉 Setup completed successfully!")
    else:
        print("❌ Setup failed")
        sys.exit(1)

if __name__ == "__main__":
    main()