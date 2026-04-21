# Lesson 5 Fix — DVSA-ADMIN-UPDATE-ORDERS/admin_update_orders.py
# Check cognito:groups after extracting username; reject non-admins immediately.

import json, base64

def lambda_handler(event, context):
    auth_header = event["headers"].get("Authorization") or event["headers"].get("authorization")
    if not auth_header:
        return {"status": "err", "msg": "Unknown user. Are you an admin?"}

    token = json.loads(base64.b64decode(auth_header.split('.')[1] + "=="))
    user  = token["username"]

    # FIX: check cognito:groups before allowing any action
    cognito_groups = token.get("cognito:groups", [])
    if "admin" not in cognito_groups:
        return {"status": "err", "msg": "Forbidden: admin only"}

    action  = event['body']['action']
    orderId = event['body']['order-id']
    item    = event['body']['item']
    # ... rest of handler unchanged