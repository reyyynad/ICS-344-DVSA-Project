#!/usr/bin/env python3
"""
Lesson 7 - Remediation.

Replaces the role's overly broad inline policies with the least-privilege
policy in payload.json, and prints manual follow-up steps for detaching
managed policies (AmazonSESFullAccess, etc.).

Usage:
    export ROLE_NAME="DVSA-SEND-RECEIPT-EMAIL-Role"
    export BUCKET="my-real-dvsa-receipts-bucket"
    export ACCOUNT_ID="123456789012"
    python3 fix.py                 # dry-run: print what would happen
    python3 fix.py --apply         # actually call IAM to attach new policy
"""

import json
import os
import sys
from pathlib import Path

try:
    import boto3
except ImportError:
    sys.stderr.write("ERROR: boto3 not installed. Run: pip install boto3\n")
    sys.exit(1)

HERE = Path(__file__).resolve().parent
POLICY_FILE = HERE / "payload.json"
POLICY_NAME = "DVSA-SendReceiptEmail-LeastPrivilege"

MANAGED_TO_DETACH = [
    "arn:aws:iam::aws:policy/AmazonSESFullAccess",
    # Add any other overly broad managed policies you find on the role:
    # "arn:aws:iam::aws:policy/AmazonS3FullAccess",
    # "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess",
]


def render_policy() -> dict:
    bucket = os.environ.get("BUCKET", "YOUR-DVSA-RECEIPTS-BUCKET")
    account_id = os.environ.get("ACCOUNT_ID", "YOUR_ACCOUNT_ID")
    text = POLICY_FILE.read_text(encoding="utf-8")
    text = text.replace("YOUR-DVSA-RECEIPTS-BUCKET", bucket)
    text = text.replace("YOUR_ACCOUNT_ID", account_id)
    return json.loads(text)


def main() -> int:
    apply = "--apply" in sys.argv
    role_name = os.environ.get("ROLE_NAME", "").strip()
    if not role_name:
        sys.stderr.write("ERROR: set ROLE_NAME env var.\n")
        return 1

    policy = render_policy()

    print("=" * 64)
    print(f" Lesson 7 - Scope down role: {role_name}")
    print("=" * 64)
    print()
    print("[1] The least-privilege policy that will be attached:")
    print(json.dumps(policy, indent=2))
    print()
    print("[2] Managed policies to DETACH manually in the console:")
    for arn in MANAGED_TO_DETACH:
        print(f"    - {arn}")
    print()
    print("[3] Inline 'wildcard *' policies: open the role in IAM and delete them.")
    print()

    if not apply:
        print("[*] Dry run. Re-run with --apply to actually modify the role.")
        return 0

    iam = boto3.client("iam")
    print(f"[*] Putting inline policy {POLICY_NAME!r} on {role_name} ...")
    iam.put_role_policy(
        RoleName=role_name,
        PolicyName=POLICY_NAME,
        PolicyDocument=json.dumps(policy),
    )
    print("[+] Done. Re-run exploit.py to confirm the 'abuse' simulations are now DENIED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
