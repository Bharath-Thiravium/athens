#!/usr/bin/env python3
"""
Quick test script to validate face recognition fixes
Usage: python test_face_recognition_fix.py
"""

import os
import sys
import django

# Setup Django
sys.path.append('/var/www/athens/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from authentication.views_attendance import compare_faces
from authentication.face_recognition_utils import enhanced_face_comparison
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_face_recognition():
    """Test face recognition with sample images"""
    
    # Find sample attendance photos
    sample_dir = "/var/www/athens/media/attendance_photos/check_in"
    
    if not os.path.exists(sample_dir):
        print("❌ Sample directory not found")
        return
    
    sample_files = [f for f in os.listdir(sample_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if len(sample_files) < 2:
        print("❌ Need at least 2 sample images for testing")
        return
    
    # Test with first two images
    img1_path = os.path.join(sample_dir, sample_files[0])
    img2_path = os.path.join(sample_dir, sample_files[1])
    
    print(f"🔍 Testing face recognition between:")
    print(f"   Image 1: {sample_files[0]}")
    print(f"   Image 2: {sample_files[1]}")
    
    try:
        # Test basic comparison
        with open(img2_path, 'rb') as f:
            result = compare_faces(img1_path, f, tolerance=0.65)
        
        print(f"✅ Basic comparison result: {'MATCH' if result else 'NO MATCH'}")
        
        # Test enhanced comparison
        with open(img2_path, 'rb') as f:
            enhanced_result = enhanced_face_comparison(img1_path, f)
        
        if 'error' not in enhanced_result:
            print(f"✅ Enhanced comparison:")
            print(f"   Match: {enhanced_result.get('matched', False)}")
            print(f"   Confidence: {enhanced_result.get('confidence', 0):.3f}")
            print(f"   Faces detected: {enhanced_result.get('face_counts', {})}")
        else:
            print(f"❌ Enhanced comparison error: {enhanced_result['error']}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    print("🚀 Testing Face Recognition Fixes")
    print("=" * 50)
    test_face_recognition()
    print("=" * 50)
    print("✅ Test completed")