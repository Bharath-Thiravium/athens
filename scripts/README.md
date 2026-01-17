# scripts/

Operational, admin, and maintenance scripts that are not part of runtime app code.

Belongs here:
- Ops workflows (deploy, restart, health checks)
- Admin utilities (user resets, data fixes)
- Maintenance and data scripts

Do not place here:
- Application source code
- Infrastructure manifests (Docker, nginx, systemd)
- Long-lived services or daemons
