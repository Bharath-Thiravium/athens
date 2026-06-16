# Port Management & Service Deployment SOP

## Overview
Automated system for deploying collision-proof backend services with static port allocation.

## Architecture
- **Template Service**: `/etc/systemd/system/project@.service`
- **Project Configs**: `/etc/projects/<name>.env` + `/etc/projects/<name>.start`
- **Port Registry**: `/etc/projects/ports.txt`
- **Automation Script**: `/usr/local/bin/add-project-service`

---

## Quick Start: Add New Service

### One-Command Deployment

```bash
sudo add-project-service <project-name> <port> <type> <workdir> [venv-path]
```

**Types:**
- `gunicorn-wsgi` - Django WSGI apps
- `gunicorn-asgi` - FastAPI/Django ASGI via Gunicorn
- `uvicorn` - FastAPI/ASGI via Uvicorn
- `node` - Node.js/Express apps

### Examples

#### Django Project
```bash
sudo add-project-service myapp 8005 gunicorn-wsgi /var/www/myapp/backend
# Prompts for: WSGI module (e.g., myapp.wsgi:application)
# Prompts for: DJANGO_SETTINGS_MODULE (optional)
```

#### FastAPI Project
```bash
sudo add-project-service api 8006 uvicorn /var/www/api
# Prompts for: ASGI module (e.g., main:app)
```

#### Node.js Project
```bash
sudo add-project-service nodeapp 8007 node /var/www/nodeapp
# Prompts for: Script name (e.g., server.js)
```

---

## Manual Deployment (Advanced)

### 1. Create Environment File

```bash
sudo tee /etc/projects/<name>.env > /dev/null << 'EOF'
APP_PORT=8005
WORKDIR=/var/www/<name>
VENV=/var/www/<name>/venv
WORKERS=4
PYTHONUNBUFFERED=1
DJANGO_SETTINGS_MODULE=<name>.settings  # If Django
EOF
```

### 2. Create Start Script

**Gunicorn (Django):**
```bash
sudo tee /etc/projects/<name>.start > /dev/null << 'EOF'
#!/bin/bash
set -euo pipefail
cd "$WORKDIR"
[[ -f .env ]] && set -a && source .env && set +a
exec "$VENV/bin/gunicorn" <module>.wsgi:application \
  --bind 127.0.0.1:${APP_PORT} \
  --workers ${WORKERS} \
  --worker-tmp-dir /dev/shm \
  --timeout 120 \
  --graceful-timeout 30 \
  --access-logfile - \
  --error-logfile -
EOF
sudo chmod +x /etc/projects/<name>.start
```

**Uvicorn (FastAPI):**
```bash
sudo tee /etc/projects/<name>.start > /dev/null << 'EOF'
#!/bin/bash
set -euo pipefail
cd "$WORKDIR"
exec "$VENV/bin/uvicorn" main:app \
  --host 127.0.0.1 \
  --port ${APP_PORT} \
  --workers ${WORKERS}
EOF
sudo chmod +x /etc/projects/<name>.start
```

**Node.js:**
```bash
sudo tee /etc/projects/<name>.start > /dev/null << 'EOF'
#!/bin/bash
set -euo pipefail
cd "$WORKDIR"
export PORT="${APP_PORT}"
export HOST="127.0.0.1"
exec /usr/bin/node server.js
EOF
sudo chmod +x /etc/projects/<name>.start
```

### 3. Update Port Registry

```bash
echo "<name>   <port>" | sudo tee -a /etc/projects/ports.txt
```

### 4. Enable and Start

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now project@<name>
```

---

## Service Management

### Check Status
```bash
systemctl status project@<name>
```

### View Logs
```bash
journalctl -u project@<name> -f
journalctl -u project@<name> -n 100 --no-pager
```

### Restart Service
```bash
sudo systemctl restart project@<name>
```

### Stop Service
```bash
sudo systemctl stop project@<name>
```

### Disable Service
```bash
sudo systemctl disable project@<name>
```

### Remove Service
```bash
sudo systemctl stop project@<name>
sudo systemctl disable project@<name>
sudo rm /etc/projects/<name>.env /etc/projects/<name>.start
sudo sed -i '/^<name> /d' /etc/projects/ports.txt
sudo systemctl daemon-reload
```

---

## Port Management

### View All Allocated Ports
```bash
cat /etc/projects/ports.txt
```

### Check Port Availability
```bash
sudo ss -H -ltnp "sport = :<port>"
```

### Find Next Available Port
```bash
for port in {8001..8100}; do
  if ! grep -q " $port$" /etc/projects/ports.txt && ! ss -H -ltn "sport = :$port" | grep -q .; then
    echo "Available: $port"
    break
  fi
done
```

### Port Audit Report
```bash
sudo ss -H -ltnp | awk '$4 ~ /:(800[0-9]|801[0-9])$/'
```

---

## Troubleshooting

### Service Won't Start

1. **Check logs:**
   ```bash
   journalctl -u project@<name> -n 50 --no-pager
   ```

2. **Verify port is free:**
   ```bash
   sudo ss -H -ltnp "sport = :<port>"
   ```

3. **Check working directory:**
   ```bash
   ls -la /var/www/<name>
   ```

4. **Test start script manually:**
   ```bash
   sudo -u www-data bash -c 'source /etc/projects/<name>.env && /etc/projects/<name>.start'
   ```

### Port Already in Use

```bash
# Find what's using the port
sudo ss -H -ltnp "sport = :<port>"

# Kill process if safe
sudo kill <PID>

# Or stop conflicting service
sudo systemctl stop <conflicting-service>
```

### Permission Issues

```bash
# Fix ownership
sudo chown -R www-data:www-data /var/www/<name>

# Fix venv permissions
sudo chown -R www-data:www-data /var/www/<name>/venv
```

---

## Current Production Services

| Service | Port | Type | Status |
|---------|------|------|--------|
| athens-backend | 8001 | Django/Gunicorn | ✅ Running (custom service) |
| project@rayzen | 8002 | Django/Uvicorn | ✅ Running (template) |
| project@athens2 | 8003 | Django/Gunicorn | ✅ Running (template) |
| project@sap | 8004 | Django/Gunicorn | ✅ Running (template) |

---

## Security Features

- ✅ All services bind to `127.0.0.1` (localhost only)
- ✅ Running as `www-data` (non-root)
- ✅ Port collision prevention (ExecStartPre checks)
- ✅ NoNewPrivileges=true
- ✅ PrivateTmp=true
- ✅ LimitNOFILE=65535
- ✅ Graceful shutdown (TimeoutStopSec, graceful-timeout)
- ✅ Auto-restart on failure

---

## Monitoring

### Daily Port Check Script

```bash
sudo tee /usr/local/bin/check-project-ports > /dev/null << 'EOF'
#!/bin/bash
while read name port; do
  [[ "$name" =~ ^# ]] && continue
  if ! ss -H -ltn "sport = :$port" | grep -q .; then
    echo "ALERT: $name (port $port) is not listening"
  fi
done < /etc/projects/ports.txt
EOF
sudo chmod +x /usr/local/bin/check-project-ports
```

### Add to Cron (Daily at 6 AM)

```bash
echo "0 6 * * * /usr/local/bin/check-project-ports | mail -s 'Port Check Alert' admin@example.com" | sudo crontab -
```

---

## Backup & Recovery

### Backup Configuration

```bash
sudo tar -czf /backup/project-configs-$(date +%Y%m%d).tar.gz /etc/projects/ /etc/systemd/system/project@.service
```

### Restore Configuration

```bash
sudo tar -xzf /backup/project-configs-YYYYMMDD.tar.gz -C /
sudo systemctl daemon-reload
```

---

## Best Practices

1. **Always use the automation script** for new services
2. **Test in staging** before production deployment
3. **Monitor logs** after deployment: `journalctl -u project@<name> -f`
4. **Use localhost binding** (127.0.0.1) and expose via nginx
5. **Keep port registry updated** manually if needed
6. **Document custom configurations** in project README
7. **Regular backups** of `/etc/projects/`

---

## Support

For issues or questions:
1. Check logs: `journalctl -u project@<name> -n 100`
2. Verify port: `sudo ss -H -ltnp "sport = :<port>"`
3. Test manually: `sudo -u www-data /etc/projects/<name>.start`
4. Review this SOP
