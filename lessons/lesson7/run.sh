#!/bin/bash
# =============================================================
# Lesson 7 - Demonstrate the over-privileged function role.
#
# Usage:
#   aws configure          # once
#   export ROLE_ARN="arn:aws:iam::YOUR_ACCOUNT_ID:role/DVSA-SEND-RECEIPT-EMAIL-Role"
#   bash run.sh
# =============================================================
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"

if [ -z "${ROLE_ARN:-}" ]; then
  echo "ERROR: set ROLE_ARN env var first." >&2
  echo '  export ROLE_ARN="arn:aws:iam::YOUR_ACCOUNT_ID:role/DVSA-SEND-RECEIPT-EMAIL-Role"' >&2
  exit 1
fi

echo "============================================"
echo " Lesson 7: Over-Privileged Function Check"
echo " Role: $ROLE_ARN"
echo "============================================"

python3 -c "import boto3" 2>/dev/null || pip install boto3 --break-system-packages --quiet

# Prove over-privilege via IAM Policy Simulator
python3 "$HERE/exploit.py"

echo ""
echo "Console-based follow-up (screenshot these for the loot folder):"
echo "  1. IAM -> Roles -> $(basename "$ROLE_ARN") -> Permissions tab"
echo "  2. https://policysim.aws.amazon.com/ -> test:"
echo "      s3:GetObject on arn:aws:s3:::some-random-bucket/some-key  -> ALLOWED"
echo "      dynamodb:Scan on arn:aws:dynamodb:us-east-1:*:table/some-table -> ALLOWED"
echo "  3. Enable a CloudTrail, place an order, wait 15 min,"
echo "     then IAM -> Role -> Generate Policy -> Last 1 day"
echo "     Compare generated (~3 actions) vs attached (dozens)."
