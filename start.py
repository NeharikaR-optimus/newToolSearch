#!/usr/bin/env python3
"""
Production startup script for Developer Tech Tools Discovery System
"""
import subprocess
import sys

def main():
    """Start the backend server"""
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "backend.fastAPI.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ], check=True)
    except KeyboardInterrupt:
        print("🛑 Server stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())