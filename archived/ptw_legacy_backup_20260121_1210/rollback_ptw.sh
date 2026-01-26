#!/bin/bash
# PTW Legacy Rollback Script
# Usage: ./rollback_ptw.sh --yes

BACKUP_DIR="/var/www/athens/archived/ptw_legacy_backup_20260121_1210"
TARGET_DIR="/var/www/athens"

if [ "$1" != "--yes" ]; then
    echo "PTW Rollback Preview:"
    echo "This will restore the following files from backup:"
    find "$BACKUP_DIR" -type f -not -name "*.sh" -not -name "MANIFEST.txt" -not -name "validate_*" | while read file; do
        rel_path=${file#$BACKUP_DIR/}
        echo "  $TARGET_DIR/$rel_path"
    done
    echo ""
    echo "Run with --yes to execute rollback"
    exit 0
fi

echo "Executing PTW rollback..."
rsync -a --exclude="*.sh" --exclude="MANIFEST.txt" --exclude="validate_*" \
    "$BACKUP_DIR/" "$TARGET_DIR/"

if [ $? -eq 0 ]; then
    echo "✓ PTW rollback completed successfully"
    echo "Run validation: cd /var/www/athens/app/backend && source venv/bin/activate && python manage.py check"
else
    echo "✗ PTW rollback failed"
    exit 1
fi