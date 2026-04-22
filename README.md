# ICS 344 — DVSA Project

A full walkthrough of **all 10 vulnerability classes** in the **Damn Vulnerable Serverless Application (DVSA)** deployed on AWS. Runnable exploit code, parameterized payloads, and ready-to-apply fixes are included for the lessons this repo implements directly (**1, 2, 3, 4, 5, 6, 7, 8, 9, 10**), which are documented below with their targets, primitives, and mitigations.

> **Course:** ICS 344 — Information & Computer Security
> **Educational use only.** Every script targets a DVSA instance you personally own in your own AWS account.

---

## 1. The ten lessons at a glance

| # | Vulnerability | Target | Attack primitive | Impact |
|---|---|---|---|---|
| 1 | Event Injection (RCE) | `DVSA-ORDER-MANAGER` Lambda | `node-serialize` `_$$ND_FUNC$$_` payload | Arbitrary code execution in the Lambda runtime |
| 2 | Broken Authentication | `DVSA-ORDER-MANAGER` Lambda | JWT payload forgery — signature never verified | Impersonate any user, read their orders/PII |
| 3 | Sensitive Data Exposure | `DVSA-ADMIN-GET-RECEIPT` Lambda + `dvsa-receipts-bucket` S3 | Direct `aws lambda invoke` returns a signed URL to a ZIP of **every** receipt for a given day | Full disclosure of all customers' receipts, addresses, and payment records |
| 4 | Insecure Cloud Configuration | `DVSA-ADMIN-SHELL` Lambda + `dvsa-receipts-bucket` S3 | S3 "Block Public Access" disabled + path traversal via `body.file` (`"../../etc/passwd"`) | Arbitrary file read inside the Lambda filesystem; RCE via `eval(body.cmd)` |
| 5 | Broken Access Control | `DVSA-ADMIN-UPDATE-ORDERS` Lambda | Lambda decodes JWT but only reads `username`; never checks `cognito:groups` | Non-admin user flips their own order from `processed (200)` to `paid (120)` — skips payment |
| 6 | Denial of Service | API Gateway stage → `DVSA-ORDER-MANAGER` | No throttling / rate-limiting → 800 concurrent POSTs saturate Lambda concurrency | Legitimate users throttled out; surprise AWS bill |
| 7 | Over-Privileged Function | `DVSA-SEND-RECEIPT-EMAIL` IAM role | `AmazonSESFullAccess` + wildcard `Resource:"*"` inline policies on S3 and DynamoDB | Any compromise of this function = full S3 + DynamoDB blast radius |
| 8 | Logic Vulnerability (Race) | `DVSA-ORDER-COMPLETE` vs `DVSA-ORDER-UPDATE` | Race between payment-finalize and item-list-update; no pessimistic/conditional lock | Pay for 1 item, receive 5 |
| 9 | Vulnerable & Outdated Components | `node-serialize@0.0.4` dependency | CVE-2017-5941 (same RCE as Lesson 1, supply-chain angle) | RCE in the Lambda runtime |
| 10 | Unhandled Exceptions | `DVSA-ORDER-BILLING` / `order_billing.py` | `event["orderId"]` accessed without validation → raw `KeyError` stack trace returned to client | Leaks internal file paths / code structure for reconnaissance |

**Bold implementation status**

| # | Code in this repo? | Evidence in `loot/`? |
|---|---|---|
| 1 | ✅ `lessons/lesson1/` | ✅ `pwned.txt` + CloudWatch screenshots |
| 2 | ✅ `lessons/lesson2/` | ✅ forged-token example + response screenshots |
| 3 | ✅ `lessons/lesson3/`  | — |
| 4 | ✅ `lessons/lesson4/`  | — |
| 5 | ✅ `lessons/lesson5/`  | — |
| 6 | ✅ `lessons/lesson6/`  | — |
| 7 | ✅ `lessons/lesson7/` | ✅ Policy Simulator + CloudTrail screenshots |
| 8 | ✅ `lessons/lesson8/`  | — |
| 9 | ✅ `lessons/lesson9/` | ✅ `npm audit` + RCE reproduction |
| 10 | ✅ `lessons/lesson10/`  | — |

Each implemented lesson ships with four files: `payload.json`, `exploit.py`, `run.sh`, `fix.py` (consistent shape across all four).

---

## 2. Repository layout

```
ICS-344-DVSA-Project/
├── README.md                     ← you are here
├── .gitignore
├── config/                       ← shared config / env templates
├── lessons/
│   ├── lesson1/   { payload.json, exploit.py, fix.py, run.sh }
│   ├── lesson2/   { payload.json, exploit.py, fix.py, run.sh }
│   ├── lesson3/   ... (team documentation — walkthrough in PDF / live demos)
│   ├── lesson4/   ...
│   ├── lesson5/   ...
│   ├── lesson6/   ...
│   ├── lesson7/   { payload.json, exploit.py, fix.py, run.sh }
│   ├── lesson8/   ...
│   ├── lesson9/   { payload.json, exploit.py, fix.py, run.sh }
│   └── lesson10/  ...
├── live demos (lessons 1-10)/    ← video / screen recordings per lesson
├── loot/                         ← sanitized evidence
│   ├── README.md                 ← screenshot guide + sanitization checklist
│   ├── lesson1/ { pwned.txt, cloudwatch_evidence.txt, *.png }
│   ├── lesson2/ { forged_token_example.txt, forged_response.json, *.png }
│   ├── lesson7/ { *.png }
│   └── lesson9/ { pwned.txt, npm_audit_example.txt, *.png }
├── screenshots/                  ← shared / cross-lesson screenshots
├── requirements.txt
└── run_all.sh                    ← optional: runs every implemented lesson end-to-end
```

---

## 3. Prerequisites

- `bash`, `curl`, `python3` (≥ 3.8)
- AWS CLI + console access to **your own** DVSA deployment
- A DVSA user account (Lesson 2 needs a starter JWT from your own login)
- `boto3` (Lesson 7 only): `pip install boto3 --break-system-packages`

---

## 4. Quick-start — implemented lessons

All inputs flow through environment variables so nothing sensitive gets committed.

### Lesson 1 — Event Injection (RCE)

```bash
export API="https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/Stage/order"
cd lessons/lesson1
bash run.sh                     # or: python3 exploit.py
python3 fix.py                  # prints the Node.js patch to apply to order-manager.js
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
**Evidence:** `loot/lesson2/forged_response.json` contains the victim's data.

### Lesson 7 — Over-Privileged Function

```bash
aws configure                    # once, with your DVSA account credentials
pip install boto3 --break-system-packages
export ROLE_ARN="arn:aws:iam::YOUR_ACCOUNT_ID:role/DVSA-SEND-RECEIPT-EMAIL-Role"

cd lessons/lesson7
bash run.sh                      # simulates actions via IAM Policy Simulator

# Apply the least-privilege policy (dry-run first):
export ROLE_NAME="DVSA-SEND-RECEIPT-EMAIL-Role"
export BUCKET="your-real-dvsa-receipts-bucket"
export ACCOUNT_ID="123456789012"
python3 fix.py                   # dry-run: prints what would change
python3 fix.py --apply           # actually attaches the scoped policy
```
**Evidence:** Policy Simulator screenshots + `exploit.py` output listing over-privileged actions.

### Lesson 9 — Vulnerable Dependencies

```bash
export API="https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/Stage/order"
# optional: export LAMBDA_SRC="/path/to/DVSA-ORDER-MANAGER"

cd lessons/lesson9
bash run.sh                      # fires the RCE + runs npm audit if LAMBDA_SRC is set
python3 fix.py /path/to/DVSA-ORDER-MANAGER/package.json
```
**Evidence:** `npm audit` flags `node-serialize` / CVE-2017-5941 as critical.

---

## . Documented-only lessons (3, 4, 5, 6, 8, 10)

this needs to be moved up 
---

## 5. Mitigation summary (implemented lessons)

| # | Remediation file | What it does |
|---|---|---|
| 1 | `lessons/lesson1/fix.py` | Prints the Node.js patch: replace `node-serialize.unserialize()` with `JSON.parse()` + reject strings containing `_$$ND_FUNC$$_`. |
| 2 | `lessons/lesson2/fix.py` | Prints the JWKS-verification helpers (`verifyCognitoJwt`) and the replacement handler block that uses verified claims. |
| 3 |
| 4 |
| 5 |
| 6 |
| 7 | `lessons/lesson7/fix.py` | Attaches a least-privilege inline policy (`payload.json`) to the role and lists managed policies to detach. |
| 8 |
| 9 | `lessons/lesson9/fix.py` | Reads the Lambda's `package.json`, flags `node-serialize`, prints `npm uninstall` + redeploy commands. |
| 10 |

Before deploying any IAM policy, replace `YOUR-DVSA-RECEIPTS-BUCKET` and `YOUR_ACCOUNT_ID` via the `BUCKET` and `ACCOUNT_ID` env vars.

---

## 6. Safety & disclosure

DVSA is an intentionally vulnerable lab application. Do not run these scripts against any system you do not own. The team takes no responsibility for misuse.
