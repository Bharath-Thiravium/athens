#!/bin/bash

# Athens Maintenance Control
# Simple interface to control maintenance mode

KEEPER_SCRIPT="/var/www/athens/athens-keeper.sh"

case "${1:-help}" in
    on|enable|maintenance)
        echo "🔧 Enabling maintenance mode..."
        $KEEPER_SCRIPT maintenance
        echo "✅ Maintenance mode enabled. Services will stop automatically."
        ;;
    off|disable|resume)
        echo "🚀 Disabling maintenance mode..."
        $KEEPER_SCRIPT resume
        echo "✅ Maintenance mode disabled. Services will start automatically."
        ;;
    status)
        $KEEPER_SCRIPT status
        ;;
    *)
        echo "Athens Maintenance Control"
        echo ""
        echo "Usage: $0 {on|off|status}"
        echo ""
        echo "Commands:"
        echo "  on     - Enable maintenance mode (stops services)"
        echo "  off    - Disable maintenance mode (starts services)"
        echo "  status - Show current status"
        ;;
esac