#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

# Start all services concurrently with pm2
pm2 delete gateway job-hunter web mirror-service 2>/dev/null || true

pm2 start "uv run uvicorn ironclaw.main:app --reload --host 127.0.0.1 --port 8000" \
	--name gateway \
	--cwd "$ROOT/apps/gateway"

pm2 start "uv run python -m job_hunter.main web" \
	--name job-hunter \
	--cwd "$ROOT/apps/job-hunter"

pm2 start "npm run dev" \
	--name web \
	--cwd "$ROOT/apps/web"

pm2 start "npm run start:webrtc" \
	--name mirror-service \
	--cwd "$ROOT/apps/mirror-service"

pm2 save
pm2 status
