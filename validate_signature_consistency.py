#!/usr/bin/env python3
"""
Validate that all signature types (requestor, verifier, approver) 
generate consistent signature data with company logos and proper formatting.
"""
import os
import sys
import django

# Setup Django
sys.path.append('/var/www/athens/app/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
os.environ.setdefault('SECRET_KEY', 'dev')
django.setup()

from ptw.models import Permit, DigitalSignature
from ptw.serializers import PermitSerializer

def main():
    print("=== SIGNATURE CONSISTENCY VALIDATION ===")
    
    # Get a permit with signatures
    permit = Permit.objects.filter(signatures__isnull=False).first()
    if not permit:
        print("No permits with signatures found")
        return
    
    print(f"Checking permit: {permit.permit_number}")
    
    # Get serializer data
    serializer = PermitSerializer(permit)
    signatures_by_type = serializer.data.get('signatures_by_type', {})
    
    for sig_type in ['requestor', 'verifier', 'approver']:
        sig_data = signatures_by_type.get(sig_type)
        print(f"\n{sig_type.upper()}:")
        
        if not sig_data:
            print("  Status: Not signed")
            continue
            
        print(f"  Signer: {sig_data.get('signer_name')}")
        print(f"  Employee ID: {sig_data.get('employee_id')}")
        print(f"  Designation: {sig_data.get('designation')}")
        print(f"  Signed At: {sig_data.get('signed_at')}")
        print(f"  Render Mode: {sig_data.get('signature_render_mode')}")
        print(f"  Company Logo: {'Yes' if sig_data.get('company_logo_url') else 'No'}")
        
        # Check signature data format
        signature_data = sig_data.get('signature_data', '')
        if signature_data.startswith('data:image/png;base64,'):
            try:
                import base64
                import json
                b64_data = signature_data.replace('data:image/png;base64,', '')
                decoded = base64.b64decode(b64_data).decode('utf-8')
                json_data = json.loads(decoded)
                print(f"  Format: JSON with template_url")
                print(f"  Template URL: {json_data.get('template_url', 'N/A')}")
            except:
                print(f"  Format: Raw PNG ({len(signature_data)} chars)")
        else:
            print(f"  Format: Other ({len(signature_data)} chars)")
    
    print("\n=== VALIDATION COMPLETE ===")

if __name__ == '__main__':
    main()