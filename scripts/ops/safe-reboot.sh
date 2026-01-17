#!/usr/bin/env bash
set -euo pipefail

# ====== CONFIG (edit if needed) ======
PG_CONTAINER="${PG_CONTAINER:-ehs-database-dev}"
REDIS_CONTAINER="${REDIS_CONTAINER:-athens-redis}"
API_HEALTH_URL="${API_HEALTH_URL:-}"   # optional, e.g. http://127.0.0.1:8000/health
LOG_DIR="${LOG_DIR:-/var/log/safe-reboot}"
STAMP="$(date +'%Y%m%d_%H%M%S')"
OUT_DIR="${LOG_DIR}/${STAMP}"

# ====== HELPERS ======
need_cmd() { command -v "$1" >/dev/null 2>&1 || { echo "Missing command: $1" >&2; exit 2; }; }
run() { echo -e "\n==> $*"; "$@"; }

# ====== PRECHECKS ======
need_cmd docker
need_cmd df
need_cmd free
need_cmd ps
need_cmd uptime
need_cmd sudo

mkdir -p "$OUT_DIR"
chmod 700 "$OUT_DIR"

echo "Writing logs to: $OUT_DIR"
echo "PG_CONTAINER=$PG_CONTAINER"
echo "REDIS_CONTAINER=$REDIS_CONTAINER"
[[ -n "$API_HEALTH_URL" ]] && echo "API_HEALTH_URL=$API_HEALTH_URL"

# ====== CAPTURE BASELINE ======
run bash -lc "docker ps" | tee "$OUT_DIR/01_docker_ps.txt"
run bash -lc "docker system df" | tee "$OUT_DIR/02_docker_system_df.txt"
run bash -lc "docker stats --no-stream" | tee "$OUT_DIR/03_docker_stats.txt"
run bash -lc "df -h" | tee "$OUT_DIR/04_df_h.txt"
run bash -lc "free -h" | tee "$OUT_DIR/05_free_h.txt"
run bash -lc "swapon --show || true" | tee "$OUT_DIR/06_swapon_show.txt"
run bash -lc "ps aux --sort=-%mem | head -n 25" | tee "$OUT_DIR/07_ps_mem_top.txt"
run bash -lc "ps aux --sort=-%cpu | head -n 25" | tee "$OUT_DIR/08_ps_cpu_top.txt"

# ====== PRE-REBOOT HEALTH CHECKS ======
echo -e "\n==> Pre-reboot health checks"
# Pre-reboot health checks: record failures but do NOT abort reboot
{
  docker exec "$PG_CONTAINER" pg_isready
} | tee "$OUT_DIR/09_pg_isready_pre.txt" || echo "WARN: pg_isready failed (recorded)" | tee -a "$OUT_DIR/09_pg_isready_pre.txt"

{
  docker exec "$REDIS_CONTAINER" redis-cli ping
} | tee "$OUT_DIR/10_redis_ping_pre.txt" || echo "WARN: redis ping failed (recorded)" | tee -a "$OUT_DIR/10_redis_ping_pre.txt"

if [[ -n "$API_HEALTH_URL" ]]; then
  if command -v curl >/dev/null 2>&1; then
    curl -fsS "$API_HEALTH_URL" | tee "$OUT_DIR/11_api_health_pre.txt"
  else
    echo "curl not installed; skipping API health check" | tee "$OUT_DIR/11_api_health_pre.txt"
  fi
fi

# ====== POST-REBOOT VALIDATOR INSTALL (optional but recommended) ======
# This makes validation automatic on boot and logs to /var/log/safe-reboot/latest/
echo -e "\n==> Installing post-reboot validator (systemd one-shot)"
sudo mkdir -p /usr/local/sbin /etc/systemd/system /var/log/safe-reboot/latest
sudo tee /usr/local/sbin/post-reboot-validate.sh >/dev/null <<'VALIDATOR_EOF'
#!/usr/bin/env bash
set -euo pipefail

PG_CONTAINER="${PG_CONTAINER:-ehs-database-dev}"
REDIS_CONTAINER="${REDIS_CONTAINER:-athens-redis}"
API_HEALTH_URL="${API_HEALTH_URL:-}"
OUT_DIR="/var/log/safe-reboot/latest"
mkdir -p "$OUT_DIR"
chmod 700 "$OUT_DIR"

ts(){ date +'%Y-%m-%d %H:%M:%S'; }
log(){ echo "[$(ts)] $*"; }

log "Post-reboot validation started"
{
  echo "== uptime =="; uptime || true; echo
  echo "== uptime -s =="; uptime -s || true; echo
  echo "== boot id =="; cat /proc/sys/kernel/random/boot_id || true; echo
  echo "== free -h =="; free -h || true; echo
  echo "== swapon --show =="; swapon --show || true; echo
  echo "== df -h =="; df -h || true; echo
  echo "== systemctl status docker =="; systemctl status docker --no-pager || true; echo
  echo "== docker ps =="; docker ps || true; echo
  echo "== docker stats --no-stream =="; docker stats --no-stream || true; echo
  echo "== pg_isready =="; docker exec "$PG_CONTAINER" pg_isready || true; echo
  echo "== redis ping =="
  if docker ps --format '{{.Names}}' | grep -qx "$REDIS_CONTAINER"; then
    docker exec "$REDIS_CONTAINER" redis-cli ping || echo "FAIL: redis-cli ping failed"
  else
    echo "FAIL: Redis container '$REDIS_CONTAINER' is not running"
  fi
  echo
  if [[ -n "$API_HEALTH_URL" ]] && command -v curl >/dev/null 2>&1; then
    echo "== api health =="; curl -fsS "$API_HEALTH_URL" || true; echo
  fi
} | tee "$OUT_DIR/post_reboot_validation.txt"

log "Post-reboot validation completed"
VALIDATOR_EOF
sudo chmod +x /usr/local/sbin/post-reboot-validate.sh

sudo tee /etc/systemd/system/post-reboot-validate.service >/dev/null <<UNIT_EOF
[Unit]
Description=Post reboot validation for Docker host
After=network-online.target docker.service
Wants=network-online.target docker.service

[Service]
Type=oneshot
Environment=PG_CONTAINER=$PG_CONTAINER
Environment=REDIS_CONTAINER=$REDIS_CONTAINER
Environment=API_HEALTH_URL=$API_HEALTH_URL
ExecStart=/usr/local/sbin/post-reboot-validate.sh

[Install]
WantedBy=multi-user.target
UNIT_EOF

sudo systemctl daemon-reload
sudo systemctl enable post-reboot-validate.service >/dev/null

echo -e "\n==> READY TO REBOOT"
echo "Logs captured at: $OUT_DIR"
echo "Post-reboot validation will write to: /var/log/safe-reboot/latest/post_reboot_validation.txt"
echo
read -r -p "Type 'REBOOT' to proceed: " CONFIRM
if [[ "$CONFIRM" != "REBOOT" ]]; then
  echo "Aborted."
  exit 0
fi

# ====== REBOOT ======
run sudo reboot
