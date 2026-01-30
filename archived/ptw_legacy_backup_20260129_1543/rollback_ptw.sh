#!/bin/bash
set -e

BACKUP_DIR="/var/www/athens/archived/ptw_legacy_backup_20260129_1543"
ATHENS_ROOT="/var/www/athens"

echo "Rolling back PTW module from backup..."

# Stop services
echo "Stopping services..."
pkill -f "python.*manage.py" || true
pkill -f vite || true

# Restore backend PTW app
echo "Restoring backend PTW app..."
rm -rf "$ATHENS_ROOT/app/backend/ptw"
cp -r "$BACKUP_DIR/ptw" "$ATHENS_ROOT/app/backend/"

# Restore frontend PTW features
echo "Restoring frontend PTW features..."
rm -rf "$ATHENS_ROOT/app/frontend/src/features/ptw"
cp -r "$BACKUP_DIR/ptw" "$ATHENS_ROOT/app/frontend/src/features/"

# Restore PTW API service
echo "Restoring PTW API service..."
cp "$BACKUP_DIR/ptwAPI.ts" "$ATHENS_ROOT/app/frontend/src/services/"

echo "PTW rollback complete. Restart services manually."
echo "Backend: cd $ATHENS_ROOT/app/backend && source venv/bin/activate && python manage.py runserver"
echo "Frontend: cd $ATHENS_ROOT/app/frontend && npm run dev"