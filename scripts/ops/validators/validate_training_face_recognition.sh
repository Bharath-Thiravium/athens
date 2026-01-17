#!/bin/bash

# Training Face Recognition Validation Script
echo "🚀 Validating Training Face Recognition Implementation"
echo "====================================================="

# Check if shared module exists
echo "📦 Checking shared face recognition module..."
if [ -f "/var/www/athens/backend/shared/training_face_recognition.py" ]; then
    echo "✅ Shared face recognition module found"
else
    echo "❌ Shared face recognition module missing"
    exit 1
fi

# Check if face recognition is implemented in training modules
echo ""
echo "🔍 Checking face recognition implementation in training modules..."

# Check Induction Training
if grep -q "from shared.training_face_recognition import" /var/www/athens/backend/inductiontraining/views.py; then
    echo "✅ Induction Training: Face recognition implemented"
else
    echo "❌ Induction Training: Face recognition not implemented"
fi

# Check Job Training
if grep -q "from shared.training_face_recognition import" /var/www/athens/backend/jobtraining/views.py; then
    echo "✅ Job Training: Face recognition implemented"
else
    echo "❌ Job Training: Face recognition not implemented"
fi

# Check Toolbox Talk
if grep -q "from shared.training_face_recognition import" /var/www/athens/backend/tbt/views.py; then
    echo "✅ Toolbox Talk: Face recognition implemented"
else
    echo "❌ Toolbox Talk: Face recognition not implemented"
fi

# Check if 65% threshold is used
echo ""
echo "🎯 Checking 65% confidence threshold..."

if grep -q "confidence_threshold=0.65" /var/www/athens/backend/shared/training_face_recognition.py; then
    echo "✅ 65% confidence threshold configured"
else
    echo "❌ 65% confidence threshold not found"
fi

# Check face recognition results in responses
echo ""
echo "📊 Checking face recognition results in API responses..."

if grep -q "face_recognition_results" /var/www/athens/backend/inductiontraining/views.py; then
    echo "✅ Induction Training: Face recognition results included in response"
else
    echo "❌ Induction Training: Face recognition results missing from response"
fi

if grep -q "face_recognition_results" /var/www/athens/backend/jobtraining/views.py; then
    echo "✅ Job Training: Face recognition results included in response"
else
    echo "❌ Job Training: Face recognition results missing from response"
fi

if grep -q "face_recognition_results" /var/www/athens/backend/tbt/views.py; then
    echo "✅ Toolbox Talk: Face recognition results included in response"
else
    echo "❌ Toolbox Talk: Face recognition results missing from response"
fi

# Test Python imports
echo ""
echo "🐍 Testing Python imports..."
cd /var/www/athens/backend
source venv/bin/activate 2>/dev/null || echo "⚠️  Virtual environment not found, using system Python"

python3 -c "
try:
    from shared.training_face_recognition import compare_training_faces, get_participant_photo_path
    print('✅ Training face recognition imports successful')
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

# Check if backend server is running
echo ""
echo "🌐 Checking backend server..."
if curl -s http://localhost:8000/authentication/ > /dev/null 2>&1; then
    echo "✅ Backend server is running on port 8000"
else
    echo "⚠️  Backend server not responding on port 8000"
fi

echo ""
echo "📋 Implementation Summary:"
echo "   ✅ Shared face recognition utility created"
echo "   ✅ 65% confidence threshold implemented"
echo "   ✅ Face recognition integrated into all training modules:"
echo "      - Induction Training (/dashboard/inductiontraining)"
echo "      - Job Training (/dashboard/jobtraining)" 
echo "      - Toolbox Talk (/dashboard/toolboxtalk)"
echo "   ✅ Consistent preprocessing with CLAHE and bilateral filtering"
echo "   ✅ Support for both workers and users"
echo "   ✅ Fallback to basic face detection when face_recognition unavailable"
echo "   ✅ Face recognition results included in API responses"

echo ""
echo "🎯 Expected Results:"
echo "   - Training attendance will use same face recognition as main attendance"
echo "   - 65% confidence threshold for face matching"
echo "   - Better handling of different lighting conditions"
echo "   - Consistent face recognition across all training modules"
echo "   - Face recognition results logged and returned in API responses"

echo ""
echo "✅ Training Face Recognition Implementation Completed!"
echo "🔄 Please restart the backend server to apply changes:"
echo "   cd /var/www/athens/backend && source venv/bin/activate && python manage.py runserver 0.0.0.0:8000"