#!/usr/bin/env python3
"""
Athens Backend Startup Guard
Ensures proper port configuration and prevents port conflicts
"""
import os
import sys

def validate_port_configuration():
    """Validate that ATHENS_BACKEND_PORT is set and not using forbidden port 8000"""
    
    # Check if ATHENS_BACKEND_PORT is set
    athens_port = os.environ.get('ATHENS_BACKEND_PORT')
    
    if not athens_port:
        print("❌ CRITICAL ERROR: ATHENS_BACKEND_PORT environment variable is not set!")
        print("   Required: ATHENS_BACKEND_PORT=8001")
        print("   Add this to your environment or .env file")
        sys.exit(1)
    
    try:
        port_num = int(athens_port)
    except ValueError:
        print(f"❌ CRITICAL ERROR: ATHENS_BACKEND_PORT must be a valid integer, got: {athens_port}")
        sys.exit(1)
    
    # Forbidden port check
    if port_num == 8000:
        print("❌ CRITICAL ERROR: Port 8000 is FORBIDDEN and must not be used!")
        print("   Athens Backend must use port 8001")
        print("   Set ATHENS_BACKEND_PORT=8001")
        sys.exit(1)
    
    # Validate expected port
    if port_num != 8001:
        print(f"⚠️  WARNING: Athens Backend should use port 8001, but ATHENS_BACKEND_PORT={port_num}")
        print("   This may cause nginx routing issues")
    
    print(f"✅ Port configuration validated: Athens Backend will use port {port_num}")
    return port_num

if __name__ == "__main__":
    validate_port_configuration()