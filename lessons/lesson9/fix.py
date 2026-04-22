#!/usr/bin/env python3
"""
Lesson 9 - Detect and remediate vulnerable dependencies.

Usage:
    python3 fix.py /path/to/order-manager/package.json
    python3 fix.py            # if package.json is in current dir
"""

import json
import sys
from pathlib import Path

KNOWN_BAD = {
    "node-serialize": "CVE-2017-5941 (RCE via unserialize)",
}

AFTER_PACKAGE_JSON = """\
{
  "name": "order-manager",
  "version": "1.0.1",
  "main": "order-manager.js",
  "dependencies": {
    "node-jose": "^2.2.0"
  }
}
"""


def main() -> int:
    target = Path(sys.argv[1] if len(sys.argv) > 1 else "package.json")
    if not target.exists():
        sys.stderr.write(f"ERROR: {target} not found.\n")
        sys.stderr.write("Point this script at the Lambda's package.json.\n")
        return 1

    pkg = json.loads(target.read_text(encoding="utf-8"))
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

    print("=" * 64)
    print(f" Lesson 9 - Scan {target}")
    print("=" * 64)

    bad = [(name, ver, KNOWN_BAD[name]) for name, ver in deps.items() if name in KNOWN_BAD]

    if not bad:
        print("[+] No known-bad packages found in dependencies.")
        return 0

    print("[!] VULNERABLE PACKAGES DETECTED:")
    for name, ver, cve in bad:
        print(f"    - {name} @ {ver}   -->  {cve}")
    print()
    print("Remediation steps:")
    print("  1. cd into the Lambda source folder (where package.json lives).")
    print("  2. Remove the package:")
    for name, _, _ in bad:
        print(f"       npm uninstall {name}")
    print("  3. Replace any `require('node-serialize')` + `.unserialize()` usage")
    print("     with `JSON.parse()` in the Node.js source (see lesson1/fix.py).")
    print("  4. Rebuild and redeploy:")
    print("       rm -rf node_modules package-lock.json && npm install")
    print("       zip -r order-manager.zip .")
    print("       aws lambda update-function-code \\")
    print("           --function-name DVSA-ORDER-MANAGER \\")
    print("           --zip-file fileb://order-manager.zip")
    print("  5. Audit regularly:")
    print("       npm audit --production --audit-level=high")
    print()
    print("Target state for package.json (copy/paste and re-pin versions):")
    print(AFTER_PACKAGE_JSON)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
