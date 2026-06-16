# Startup Configuration Script

## Overview
Automated startup script that enforces static port allocation by killing existing processes and restarting all services on their designated ports.

## Installation
✅ **Already Installed**
- Script: `/usr/local/bin/startup-all-projects`
- Service: `/etc/systemd/system/startup-all-projects.service`
- Log: `/var/log/project-startup.log`

## Usage

### Manual Startup (All Projects)
```bash
sudo startup-all-projects
```

### Manual Startup (Single Project)
```bash
sudo systemctl restart project@<name>
# or
sudo systemctl restart <name>-backend
```

### View Startup Logs
```bash
tail -f /var/log/project-startup.log
```

### Check Boot Service Status
```bash
systemctl status startup-all-projects
```

## How It Works

1. **Reads Port Registry** (`/etc/projects/ports.txt`)
2. **For Each Project:**
   - Finds any process using the allocated port
   - Kills the process (SIGTERM, then SIGKILL if needed)
   - Stops any existing systemd service
   - Starts the correct systemd service
   - Verifies the service is listening on the correct port
3. **Logs Everything** to `/var/log/project-startup.log`

## Automatic Startup on Boot

The system is configured to automatically run this script on boot:
```bash
systemctl status startup-all-projects
```

To disable automatic startup:
```bash
sudo systemctl disable startup-all-projects
```

To re-enable:
```bash
sudo systemctl enable startup-all-projects
```

## Safety Features

- ✅ Logs all actions with timestamps
- ✅ Graceful shutdown (SIGTERM) before force kill (SIGKILL)
- ✅ Verifies services after startup
- ✅ Reports success/failure for each service
- ✅ Shows final port allocation status

## Example Output

```
[2026-02-10 14:15:00] =========================================
[2026-02-10 14:15:00] Starting all projects with port enforcement
[2026-02-10 14:15:00] =========================================
[2026-02-10 14:15:00] Starting athens on port 8001...
[2026-02-10 14:15:00] Port 8001 occupied by PID 12345: /var/www/athens/backend/venv/bin/python...
[2026-02-10 14:15:00] Killing PID 12345 to free port 8001 for athens
[2026-02-10 14:15:02] Port 8001 freed
[2026-02-10 14:15:02] Stopping existing systemd service: athens-backend
[2026-02-10 14:15:04] ✅ athens started successfully on port 8001
[2026-02-10 14:15:04] Starting rayzen on port 8002...
[2026-02-10 14:15:06] ✅ rayzen started successfully on port 8002
...
```

## Troubleshooting

### Service Won't Start
```bash
# Check logs
tail -50 /var/log/project-startup.log

# Check individual service
journalctl -u project@<name> -n 50

# Verify port is free
sudo ss -H -ltnp "sport = :<port>"
```

### Port Still Occupied After Kill
```bash
# Find stubborn process
sudo ss -H -ltnp "sport = :<port>"

# Force kill manually
sudo kill -9 <PID>

# Restart service
sudo systemctl restart project@<name>
```

### Script Fails on Boot
```bash
# Check service status
systemctl status startup-all-projects

# View boot logs
journalctl -u startup-all-projects -b

# Test manually
sudo /usr/local/bin/startup-all-projects
```

## Integration with Existing Services

The script works with:
- ✅ Template-based services (`project@<name>`)
- ✅ Custom services (`<name>-backend`)
- ✅ Any service in `/etc/projects/ports.txt`

## Maintenance

### Add New Project
1. Add to port registry: `echo "newproject 8005" | sudo tee -a /etc/projects/ports.txt`
2. Create service config (see SOP)
3. Run: `sudo startup-all-projects`

### Remove Project
1. Remove from port registry: `sudo sed -i '/^projectname /d' /etc/projects/ports.txt`
2. Stop service: `sudo systemctl stop project@projectname`
3. Disable service: `sudo systemctl disable project@projectname`

### Update Port Allocation
1. Edit `/etc/projects/ports.txt`
2. Update `/etc/projects/<name>.env` with new `APP_PORT`
3. Run: `sudo startup-all-projects`

## Log Rotation

Create log rotation config:
```bash
sudo tee /etc/logrotate.d/project-startup > /dev/null << 'EOF'
/var/log/project-startup.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
EOF
```

## Related Commands

| Action | Command |
|--------|---------|
| **Start all** | `sudo startup-all-projects` |
| **View logs** | `tail -f /var/log/project-startup.log` |
| **Check boot service** | `systemctl status startup-all-projects` |
| **Disable auto-start** | `sudo systemctl disable startup-all-projects` |
| **Enable auto-start** | `sudo systemctl enable startup-all-projects` |
| **Manual restart** | `sudo systemctl restart project@<name>` |
| **Port status** | `sudo ss -H -ltnp \| awk '$4 ~ /:(800[0-9])$/'` |

## Security Considerations

⚠️ **WARNING**: This script kills processes forcefully. Use with caution in production.

- Only kills processes on ports defined in `/etc/projects/ports.txt`
- Logs all kill actions for audit trail
- Uses graceful shutdown (SIGTERM) before force kill
- Verifies service restart after kill

## Best Practices

1. **Test before production**: Run manually first
2. **Monitor logs**: Check `/var/log/project-startup.log` after boot
3. **Backup configs**: Before modifying port registry
4. **Document changes**: Update port registry comments
5. **Regular audits**: Review startup logs weekly
