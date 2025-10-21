#!/usr/bin/env bash
# Simple helper to call the Portainer webhook stored in PORTAINER_WEBHOOK_URL env var
set -euo pipefail

if [ -z "${PORTAINER_WEBHOOK_URL:-}" ]; then
  echo "PORTAINER_WEBHOOK_URL environment variable not set"
  exit 2
fi

echo "Calling Portainer webhook..."
curl -fsS -X POST "$PORTAINER_WEBHOOK_URL"
echo "Done."
