# Loot — Sanitized Evidence

One sub-folder per lesson. Drop **sanitized** evidence here: stolen files, stack traces, exfiltrated data, and PNG screenshots of the output after running each script/payload.

## What to capture and where it goes

### `loot/lesson1/` — Event Injection

| File | What it proves |
|---|---|
| `pwned.txt` | the file the payload wrote into `/tmp` inside the Lambda (already included) |
| `cloudwatch_evidence.txt` | the exact CloudWatch log line `FILE READ SUCCESS: ...` (template included) |
| `01-terminal-run-exploit.png` | terminal output from `python3 exploit.py` / `bash run.sh` |
| `02-api-response-500.png` | the "Internal server error" response in the terminal |
| `03-cloudwatch-log-file-read-success.png` | CloudWatch log stream showing `FILE READ SUCCESS: ...` |
| `04-lambda-tmp-pwned-file.png` *(optional)* | screenshot from a follow-up RCE listing `/tmp/` |

### `loot/lesson2/` — JWT Forgery

| File | What it proves |
|---|---|
| `forged_token_example.txt` | sanitized before/after of the forged JWT (already included) |
| `forged_response.json` | the victim's data returned by the API after the forgery (auto-saved by `run.sh`, keep a **sanitized** copy) |
| `01-login-as-attacker.png` | DVSA login page signed in as your own attacker account |
| `02-devtools-idtoken.png` | devtools → Local Storage → `CognitoIdentityServiceProvider....idToken` (blur most of the token) |
| `03-exploit-py-forged-token.png` | terminal showing the forged token printed by `exploit.py` |
| `04-curl-returns-victim-data.png` | `curl` or `run.sh` showing victim orders/profile returned |
| `05-decoded-forged-payload.png` *(optional)* | jwt.io or `base64 -d` output showing `"cognito:username":"reyyynad"` |

### `loot/lesson7/` — Over-Privileged Function

| File | What it proves |
|---|---|
| `01-iam-role-permissions.png` | IAM → Roles → DVSA-SEND-RECEIPT-EMAIL-Role → attached policies list (showing AmazonSESFullAccess, wildcard inline policies) |
| `02-policy-simulator-s3-allowed.png` | https://policysim.aws.amazon.com/ — `s3:GetObject` on `arn:aws:s3:::some-random-bucket/some-key` → **ALLOWED** |
| `03-policy-simulator-dynamo-allowed.png` | Policy Simulator — `dynamodb:Scan` on a random table → **ALLOWED** |
| `04-exploit-py-output.png` | terminal from `python3 exploit.py` listing each over-privileged action |
| `05-cloudtrail-generated-policy.png` | IAM → Role → Generate Policy → Last 1 day (only ~3 actions actually used) |
| `06-after-fix-denied.png` | re-run of Policy Simulator/`exploit.py` after `fix.py --apply` → **DENIED** |

### `loot/lesson9/` — Vulnerable Dependencies

| File | What it proves |
|---|---|
| `pwned.txt` | same RCE artifact as Lesson 1 (already included) |
| `npm_audit_example.txt` | `npm audit` flagging node-serialize / CVE-2017-5941 (template included) |
| `01-package-json-before.png` | screenshot of `package.json` showing `"node-serialize": "0.0.4"` |
| `02-npm-audit-critical.png` | `npm audit` terminal output listing the critical vulnerability |
| `03-exploit-reproduces-rce.png` | terminal run of `exploit.py` / `run.sh` triggering the same RCE |
| `04-package-json-after.png` | `package.json` with node-serialize removed |
| `05-npm-audit-clean.png` | `npm audit` clean after the fix |

## Naming convention

- `NN-short-description.png` (zero-padded, kebab-case)
- Use PNG for screenshots (lossless, searchable in GitHub)
- Keep files under ~2 MB each when possible

## Sanitization checklist (before `git add`)

Before every commit, check every screenshot and text file for:

- Real 12-digit AWS account IDs → redact
- Real API Gateway IDs (e.g. `abc123xyz.execute-api...`) → redact
- Real Cognito User Pool IDs (e.g. `us-east-1_AbCdEf012`) → redact
- Real App Client IDs → redact
- Full JWTs → show only first and last 6–10 chars, replace middle with `...`
- Real emails, phone numbers, and student IDs → redact
- Browser bookmarks, other tabs, personal Slack/email → crop out

Preview on macOS: open the PNG → Tools → Annotate → Rectangle (filled, black).

The repo's `.gitignore` blocks `*real_token*`, `*real_jwt*`, and live `forged_response.json`, but screenshots must be sanitized manually.
