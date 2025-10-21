#!/usr/bin/env bash
set -euo pipefail

# Deploy script for server (Debian/Ubuntu).
# Usage: sudo ./deploy_server.sh [repo_url] [branch]
# Example: sudo ./deploy_server.sh https://github.com/petroslobodenuik-ui/project.git main

REPO_URL=${1:-https://github.com/petroslobodenuik-ui/project.git}
BRANCH=${2:-main}
APP_DIR=${3:-/opt/humanitarian-app}
APP_PORT=${4:-8080}
PORTAINER_PORT=${5:-9000}

echo "Deploying project from ${REPO_URL} (branch ${BRANCH}) to ${APP_DIR}"

if [ "$EUID" -ne 0 ]; then
  echo "This script must be run as root (or via sudo)" >&2
  exit 1
fi

mkdir -p "$APP_DIR"
chown "$SUDO_USER":"$SUDO_USER" "$APP_DIR" || true

echo "Installing prerequisites..."
if command -v apt-get >/dev/null 2>&1; then
  apt-get update
  apt-get install -y ca-certificates curl gnupg lsb-release git
  # Install Docker (official script)
  if ! command -v docker >/dev/null 2>&1; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
  fi
  # Ensure docker compose plugin (modern Docker provides `docker compose`)
  apt-get install -y docker-compose-plugin || true
elif command -v yum >/dev/null 2>&1; then
  # RHEL/CentOS
  yum install -y yum-utils
  yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
  yum install -y docker-ce docker-ce-cli containerd.io
  systemctl enable --now docker
else
  echo "Unsupported package manager. Please install Docker and git manually." >&2
fi

echo "Adding $SUDO_USER to docker group"
usermod -aG docker "$SUDO_USER" || true

echo "Cloning or updating repository"
if [ -d "$APP_DIR/.git" ]; then
  cd "$APP_DIR"
  git fetch origin
  git checkout "$BRANCH"
  git pull origin "$BRANCH"
else
  rm -rf "$APP_DIR"/*
  git clone --depth 1 --branch "$BRANCH" "$REPO_URL" "$APP_DIR"
fi

cd "$APP_DIR"

echo "Ensuring production port mapping (host:${APP_PORT} -> container:8080)"
# create a simple override compose file to publish the requested port
cat > docker-compose.prod.yml <<EOF
version: '3.8'
services:
  app:
    ports:
      - "${APP_PORT}:8080"
    restart: always
EOF

echo "Pulling/building and starting containers"
docker compose -f docker-compose.yml -f docker-compose.prod.yml pull --ignore-pull-failures || true
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

echo "Optionally installing Portainer (if not present)"
if ! docker ps --format '{{.Names}}' | grep -q portainer; then
  docker volume create portainer_data || true
  docker run -d -p ${PORTAINER_PORT}:9000 -p 8080:8080 --name portainer --restart=always \
    -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latest
fi

echo "Allow firewall ports (ufw) if available: ${APP_PORT}, ${PORTAINER_PORT}"
if command -v ufw >/dev/null 2>&1; then
  ufw allow ${APP_PORT}/tcp || true
  ufw allow ${PORTAINER_PORT}/tcp || true
fi

echo "Deployment finished. App should be accessible at http://$(hostname -I | awk '{print $1}'):${APP_PORT} (or by server IP)."
echo "If you changed user groups, you may need to re-login to apply docker group membership for $SUDO_USER."
