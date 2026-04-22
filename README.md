# ICS 344 — DVSA Project

A walkthrough of four vulnerability classes in the **Damn Vulnerable Serverless Application** (DVSA) deployed on AWS, covering Lessons **1, 2, 7, and 9**. Each lesson ships with a runnable exploit, a parameterized payload, a fix, and sanitized evidence.

> **Course:** ICS 344 — Information & Computer Security
> **Educational use only.** Every script targets a DVSA instance you personally own in your own AWS account.

---

## 1. What's in this repo

| # | Vulnerability                       | Target                              | Attack primitive                           |
|---|-------------------------------------|-------------------------------------|--------------------------------------------|
| 1 | Event Injection (RCE)               | `DVSA-ORDER-MANAGER` Lambda         | `node-serialize` `_$$ND_FUNC$$_` payload   |
| 2 | Broken Authentication               | `DVSA-ORDER-MANAGER` Lambda         | JWT payload forgery (no signature check)   |
| 7 | Over-Privileged Function            | `DVSA-SEND-RECEIPT-EMAIL` IAM role  | IAM Policy Simulator + CloudTrail          |
| 9 | Vulnerable & Outdated Components    | `node-serialize@0.0.4` dependency   | CVE-2017-5941 (same RCE, supply-chain angle) |

Each lesson folder contains four files with a consistent shape:

| File | Purpose |
|---|---|
| `payload.json` | the raw attack payload or policy document — edit-in-place friendly |
| `exploit.py`   | the attack logic in Python (stdlib only, except Lesson 7 which uses `boto3`) |
| `run.sh`       | one-shot bash runner: reads env vars, fires the attack, writes evidence to `loot/` |
| `fix.py`       | prints (and for Lesson 7 applies) the remediation |

Sanitized evidence — the "loot" — lives in `loot/<lessonN>/`. See `loot/README.md` for the screenshot naming + sanitization checklist.

---

## 2. Layout

```
ICS-344-DVSA-Project/
├── README.md                ← you are here
├── .gitignore
├── lessons/
│   ├── lesson1/ { exploit.py, fix.py, payload.json, run.sh }
│   ├── lesson2/ { exploit.py, fix.py, payload.json, run.sh }
│   ├── lesson7/ { exploit.py, fix.py, payload.json, run.sh }
│   └── lesson9/ { exploit.py, fix.py, payload.json, run.sh }
└── loot/
    ├── README.md                         ← screenshot guide + sanitization checklist
    ├── lesson1/ { pwned.txt, cloudwatch_evidence.txt, *.png }
    ├── lesson2/ { forged_token_example.txt, forged_response.json, *.png }
    ├── lesson7/ { *.png }
    └── lesson9/ { pwned.txt, npm_audit_example.txt, *.png }
```

---

## 3. Prerequisites

- `bash`, `curl`, `python3` (≥3.8)
- AWS CLI + console access to **your own** DVSA deployment
- A DVSA user account (needed for Lesson 2 — you need a starter JWT from your own login)
- `boto3` (Lesson 7 only): `pip install boto3 --break-system-packages`

---

## 4. Quick-start

All inputs flow through environment variables so nothing sensitive gets committed.

### Lesson 1 — Event Injection
```bash
export API="https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/Stage/order"
cd lessons/lesson1
bash run.sh                     # or: python3 exploit.py
python3 fix.py                  # prints the Node.js patch
```
**Evidence:** CloudWatch log `FILE READ SUCCESS: You are reading the contents of my hacked file!`

### Lesson 2 — JWT Forgery
```bash
# 1. Log into DVSA as YOUR OWN user, open devtools,
#    copy the idToken from Application → Local Storage
#    (key: CognitoIdentityServiceProvider....idToken).
export TOKEN_B="<your.own.cognito.idToken>"
export VICTIM_USER="reyyynad"
# export VICTIM_SUB="<victim-cognito-sub>"    # optional
export API="https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/Stage/orders"

cd lessons/lesson2
bash run.sh                     # forges + fires + saves response to loot/lesson2/
python3 fix.py                  # prints the JWKS verification patch
```
**Evidence:** response body in `loot/lesson2/forged_response.json` contains the victim's data.

### Lesson 7 — Over-Privileged Function
```bash
aws configure                    # once, with your DVSA account credentials
pip install boto3 --break-system-packages
export ROLE_ARN="arn:aws:iam::YOUR_ACCOUNT_ID:role/DVSA-SEND-RECEIPT-EMAIL-Role"

cd lessons/lesson7
bash run.sh                      # runs exploit.py + prints console follow-up steps

# Apply the fix (dry-run first, then --apply):
export ROLE_NAME="DVSA-SEND-RECEIPT-EMAIL-Role"
export BUCKET="your-real-dvsa-receipts-bucket"
export ACCOUNT_ID="123456789012"
python3 fix.py                   # dry-run: shows what would change
python3 fix.py --apply           # actually attaches the least-privilege policy
```
**Evidence:** IAM Policy Simulator screenshots + `exploit.py` output listing over-privileged actions.

### Lesson 9 — Vulnerable Dependencies
```bash
export API="https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/Stage/order"
# optional: point at a local clone of the Lambda source:
# export LAMBDA_SRC="/path/to/DVSA-ORDER-MANAGER"

cd lessons/lesson9
bash run.sh                      # fires the RCE + runs npm audit if LAMBDA_SRC is set
python3 fix.py /path/to/DVSA-ORDER-MANAGER/package.json
```
**Evidence:** `npm audit` output listing `node-serialize` as critical.

---

## 5. Mitigation summary

| # | Remediation |
|---|---|
| 1 | `fix.py` prints the Node.js patch for `order-manager.js`: replace `node-serialize.unserialize()` with `JSON.parse()` + reject strings containing `_$$ND_FUNC$$_`. |
| 2 | `fix.py` prints the JWKS-verification helpers (`verifyCognitoJwt`, `getCognitoKeystore`) and the replacement handler block that uses **verified** claims. |
| 7 | `payload.json` holds a least-privilege IAM policy. `fix.py --apply` attaches it to the role and tells you which managed policies to detach manually. |
| 9 | `fix.py` reads the Lambda's `package.json`, flags `node-serialize`, and prints the exact `npm uninstall` + redeploy commands. Root cause is the same as Lesson 1. |

Before deploying IAM policies, replace placeholders (`YOUR-DVSA-RECEIPTS-BUCKET`, `YOUR_ACCOUNT_ID`) with real values via the `BUCKET` and `ACCOUNT_ID` env vars.

---

## 6. Safety & disclosure

DVSA is an intentionally vulnerable lab application. Do not run these scripts against any system you don't own. The team takes no responsibility for misuse.
