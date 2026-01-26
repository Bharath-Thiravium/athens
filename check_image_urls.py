#!/usr/bin/env python3
import requests
import sys

urls = [
    "https://prozeal.athenas.co.in/media/signature_templates/signature_template_v4_68_20260122_143843_xZOBPE6.png",
    "https://prozeal.athenas.co.in/media/signature_templates/signature_template_v4_56_20260122_143843_eWMc9V8.png"
]

for i, url in enumerate(urls, 1):
    try:
        response = requests.head(url, timeout=10)
        print(f"URL {i}: {response.status_code} - {url}")
        if response.status_code == 200:
            print(f"  ✓ Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
            print(f"  ✓ Content-Length: {response.headers.get('Content-Length', 'Unknown')} bytes")
        else:
            print(f"  ✗ Error: HTTP {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"URL {i}: FAILED - {url}")
        print(f"  ✗ Error: {e}")
    print()