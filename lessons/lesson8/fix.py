# Lesson 8 Fix — DVSA-ORDER-UPDATE/update_order.py
# DynamoDB ConditionExpression atomically blocks updates once billing starts.
# The race window is eliminated: if status moved past 110, the update is rejected.

import boto3, os

def lambda_handler(event, context):
    orderId  = event["orderId"]
    itemList = event["items"]
    userId   = event["user"]
    dynamodb = boto3.resource('dynamodb')
    table    = dynamodb.Table(os.environ["ORDERS_TABLE"])

    response = table.get_item(Key={"orderId": orderId, "userId": userId},
                               AttributesToGet=['orderStatus'])
    if 'Item' not in response:
        return {"status": "err", "msg": "could not find order"}
    if response["Item"]["orderStatus"] > 110:
        return {"status": "err", "msg": "order already paid"}

    # FIX: atomic conditional update
    try:
        response = table.update_item(
            Key={"orderId": orderId, "userId": userId},
            UpdateExpression='SET itemList = :itemList',
            ConditionExpression="orderStatus <= :maxStatus",
            ExpressionAttributeValues={':itemList': itemList, ':maxStatus': 110})
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return {"status": "err", "msg": "order already paid"}

    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        return {"status": "ok", "msg": "cart updated"}
    return {"status": "err", "msg": "could not update cart"}