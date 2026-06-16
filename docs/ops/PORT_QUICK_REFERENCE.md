# Port Management Quick Reference

## Add New Service (One Command)
```bash
sudo add-project-service <name> <port> <type> <workdir> [venv]
```

**Types:** `gunicorn-wsgi` | `gunicorn-asgi` | `uvicorn` | `node`

## Common Commands

| Action | Command |
|--------|---------|
| **Add service** | `sudo add-project-service myapp 8005 gunicorn-wsgi /var/www/myapp` |
| **Check status** | `systemctl status project@myapp` |
| **View logs** | `journalctl -u project@myapp -f` |
| **Restart** | `sudo systemctl restart project@myapp` |
| **Stop** | `sudo systemctl stop project@myapp` |
| **Check port** | `sudo ss -H -ltnp "sport = :8005"` |
| **View all ports** | `cat /etc/projects/ports.txt` |
| **Port audit** | `sudo ss -H -ltnp \| awk '$4 ~ /:(800[0-9])$/'` |

## Current Services

```
athens-backend  → 8001 (custom service)
project@rayzen  → 8002 (template)
project@athens2 → 8003 (template)
project@sap     → 8004 (template)
```

## Files

- **Template**: `/etc/systemd/system/project@.service`
- **Configs**: `/etc/projects/<name>.env` + `/etc/projects/<name>.start`
- **Registry**: `/etc/projects/ports.txt`
- **SOP**: `/var/www/athens/docs/ops/PORT_MANAGEMENT_SOP.md`
- **Script**: `/usr/local/bin/add-project-service`

## Troubleshooting

```bash
# Check logs
journalctl -u project@<name> -n 50

# Test manually
sudo -u www-data bash -c 'source /etc/projects/<name>.env && /etc/projects/<name>.start'

# Find port owner
sudo ss -H -ltnp "sport = :<port>"
```

## Examples

### Django
```bash
sudo add-project-service blog 8010 gunicorn-wsgi /var/www/blog/backend
# Enter: blog.wsgi:application
# Enter: blog.settings
```

### FastAPI
```bash
sudo add-project-service api 8011 uvicorn /var/www/api
# Enter: main:app
```

### Node.js
```bash
sudo add-project-service webapp 8012 node /var/www/webapp
# Enter: server.js
```
