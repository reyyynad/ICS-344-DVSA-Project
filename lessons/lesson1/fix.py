#!/usr/bin/env python3
"""
Lesson 1 - Mitigation helper.

The actual fix lives in the Lambda source (Node.js), but this script:
  1. Prints the exact patch to apply to DVSA-ORDER-MANAGER/order-manager.js.
  2. Can optionally patch a local copy of order-manager.js in place.

Usage:
    python3 fix.py                      # print the patch
    python3 fix.py path/to/order-manager.js   # patch the file in place
"""

import sys
from pathlib import Path

# ==============================================================
# PATCH #1 - Input validation (drop in after `var req = ...`)
# ==============================================================
INPUT_VALIDATION_JS = r"""
// --- BEGIN Lesson 1 fix: block node-serialize RCE marker ---
if (typeof req.action !== "string" || req.action.includes("_$$ND_FUNC$$_")) {
    return callback(null, {
        statusCode: 400,
        body: JSON.stringify({ message: "Malicious input detected" })
    });
}
// --- END Lesson 1 fix ---
""".strip()

# ==============================================================
# PATCH #2 - Remove node-serialize entirely, use JSON.parse
# ==============================================================
PARSER_FIX_JS = r"""
// BEFORE (vulnerable):
//   var serialize = require('node-serialize');
//   var req = serialize.unserialize(event.body);
//
// AFTER (safe):
var req = JSON.parse(event.body);
""".strip()


def print_patch() -> None:
    print("=" * 64)
    print(" Lesson 1 - Fix for DVSA-ORDER-MANAGER / order-manager.js")
    print("=" * 64)
    print()
    print("[1] Replace the node-serialize parser with JSON.parse:")
    print()
    print(PARSER_FIX_JS)
    print()
    print("[2] Add an input-validation guard right after the parse:")
    print()
    print(INPUT_VALIDATION_JS)
    print()
    print("[3] Remove node-serialize from package.json, reinstall, redeploy:")
    print("    npm uninstall node-serialize")
    print("    rm -rf node_modules package-lock.json && npm install")
    print("    zip -r order-manager.zip .")
    print("    aws lambda update-function-code \\")
    print("        --function-name DVSA-ORDER-MANAGER \\")
    print("        --zip-file fileb://order-manager.zip")


def patch_file(target: Path) -> int:
    if not target.exists():
        sys.stderr.write(f"ERROR: {target} not found.\n")
        return 1
    src = target.read_text(encoding="utf-8")

    if "JSON.parse(event.body)" in src and "_$$ND_FUNC$$_" in src:
        print("[+] File already contains both fixes - nothing to do.")
        return 0

    patched = src
    patched = patched.replace("var serialize = require('node-serialize');", "")
    patched = patched.replace("serialize.unserialize(event.body)", "JSON.parse(event.body)")
    patched = patched.replace("serialize.unserialize(body)", "JSON.parse(body)")

    # Insert the validation guard after the first `var req = JSON.parse(event.body);`
    marker = "var req = JSON.parse(event.body);"
    if marker in patched and "_$$ND_FUNC$$_" not in patched:
        patched = patched.replace(
            marker,
            marker + "\n" + INPUT_VALIDATION_JS,
            1,
        )

    target.write_text(patched, encoding="utf-8")
    print(f"[+] Patched {target}")
    return 0


def main() -> int:
    if len(sys.argv) == 1:
        print_patch()
        return 0
    return patch_file(Path(sys.argv[1]))


if __name__ == "__main__":
    raise SystemExit(main())
