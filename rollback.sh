#!/bin/bash
# ============================================================
# Rollback — Redeploy a previous image by its commit SHA
#
# Usage:
#   ./rollback.sh abc123def456...
#
# How to find old SHAs:
#   - GitHub → Actions tab → click any past run → see the SHA
#   - Or run: git log --oneline
# ============================================================
set -e

if [ -z "$1" ]; then
  echo "Usage: ./rollback.sh <commit-sha>"
  echo "Example: ./rollback.sh a1b2c3d4e5f6"
  exit 1
fi

SHA=$1
cd ~/tasks-api

echo "===> Rolling back to image tag: $SHA"
export TAG=$SHA
docker compose pull api
docker compose up -d

echo "===> ✅ Rollback complete. Running image:"
docker ps --format "table {{.Image}}\t{{.Status}}"
