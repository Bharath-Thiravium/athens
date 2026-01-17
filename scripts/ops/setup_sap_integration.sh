#!/bin/bash

# SAP Integration Setup Script
# Configures Athens for SAP credential synchronization

echo "🔧 Setting up SAP Integration for Athens..."

# Check if SAP configuration exists
if [ ! -f ".env.sap" ]; then
    echo "📝 Creating SAP configuration file..."
    cp .env.sap.example .env.sap
    echo "⚠️  Please edit .env.sap with your SAP API credentials"
fi

# Load SAP environment variables
if [ -f ".env.sap" ]; then
    source .env.sap
fi

# Validate SAP configuration
if [ -z "$SAP_API_URL" ] || [ -z "$SAP_API_KEY" ]; then
    echo "❌ SAP configuration incomplete. Please configure .env.sap"
    exit 1
fi

echo "✅ SAP configuration validated"

# Create management command directory if it doesn't exist
mkdir -p backend/authentication/management/commands

# Run initial SAP credential sync
echo "🔄 Running initial SAP credential synchronization..."
cd backend
source venv/bin/activate
python manage.py sync_sap_credentials

if [ $? -eq 0 ]; then
    echo "✅ SAP credential sync completed successfully"
else
    echo "⚠️  SAP credential sync failed - check logs"
fi

# Setup periodic sync (optional)
read -p "📅 Setup automatic SAP sync every hour? (y/n): " setup_cron
if [ "$setup_cron" = "y" ]; then
    # Add cron job for SAP sync
    (crontab -l 2>/dev/null; echo "0 * * * * cd /var/www/athens/backend && source venv/bin/activate && python manage.py sync_sap_credentials") | crontab -
    echo "✅ Automatic SAP sync configured"
fi

echo "🎉 SAP Integration setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Configure your SAP API credentials in .env.sap"
echo "2. Test authentication with a master user"
echo "3. Monitor logs for SAP sync status"