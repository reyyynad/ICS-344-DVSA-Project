# ICS 344 - DVSA Project | OWASP Serverless Top 10

**Team Members:**
- Raghad Almaghrabi (202156390)
- Renad Adel (202276760)
- Shatha Alharbi (202283660)

This repository documents the exploitation and remediation of the first **10 security vulnerabilities** identified in the **DVSA (Damn Vulnerable Serverless Application)** as part of the ICS 344 course project.

The project demonstrates practical hands-on experience with common security issues in modern **serverless architectures** on AWS, following the **OWASP Serverless Top 10** guidelines.

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Covered Vulnerabilities](#covered-vulnerabilities)
- [Environment](#environment)
- [Lessons](#lessons)
- [Repository Structure](#repository-structure)
- [Key Takeaways](#key-takeaways)

---

## Project Overview

This project involved identifying, exploiting, documenting, and fixing **10 critical security vulnerabilities** in a serverless e-commerce application (DVSA) deployed on AWS. Each lesson follows a structured approach including:

- Vulnerability summary and impact
- Root cause analysis
- Reproduction steps with evidence
- Fix strategy and code/configuration changes
- Post-fix verification
- Security analysis tables
- Lessons learned

---

## Covered Vulnerabilities (Lessons 1–10)

| # | Lesson | Vulnerability | OWASP Category |
|---|--------|---------------|----------------|
| 1 | Event Injection | **Remote Code Execution (RCE)** via unsafe deserialization (`node-serialize`) | Injection |
| 2 | Broken Authentication | **JWT Signature Bypass** – trusting payload without verification | Identification and Authentication Failures |
| 3 | Sensitive Data Exposure | Unauthorized direct invocation of admin Lambda exposing all receipts | Sensitive Data Exposure |
| 4 | Insecure Cloud Configuration | Public S3 bucket + Path Traversal in Lambda | Security Misconfiguration |
| 5 | Broken Access Control | Privilege Escalation via Event Injection + Over-privileged IAM role | Broken Access Control |
| 6 | Denial of Service (DoS) | Missing API Gateway throttling leading to Lambda exhaustion | Denial of Service |
| 7 | Over-Privileged Functions | Lambda execution role with wildcard IAM permissions | Security Misconfiguration |
| 8 | Logic Vulnerabilities | Race Condition allowing payment for more items than charged | Business Logic Vulnerability |
| 9 | Vulnerable Dependencies | Use of insecure `node-serialize` package (RCE) | Vulnerable and Outdated Components |
|10 | Unhandled Exceptions | Stack trace and internal path exposure via uncaught `KeyError` | Security Misconfiguration |

---

## Environment

- **Platform**: AWS Serverless (API Gateway + Lambda + DynamoDB + S3 + Cognito)
- **Backend**: Node.js & Python Lambda functions
- **Region**: Primarily `us-east-1` (some components in `eu-north-1`)
- **DVSA URL**: Deployed DVSA instance provided by the course

---

## Lessons

Each lesson is fully documented with:

- **Goal & Vulnerability Summary**
- **Root Cause**
- **Reproduction Steps** + Screenshots
- **Evidence & Proof**
- **Fix Strategy**
- **Code / Config Changes**
- **Verification After Fix**
- **Structured Security Analysis** (Table A & B)
- **Takeaways & Lessons Learned**

Detailed reports for all 10 lessons are available in the [`docs/`](./docs/) or [`report/`](./report/) directory (or see the main project report: `ICS 344 project BACKUP.docx`).

---

## Repository Structure

```
ICS-344-DVSA-Project/
├── README.md
├── docs/                  # Individual lesson reports (Markdown/PDF)
├── screenshots/           # Evidence screenshots
├── code/                  # Vulnerable vs Fixed code snippets
├── report/                # Full project report (DOCX + PDF)
└── analysis/              # Security analysis tables
```

---

## Key Takeaways

- Serverless does **not** mean "secure by default".
- Every Lambda function is its own security boundary.
- **Never trust** client input, JWT payloads, or deserialized data without proper validation.
- Apply **least privilege** strictly to IAM roles and resource policies.
- Always implement proper **input validation**, **error handling**, and **rate limiting**.
- Logging and monitoring must be actively configured — logs alone are not monitoring.

This project significantly improved our understanding of cloud-native security challenges and best practices for securing serverless applications.

---

## Acknowledgments

- Course: ICS 344 – Cloud Computing Security
- Instructor: Waleed Algobi
- Application: Damn Vulnerable Serverless Application (DVSA)
- Team members: Raghad Almaghrabi · Renad Adel · Shatha Alharbi


---

**Repository**: [https://github.com/reyyynad/ICS-344-DVSA-Project](https://github.com/reyyynad/ICS-344-DVSA-Project)

Made with ❤️ by Team DVSA | April 2026

