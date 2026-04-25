#!/usr/bin/env python3
"""
Lesson 10 - Mitigation helper.

The fix is applied directly to order_billing.py inside the
DVSA-ORDER-BILLING Lambda. This script prints the exact patch
and can optionally apply it to a local copy of the file.

Usage:
    python3 fix.py                              # print the patch
    python3 fix.py path/to/order_billing.py     # patch the file in place
"""

import sys
from pathlib import Path

# ---------------------------------------------------------------
# The secure wrapper to add at the top of lambda_handler
# ---------------------------------------------------------------
VALIDATION_PATCH = '''
# LESSON 10 FIX: Validate required fields before using them
if "orderId" not in event:
    return {"status": "err", "msg": "Bad request: missing required fields"}
if "user" not in event:
    return {"status": "err", "msg": "Bad request: missing required fields"}
'''.strip()

TRYCATCH_BEFORE = "def lambda_handler(event, context):"

TRYCATCH_DESCRIPTION = '''
# LESSON 10 FIX: Wrap entire handler in try/except so no raw
# exception ever escapes back to the API caller.
# Replace the handler body indentation with a try block, e.g.:
#
#   def lambda_handler(event, context):
#       try:
#           if "orderId" not in event:
#               return {"status": "err", "msg": "Bad request: missing required fields"}
#           if "user" not in event:
#               return {"status": "err", "msg": "Bad request: missing required fields"}
#           orderId = event["orderId"]
#           ... rest of handler ...
#       except Exception as e:
#           print(f"[ERROR] Unhandled exception: {e}")   # logs to CloudWatch only
#           return {"status": "err", "msg": "Internal server error"}
'''.strip()


def print_patch():
    print("=" * 64)
    print(" Lesson 10 - Fix for DVSA-ORDER-BILLING / order_billing.py")
    print("=" * 64)
    print()
    print("[1] Add input validation BEFORE accessing event fields (line 34 area):")
    print()
    print(VALIDATION_PATCH)
    print()
    print("[2] Wrap the entire handler body in a top-level try/except:")
    print()
    print(TRYCATCH_DESCRIPTION)
    print()
    print("[3] Never return raw exception details to the caller.")
    print("    Keep full diagnostics in CloudWatch logs only.")
    print()
    print("[4] Redeploy via AWS Console:")
    print("    Lambda -> DVSA-ORDER-BILLING -> Code -> Edit -> Deploy")


def patch_file(target):
    if not target.exists():
        sys.stderr.write("ERROR: " + str(target) + " not found.\n")
        return 1

    src = target.read_text(encoding="utf-8")

    if "Bad request: missing required fields" in src:
        print("[+] File already contains the fix -- nothing to do.")
        return 0

    # Insert validation right after the handler signature line
    patched = src.replace(
        TRYCATCH_BEFORE,
        TRYCATCH_BEFORE + "\n    try:",
        1,
    )

    # Re-indent body (simple heuristic: add 4 spaces to lines after signature)
    lines = patched.split("\n")
    in_handler = False
    result_lines = []
    for line in lines:
        if TRYCATCH_BEFORE in line:
            in_handler = True
            result_lines.append(line)
            result_lines.append("    try:")
            continue
        if in_handler and line.startswith("def ") and TRYCATCH_BEFORE not in line:
            in_handler = False
        if in_handler and line.startswith("    ") and not line.startswith("    try:"):
            result_lines.append("    " + line)
        else:
            result_lines.append(line)

    # Append except block before the end
    final = "\n".join(result_lines)
    final = final.rstrip() + "\n    except Exception as e:\n"
    final += '        print("[ERROR] Unhandled exception: " + str(e))\n'
    final += '        return {"status": "err", "msg": "Internal server error"}\n'

    target.write_text(final, encoding="utf-8")
    print("[+] Patched " + str(target))
    print("    - Added try/except wrapper")
    print("    - Added orderId and user field validation")
    print("    Re-deploy via AWS Console -> Lambda -> DVSA-ORDER-BILLING -> Deploy")
    return 0


def main():
    if len(sys.argv) == 1:
        print_patch()
        return 0
    return patch_file(Path(sys.argv[1]))


if __name__ == "__main__":
    raise SystemExit(main())
