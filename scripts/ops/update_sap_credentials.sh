#!/bin/bash

# SAP Credential Update Script
# Usage: ./update_sap_credentials.sh <API_URL> <API_KEY> <CLIENT_ID>

if [ $# -ne 3 ]; then
    echo "Usage: $0 <SAP_API_URL> <SAP_API_KEY> <SAP_CLIENT_ID>"
    echo "Example: $0 https://sap.company.com demo_key_123 client_456"
    exit 1
fi

SAP_API_URL="$1"
SAP_API_KEY="$2" 
SAP_CLIENT_ID="$3"

echo "🔧 Updating SAP credentials..."

# Update main .env file
sed -i "s|SAP_API_URL=.*|SAP_API_URL=$SAP_API_URL|" /var/www/athens/.env
sed -i "s|SAP_API_KEY=.*|SAP_API_KEY=$SAP_API_KEY|" /var/www/athens/.env
sed -i "s|SAP_CLIENT_ID=.*|SAP_CLIENT_ID=$SAP_CLIENT_ID|" /var/www/athens/.env
sed -i "s|SAP_SYNC_ENABLED=.*|SAP_SYNC_ENABLED=true|" /var/www/athens/.env

# Update backend .env file
sed -i "s|SAP_API_URL=.*|SAP_API_URL=$SAP_API_URL|" /var/www/athens/backend/.env
sed -i "s|SAP_API_KEY=.*|SAP_API_KEY=$SAP_API_KEY|" /var/www/athens/backend/.env
sed -i "s|SAP_CLIENT_ID=.*|SAP_CLIENT_ID=$SAP_CLIENT_ID|" /var/www/athens/backend/.env
sed -i "s|SAP_SYNC_ENABLED=.*|SAP_SYNC_ENABLED=true|" /var/www/athens/backend/.env

echo "✅ SAP credentials updated"
echo "🔄 Testing connection..."

# Test SAP connection
cd /var/www/athens/backend
source venv/bin/activate
python manage.py sync_sap_credentials

if [ $? -eq 0 ]; then
    echo "✅ SAP connection successful"
else
    echo "❌ SAP connection failed - check credentials"
fi