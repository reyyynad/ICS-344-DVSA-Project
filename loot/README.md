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

## Lesson 4
- Terminal output confirming path traversal escaped /tmp/ and returned /etc/passwd contents
- Raw Lambda JSON response containing leaked file contents
- S3 public upload evidence showing unauthenticated PUT accepted before fix and blocked after fix

## Lesson 5
- Order receipt showing status: paid, total: $0, token: FREE_RIDE_TOKEN
- CloudWatch evidence confirming DVSA-ADMIN-UPDATE-ORDERS invoked by regular user
- Exploit payload used to trigger the access control bypass

## Lesson 6
- Flood results showing 200 concurrent requests with 0 HTTP 429s and 131 HTTP 500s before fix
- CloudWatch metrics showing Invocations, Throttles, Errors, and Duration spike during attack
- Post-fix results confirming HTTP 429 returned after rate limiting was applied

## Lesson 7
- Outputs from privileged Lambda invocation

## Lesson 8
- Terminal output confirming race condition succeeded
- Order record showing 5 items received but only $40 charged
- Verification output showing fix blocks updates on in-progress orders

## Lesson 9
- Vulnerability scan results

## Lesson 10
- Raw API response leaking errorType, errorMessage, and stackTrace with internal file path
- Terminal output confirming stack trace exposed before fix and generic error returned after fix
