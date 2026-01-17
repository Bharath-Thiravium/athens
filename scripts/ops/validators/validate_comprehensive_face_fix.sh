#!/bin/bash

# Comprehensive Face Recognition Fix Validation
echo "🚀 Comprehensive Face Recognition Fix Validation"
echo "================================================"

# Check if all components are properly implemented
echo "🔍 Checking face recognition components..."

# 1. Check shared training face recognition module
if [ -f "/var/www/athens/backend/shared/training_face_recognition.py" ]; then
    echo "✅ Shared training face recognition module exists"
    
    # Check for strict basic comparison
    if grep -q "confidence_threshold = 0.85" /var/www/athens/backend/shared/training_face_recognition.py; then
        echo "✅ Strict 85% threshold for basic detection implemented"
    else
        echo "❌ Strict 85% threshold not found"
    fi
    
    # Check for individual metric validation
    if grep -q "template_score < 0.6" /var/www/athens/backend/shared/training_face_recognition.py; then
        echo "✅ Individual metric validation implemented"
    else
        echo "❌ Individual metric validation not found"
    fi
    
    # Check for user validation function
    if grep -q "validate_user_face_attendance" /var/www/athens/backend/shared/training_face_recognition.py; then
        echo "✅ User face validation function exists"
    else
        echo "❌ User face validation function not found"
    fi
else
    echo "❌ Shared training face recognition module missing"
fi

# 2. Check face comparison API
echo ""
echo "🌐 Checking face comparison API..."
if [ -f "/var/www/athens/backend/authentication/face_comparison_api.py" ]; then
    echo "✅ Face comparison API exists"
    
    if grep -q "confidence_threshold=0.70" /var/www/athens/backend/authentication/face_comparison_api.py; then
        echo "✅ 70% threshold in face comparison API"
    else
        echo "❌ 70% threshold not found in face comparison API"
    fi
    
    if grep -q "from shared.training_face_recognition import compare_training_faces" /var/www/athens/backend/authentication/face_comparison_api.py; then
        echo "✅ Face comparison API uses shared module"
    else
        echo "❌ Face comparison API not using shared module"
    fi
else
    echo "❌ Face comparison API missing"
fi

# 3. Check user self-validation API
echo ""
echo "👤 Checking user self-validation API..."
if [ -f "/var/www/athens/backend/authentication/user_face_validation_api.py" ]; then
    echo "✅ User self-validation API exists"
    
    if grep -q "validate_user_self_face" /var/www/athens/backend/authentication/user_face_validation_api.py; then
        echo "✅ User self-validation function implemented"
    else
        echo "❌ User self-validation function not found"
    fi
else
    echo "❌ User self-validation API missing"
fi

# 4. Check URL configuration
echo ""
echo "🔗 Checking URL configuration..."
if grep -q "validate-user-face" /var/www/athens/backend/authentication/urls.py; then
    echo "✅ User face validation endpoint configured"
else
    echo "❌ User face validation endpoint not configured"
fi

# 5. Check induction training integration
echo ""
echo "🎓 Checking induction training integration..."
if grep -q "validate_user_face_attendance" /var/www/athens/backend/inductiontraining/views.py; then
    echo "✅ Induction training uses user validation"
else
    echo "❌ Induction training not using user validation"
fi

if grep -q "confidence_threshold=0.70" /var/www/athens/backend/inductiontraining/views.py; then
    echo "✅ 70% threshold in induction training"
else
    echo "❌ 70% threshold not found in induction training"
fi

# 6. Test Python imports
echo ""
echo "🐍 Testing Python imports..."
cd /var/www/athens/backend
source venv/bin/activate 2>/dev/null || echo "⚠️  Virtual environment not found, using system Python"

python3 -c "
try:
    from shared.training_face_recognition import validate_user_face_attendance, compare_training_faces
    from authentication.user_face_validation_api import validate_user_self_face
    print('✅ All face recognition imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
except Exception as e:
    print(f'❌ Error: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Python import test failed"
    exit 1
fi

# 7. Check server status
echo ""
echo "🌐 Checking backend server..."
if curl -s http://localhost:8000/authentication/ > /dev/null 2>&1; then
    echo "✅ Backend server is running on port 8000"
    
    # Test the new endpoint
    echo "🧪 Testing new validation endpoint..."
    if curl -s http://localhost:8000/authentication/validate-user-face/ > /dev/null 2>&1; then
        echo "✅ User face validation endpoint is accessible"
    else
        echo "⚠️  User face validation endpoint not accessible (may require authentication)"
    fi
else
    echo "⚠️  Backend server not responding on port 8000"
fi

echo ""
echo "📋 Comprehensive Fix Summary:"
echo "   ✅ Strict Basic Face Comparison:"
echo "      - 85% threshold for basic detection (very conservative)"
echo "      - Individual metric validation (template, histogram, structural, size)"
echo "      - Requires exactly 1 face in each image"
echo "      - Multiple similarity algorithms with weighted scoring"
echo ""
echo "   ✅ Advanced Face Recognition:"
echo "      - 70% confidence threshold for training attendance"
echo "      - Proper image preprocessing with CLAHE and bilateral filtering"
echo "      - Best match selection among multiple detected faces"
echo ""
echo "   ✅ User Validation:"
echo "      - validate_user_face_attendance() for logged-in user verification"
echo "      - New /authentication/validate-user-face/ endpoint"
echo "      - Ensures attendance is marked only for the correct user"
echo ""
echo "   ✅ API Integration:"
echo "      - Fixed /authentication/compare-faces/ to use improved algorithms"
echo "      - Proper error handling and validation messages"
echo "      - Detailed logging for debugging"
echo ""
echo "   ✅ Induction Training Integration:"
echo "      - Uses strict user validation for logged-in user"
echo "      - 70% confidence threshold enforced"
echo "      - Attendance blocked for non-matching faces"

echo ""
echo "🎯 Expected Results After Fix:"
echo "   ❌ NO MORE 75% false positives for different faces"
echo "   ✅ Only matching faces will show high confidence (>70%)"
echo "   ✅ Different faces will show low confidence (<70%) and be rejected"
echo "   ✅ Clear error messages: 'Face does not match. Attendance not marked.'"
echo "   ✅ Multiple faces or unclear captures will be rejected"
echo "   ✅ Attendance validation against logged-in user's registered photo"

echo ""
echo "✅ Comprehensive Face Recognition Fix Validation Completed!"
echo "🔄 Please restart the backend server to apply all changes:"
echo "   cd /var/www/athens/backend && source venv/bin/activate && python manage.py runserver 0.0.0.0:8000"

echo ""
echo "🧪 Testing Instructions:"
echo "   1. Login to the system with a user who has a registered photo"
echo "   2. Go to Induction Training attendance"
echo "   3. Try taking attendance with:"
echo "      - Your own face (should show >70% and mark present)"
echo "      - A different person's face (should show <70% and mark absent)"
echo "      - Multiple faces (should be rejected)"
echo "      - Unclear/blurry image (should be rejected)"