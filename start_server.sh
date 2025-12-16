#!/bin/bash

echo "🚀 Starting EHS System..."

# Navigate to backend directory
cd backend

# Activate virtual environment
source venv/bin/activate

# Check if Django server is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Django server already running on port 8000"
    echo "Stopping existing server..."
    pkill -f "python.*manage.py.*runserver"
    sleep 2
fi

# Start Django server
echo "🔧 Starting Django backend server..."
python manage.py runserver 0.0.0.0:8000 &
DJANGO_PID=$!

# Wait for Django to start
sleep 3

# Test if Django is running
if curl -s http://localhost:8000/authentication/ > /dev/null; then
    echo "✅ Django backend is running on http://localhost:8000"
else
    echo "❌ Django backend failed to start"
    exit 1
fi

# Navigate to frontend directory
cd ../frontedn

# Check if frontend server is already running
if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Frontend server already running on port 5173"
else
    echo "🎨 Starting React frontend server..."
    npm run dev &
    FRONTEND_PID=$!
    
    # Wait for frontend to start
    sleep 5
    
    if curl -s http://localhost:5173 > /dev/null; then
        echo "✅ React frontend is running on http://localhost:5173"
    else
        echo "❌ React frontend failed to start"
    fi
fi

echo ""
echo "🎉 EHS System is ready!"
echo "📱 Frontend: http://localhost:5173"
echo "🔧 Backend API: http://localhost:8000"
echo "👤 Login with: username=ilaiaraja, password=admin123"
echo ""
echo "Press Ctrl+C to stop all servers"

# Keep script running
wait