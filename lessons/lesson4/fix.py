#!/usr/bin/env python3
"""
Lesson 4 - Mitigation helper.

Two fixes required:
  1. Lambda code: add filename validation in admin_shell.js to reject
     any filename containing '..' or '/' (path traversal characters).
  2. S3 bucket: enable Block All Public Access and add a Deny PutObject
     bucket policy to restrict uploads to authorized roles only.

Usage:
    python3 fix.py                          # print both fixes
    python3 fix.py path/to/admin_shell.js   # patch the JS file in place
"""

import json
import sys
from pathlib import Path

# ---------------------------------------------------------------
# Lambda code fix -- add to admin_shell.js before file path use
# ---------------------------------------------------------------
VALIDATION_JS = r"""
// LESSON 4 FIX: Validate filename to prevent path traversal
if (!body.file || body.file.includes('..') || body.file.includes('/')) {
    return callback(null, {
        statusCode: 400,
        body: JSON.stringify({ status: "err", msg: "Invalid filename" })
    });
}
""".strip()

VULNERABLE_LINE = 'const filename = "/tmp/" + body.file; // VULNERABLE'
SAFE_LINE       = 'const filename = "/tmp/" + body.file; // validated above'

# ---------------------------------------------------------------
# S3 bucket policy fix -- replace YOUR_BUCKET and ACCOUNT_ID
# ---------------------------------------------------------------
S3_BUCKET_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "DenyPublicPutObject",
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::YOUR-DVSA-RECEIPTS-BUCKET/*",
            "Condition": {
                "StringNotLike": {
                    "aws:PrincipalArn": [
                        "arn:aws:iam::YOUR_ACCOUNT_ID:role/DVSA-*"
                    ]
                }
            }
        }
    ]
}


def print_fix():
    print("=" * 64)
    print(" Lesson 4 - Fix: Path Traversal + S3 Misconfiguration")
    print("=" * 64)
    print()
    print("[FIX 1] Lambda code fix in admin_shell.js:")
    print("  Add this validation block BEFORE the filename is constructed:")
    print()
    print(VALIDATION_JS)
    print()
    print("  Then change the vulnerable line:")
    print('    BEFORE: ' + VULNERABLE_LINE)
    print('    AFTER : ' + SAFE_LINE)
    print()
    print("[FIX 2] S3 bucket fix — apply via AWS Console:")
    print("  S3 -> dvsa-receipts-bucket -> Permissions ->")
    print("    a) Block Public Access: Enable ALL four checkboxes -> Save")
    print("    b) Bucket Policy: Add the following (replace bucket name and account ID):")
    print()
    print(json.dumps(S3_BUCKET_POLICY, indent=2))
    print()
    print("[FIX 3] Remove or restrict eval(cmd) in admin_shell.js:")
    print("  Remove the eval(cmd) call entirely, or gate it behind a strict admin check.")
    print()
    print("Verify:")
    print("  Re-run exploit.py -- should return 400 'Invalid filename'")
    print("  Try uploading to S3 without an authorized role -- should return AccessDenied")


def patch_file(target):
    if not target.exists():
        sys.stderr.write("ERROR: " + str(target) + " not found.\n")
        return 1

    src = target.read_text(encoding="utf-8")

    if "includes('..')" in src:
        print("[+] File already contains the path traversal fix -- nothing to do.")
        return 0

    patched = src.replace(
        VULNERABLE_LINE,
        VALIDATION_JS + "\n" + SAFE_LINE,
    )

    if patched == src:
        sys.stderr.write(
            "WARNING: Could not find the vulnerable line in the file.\n"
            "Apply the fix manually:\n"
            "  " + VALIDATION_JS.replace("\n", "\n  ") + "\n"
        )
        return 1

    target.write_text(patched, encoding="utf-8")
    print("[+] Patched " + str(target))
    print("    - Added filename validation rejecting '..' and '/'")
    print("    Redeploy via AWS Console -> Lambda -> DVSA-ADMIN-SHELL -> Deploy")
    return 0


def main():
    if len(sys.argv) == 1:
        print_fix()
        return 0
    return patch_file(Path(sys.argv[1]))


if __name__ == "__main__":
    raise SystemExit(main())
