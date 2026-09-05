#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/deploy/config.env"

die() {
  echo "ERROR: $*" >&2
  exit 1
}

need_python() {
  command -v python3 >/dev/null 2>&1 || die "python3 not found"
}

build_site() {
  need_python
  cd "$ROOT"
  python3 build.py >/dev/null
  test -f "$ROOT/public/index.html" || die "build failed"
}

deploy_api() {
  command -v ssh >/dev/null 2>&1 || die "ssh not found"
  command -v scp >/dev/null 2>&1 || die "scp not found"
  ssh -o ConnectTimeout=15 "$SSH_HOST" "mkdir -p /opt/clinic-contact/clinic /var/lib/clinic-inquiries && chown www-data:www-data /var/lib/clinic-inquiries && chmod 750 /var/lib/clinic-inquiries"
  scp -o ConnectTimeout=15 "$ROOT/services/contact_api/app.py" "$SSH_HOST:/opt/clinic-contact/app.py"
  scp -o ConnectTimeout=15 "$ROOT/clinic/security.py" "$SSH_HOST:/opt/clinic-contact/clinic/security.py"
  ssh -o ConnectTimeout=15 "$SSH_HOST" "test -f /opt/clinic-contact/clinic/__init__.py || touch /opt/clinic-contact/clinic/__init__.py"
  scp -o ConnectTimeout=15 "$ROOT/deploy/contact-api.env" "$SSH_HOST:/etc/clinic-contact.env"
  scp -o ConnectTimeout=15 "$ROOT/deploy/contact-api.service" "$SSH_HOST:/etc/systemd/system/clinic-contact.service"
  ssh -o ConnectTimeout=15 "$SSH_HOST" "systemctl daemon-reload && systemctl enable clinic-contact && systemctl restart clinic-contact"
}

preview_site() {
  build_site
  cd "$ROOT/public"
  echo "PREVIEW http://127.0.0.1:${PREVIEW_PORT}"
  python3 -m http.server "$PREVIEW_PORT" --bind 127.0.0.1
}

purge_cloudflare_cache() {
  if [[ -z "${CLOUDFLARE_ZONE_ID:-}" || -z "${CLOUDFLARE_API_TOKEN:-}" ]]; then
    return 0
  fi
  curl -sf -X POST "https://api.cloudflare.com/client/v4/zones/${CLOUDFLARE_ZONE_ID}/purge_cache" \
    -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
    -H "Content-Type: application/json" \
    --data '{"purge_everything":true}' >/dev/null || true
}

deploy_site() {
  build_site
  command -v rsync >/dev/null 2>&1 || die "rsync not found"
  ssh -o ConnectTimeout=15 -o BatchMode=yes "$SSH_HOST" "mkdir -p '$REMOTE_DIR'" || die "ssh failed: $SSH_HOST"
  rsync -avz --delete -e "ssh -o ConnectTimeout=15" "$ROOT/public/" "$SSH_HOST:$REMOTE_DIR/"
  scp -o ConnectTimeout=15 "$ROOT/deploy/nginx.conf" "$SSH_HOST:/etc/nginx/sites-available/$DOMAIN"
  deploy_api
  ssh "$SSH_HOST" "nginx -t && systemctl reload nginx" || die "nginx reload failed"
  purge_cloudflare_cache
  echo "LIVE https://$DOMAIN"
}

setup_server() {
  command -v ssh >/dev/null 2>&1 || die "ssh not found"
  ssh -o ConnectTimeout=15 "$SSH_HOST" "bash -s" <<EOF
set -euo pipefail
mkdir -p '$REMOTE_DIR'
apt-get update -qq
apt-get install -y nginx rsync
cat > /etc/nginx/sites-available/$DOMAIN <<'NGX'
$(cat "$ROOT/deploy/nginx.conf")
NGX
ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/$DOMAIN
nginx -t
systemctl enable nginx
systemctl restart nginx
EOF
  deploy_api
  echo "SERVER OK $DOMAIN -> $REMOTE_DIR"
}
