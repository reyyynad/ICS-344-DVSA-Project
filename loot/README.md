# Loot Directory (Sanitized Evidence)

## Overview
This directory contains evidence collected from successful exploitation.

## Lesson 1
- CloudWatch logs showing code execution

## Lesson 2
- Forged JWT tokens
- Unauthorized responses

## Lesson 3
- Signed S3 receipt URL obtained with no authorization
- Terminal output confirming direct Lambda invocation with no auth check
- Verification output showing fix blocks unauthorized access

## Lesson 5
- Order receipt showing status: paid, total: $0, token: FREE_RIDE_TOKEN
- CloudWatch evidence confirming DVSA-ADMIN-UPDATE-ORDERS invoked by regular user
- Exploit payload used to trigger the access control bypass

## Lesson 7
- Outputs from privileged Lambda invocation

## Lesson 8
- Terminal output confirming race condition succeeded
- Order record showing 5 items received but only $40 charged
- Verification output showing fix blocks updates on in-progress orders

## Lesson 9
- Vulnerability scan results

## Team Sections
- Lesson 4: [To be added]
- Lesson 6: [To be added]
- Lesson 10: [To be added]