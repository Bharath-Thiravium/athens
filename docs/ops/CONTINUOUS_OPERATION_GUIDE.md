# Athens Continuous Operation System

## Overview
The Athens Keeper system ensures your frontend and backend services run continuously without interruption.

## Quick Commands

### Check Status
```bash
/var/www/athens/athens-keeper.sh status
# or
systemctl status athens-keeper.service
```

### Maintenance Mode
```bash
# Enable maintenance (stops services)
/var/www/athens/maintenance.sh on

# Disable maintenance (starts services)
/var/www/athens/maintenance.sh off

# Check maintenance status
/var/www/athens/maintenance.sh status
```

### Service Control
```bash
# Start keeper service
systemctl start athens-keeper.service

# Stop keeper service
systemctl stop athens-keeper.service

# Restart keeper service
systemctl restart athens-keeper.service
```

## How It Works

1. **Athens Keeper** runs as a systemd service that monitors both frontend and backend
2. Checks every 10 seconds if services are running
3. Automatically restarts any stopped services
4. Respects maintenance mode - stops services when maintenance is enabled
5. Logs all activities to `/var/log/athens-keeper.log`

## Maintenance Mode

- **Enable**: `./maintenance.sh on` - Services will stop and stay stopped
- **Disable**: `./maintenance.sh off` - Services will start automatically
- **Status**: `./maintenance.sh status` - Shows current state

## Service Ports

- **Backend**: Port 8001 (configured via ATHENS_BACKEND_PORT)
- **Frontend**: Port 3000 (Vite dev server)

## Log Files

- **Keeper Log**: `/var/log/athens-keeper.log`
- **Backend Log**: `/tmp/backend.log`
- **Frontend Log**: `/tmp/frontend.log`

## Troubleshooting

If services aren't starting:
1. Check logs: `tail -f /var/log/athens-keeper.log`
2. Verify ports aren't blocked
3. Check maintenance mode status
4. Restart keeper service: `systemctl restart athens-keeper.service`