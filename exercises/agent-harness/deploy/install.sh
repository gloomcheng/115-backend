#!/usr/bin/env bash
# Install the agent harness as a service on a Debian or Ubuntu host.
#
#   sudo bash deploy/install.sh
#
# The script is idempotent: running it twice leaves the same result as
# running it once.
set -euo pipefail

APP_DIR=/opt/agent-harness
STATE_DIR=/var/lib/agent-harness
CONF_DIR=/etc/agent-harness
SERVICE_USER=harness
SERVICE_PORT=8010

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

say() { printf '[install] %s\n' "$1"; }

if [ "$(id -u)" -ne 0 ]; then
  echo "this script has to run as root" >&2
  exit 1
fi

say "creating the service user"
if ! id -u "$SERVICE_USER" >/dev/null 2>&1; then
  useradd --system --home-dir "$STATE_DIR" --shell /usr/sbin/nologin "$SERVICE_USER"
fi

say "installing the application into $APP_DIR"
mkdir -p "$APP_DIR"
cp "$SOURCE_DIR/main.py" "$APP_DIR/"
cp -r "$SOURCE_DIR/harness" "$APP_DIR/"
cp "$SOURCE_DIR/requirements.txt" "$APP_DIR/"

say "creating a virtual environment"
python3 -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/pip" install --quiet --upgrade pip
"$APP_DIR/.venv/bin/pip" install --quiet -r "$APP_DIR/requirements.txt"

say "preparing the state directory"
mkdir -p "$STATE_DIR"
chown -R "$SERVICE_USER:$SERVICE_USER" "$STATE_DIR" "$APP_DIR"

say "preparing the configuration directory"
mkdir -p "$CONF_DIR"
if [ ! -f "$CONF_DIR/env" ]; then
  # A random value, generated once and never printed.
  GENERATED="$(head -c 32 /dev/urandom | base64 | tr -d '\n')"
  printf 'HARNESS_SECRET=%s\n' "$GENERATED" > "$CONF_DIR/env"
  chmod 0640 "$CONF_DIR/env"
  chown root:"$SERVICE_USER" "$CONF_DIR/env"
  say "generated a new secret in $CONF_DIR/env"
else
  say "keeping the existing secret in $CONF_DIR/env"
fi

say "installing the systemd unit"
install -m 0644 "$SOURCE_DIR/deploy/harness.service" /etc/systemd/system/harness.service

systemctl daemon-reload
systemctl enable harness.service
systemctl restart harness.service

say "waiting for the service to answer"
for _ in $(seq 1 30); do
  if curl -fsS "http://127.0.0.1:${SERVICE_PORT}/health" >/dev/null 2>&1; then
    say "the service is up on 127.0.0.1:${SERVICE_PORT}"
    break
  fi
  sleep 1
done

say "mint the first admin token"
say "  sudo -u $SERVICE_USER env HARNESS_SECRET=\$(grep -oP '(?<=^HARNESS_SECRET=).*' $CONF_DIR/env) \\"
say "    /opt/agent-harness/.venv/bin/python -m harness.authz root admin"
