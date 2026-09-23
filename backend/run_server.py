#!/usr/bin/env python3
"""Start Jarvis 2 API Server with proper environment loading"""
import os
import sys
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Verify credentials
client_id = os.getenv("DHAN_CLIENT_ID", "").strip()
access_token = os.getenv("DHAN_ACCESS_TOKEN", "").strip()

print(f"[OK] DHAN_CLIENT_ID: {'SET' if client_id else 'MISSING'}")
print(f"[OK] DHAN_ACCESS_TOKEN: {'SET' if access_token else 'MISSING'}")

if not client_id or not access_token:
    print("[ERROR] DhanHQ credentials not set!")
    sys.exit(1)

# Start server
import uvicorn
uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
