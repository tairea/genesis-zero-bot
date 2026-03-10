#!/usr/bin/env bash
# setup.sh — Deploy the live knowledge graph server on Hetzner
# Run this ON the server: bash ~/.openclaw/workspace-genesis/skills/semantic-graph/deploy/setup.sh
set -euo pipefail

DEPLOY_DIR="$HOME/.openclaw/workspace-genesis/skills/semantic-graph/deploy"
DOMAIN="graph.regentribe.org"

echo "=== 1/4 Install nginx site config ==="
sudo cp "$DEPLOY_DIR/nginx-graph.regentribe.org" "/etc/nginx/sites-available/$DOMAIN"
sudo ln -sf "/etc/nginx/sites-available/$DOMAIN" "/etc/nginx/sites-enabled/"
sudo nginx -t
echo "  OK"

echo ""
echo "=== 2/4 Get SSL certificate ==="
sudo certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --redirect -m ian@regentribe.org
echo "  OK"

echo ""
echo "=== 3/4 Reload nginx ==="
sudo systemctl reload nginx
echo "  OK"

echo ""
echo "=== 4/4 Install and start systemd service ==="
sudo cp "$DEPLOY_DIR/graph-live.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now graph-live
echo "  OK"

echo ""
echo "=== Done ==="
echo "  WebSocket: wss://$DOMAIN/ws"
echo "  Frontend:  https://$DOMAIN/"
echo ""
systemctl status graph-live --no-pager
