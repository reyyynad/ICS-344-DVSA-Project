#!/usr/bin/env python3
"""
Lesson 6 - Mitigation helper.

The fix is a pure AWS infrastructure change — no Lambda code to modify.
This script prints the exact AWS CLI commands to enable stage-level
throttling on the DVSA API Gateway dvsa stage.

Usage:
    python3 fix.py                  # print the fix steps
    python3 fix.py --apply          # apply via AWS CLI (requires aws configured)
"""

import os
import subprocess
import sys

# ---------------------------------------------------------------
# Target values (match what is documented in the report Part 7)
# ---------------------------------------------------------------
REST_API_ID = os.environ.get("REST_API_ID", "yi8ph319ja")
STAGE_NAME  = os.environ.get("STAGE_NAME",  "dvsa")
RATE_LIMIT  = 100   # requests per second
BURST_LIMIT = 50    # concurrent requests


def print_fix() -> None:
    print("=" * 64)
    print(" Lesson 6 - Fix: Enable API Gateway Stage-Level Throttling")
    print("=" * 64)
    print()
    print("The vulnerability: API Gateway dvsa stage has no throttling.")
    print("AWS default settings (Rate=10,000 / Burst=5,000) allow flooding.")
    print()
    print("[1] Enable throttling via AWS Console:")
    print("    API Gateway -> DVSA-APIs -> Stages -> dvsa -> Edit")
    print(f"      Throttling : Enabled")
    print(f"      Rate       : {RATE_LIMIT} requests/second")
    print(f"      Burst      : {BURST_LIMIT} requests")
    print("    Click Save.")
    print()
    print("[2] Or apply via AWS CLI:")
    print(f"    aws apigateway update-stage \\")
    print(f"        --rest-api-id {REST_API_ID} \\")
    print(f"        --stage-name {STAGE_NAME} \\")
    print(f"        --patch-operations \\")
    print(f'            op=replace,path=/defaultRouteSettings/throttlingRateLimit,value={RATE_LIMIT} \\')
    print(f'            op=replace,path=/defaultRouteSettings/throttlingBurstLimit,value={BURST_LIMIT}')
    print()
    print("[3] Optional additional mitigations:")
    print("    - Attach a Usage Plan to the API stage")
    print("    - Enable AWS WAF rate-based rules on the API Gateway")
    print()
    print("Verify: re-run exploit.py — responses should now include HTTP 429")
    print("        and CloudWatch Invocations graph should remain flat.")


def apply_fix() -> int:
    print(f"[*] Applying throttling (Rate={RATE_LIMIT}, Burst={BURST_LIMIT}) "
          f"to stage '{STAGE_NAME}' of API '{REST_API_ID}' ...")
    cmd = [
        "aws", "apigateway", "update-stage",
        "--rest-api-id", REST_API_ID,
        "--stage-name", STAGE_NAME,
        "--patch-operations",
        f"op=replace,path=/defaultRouteSettings/throttlingRateLimit,value={RATE_LIMIT}",
        f"op=replace,path=/defaultRouteSettings/throttlingBurstLimit,value={BURST_LIMIT}",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print("[+] Throttling applied successfully.")
        print(f"    Rate  = {RATE_LIMIT} req/sec")
        print(f"    Burst = {BURST_LIMIT}")
        return 0
    else:
        sys.stderr.write(f"ERROR: {result.stderr}\n")
        return 1


def main() -> int:
    if "--apply" in sys.argv:
        return apply_fix()
    print_fix()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
