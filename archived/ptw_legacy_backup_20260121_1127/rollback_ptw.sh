#!/bin/bash
set -e

BACKUP_DIR="/var/www/athens/archived/ptw_legacy_backup_20260121_1127"
TARGET_DIR="/var/www/athens"

if [ "$1" != "--yes" ]; then
    echo "PTW Rollback Script"
    echo "=================="
    echo "This will restore PTW files from backup:"
    echo "  From: $BACKUP_DIR"
    echo "  To: $TARGET_DIR"
    echo ""
    echo "Files to restore:"
    find "$BACKUP_DIR" -name "*.py" -o -name "*.ts" -o -name "*.tsx" | sed "s|$BACKUP_DIR/||" | sort
    echo ""
    echo "Run with --yes to execute rollback"
    exit 1
fi

echo "Rolling back PTW files..."
rsync -av --delete "$BACKUP_DIR/app/" "$TARGET_DIR/app/"
echo "Rollback complete!"
echo "Run validate_new_ptw.sh to verify rollback"