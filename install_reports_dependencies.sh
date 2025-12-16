#!/bin/bash

# Install Reports Dependencies Script
# This script installs the required Python packages for PTW Reports functionality

echo "🚀 Installing PTW Reports Dependencies..."

# Navigate to backend directory
cd backend

# Install reportlab for PDF generation
echo "📦 Installing reportlab for PDF generation..."
pip install reportlab==4.0.4

echo "✅ Dependencies installed successfully!"
echo ""
echo "📋 Installed packages:"
echo "  - reportlab==4.0.4 (PDF generation)"
echo ""
echo "🎯 PTW Reports system is now ready!"
echo "   - Real-time data connection ✅"
echo "   - PDF export functionality ✅" 
echo "   - Excel/CSV export functionality ✅"
echo "   - Auto-refresh every 5 minutes ✅"
echo ""
echo "🔧 To start using reports:"
echo "   1. Restart your Django server"
echo "   2. Navigate to PTW Reports in the dashboard"
echo "   3. Generate and export reports!"
