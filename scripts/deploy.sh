#!/usr/bin/env bash
# Permanent deploy to the user's Cloudflare account (not claim-preview).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -z "${CLOUDFLARE_API_TOKEN:-}" ]]; then
  echo "CLOUDFLARE_API_TOKEN is not set." >&2
  echo "Create a token with Account → Cloudflare Workers Scripts:Edit, then:" >&2
  echo "  export CLOUDFLARE_API_TOKEN=..." >&2
  echo "Optional: export CLOUDFLARE_ACCOUNT_ID=..." >&2
  exit 1
fi

python3 scripts/verify.py
npx wrangler deploy
