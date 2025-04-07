import json
import uuid
import os
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    http_method = event.get("httpMethod")

    if http_method == "POST":
        return handle_post(event)
    elif http_method == "GET":
        return handle_get(event)
    else:
        return response(405, {"message": "Method Not Allowed"})

def handle_post(event):
    try:
        data = json.loads(event['body'])

        item = {
            "id": str(uuid.uuid4()),
            "period": data["period"],
            "duoarea": data["duoarea"],
            "area-name": data["area-name"],
            "product": data["product"],
            "product-name": data["product-name"],
            "process": data["process"],
            "process-name": data["process-name"],
            "series": data["series"],
            "series-description": data["series-description"],
            "value": Decimal(str(data["value"])),
            "units": data["units"]
        }

        table.put_item(Item=item)
        return response(201, {"message": "Item created", "id": item["id"]})

    except Exception as e:
        return response(400, {"error": str(e)})

def handle_get(event):
    params = event.get("queryStringParameters") or {}

    try:
        items = []

        # Query by duoarea and period range
        if "duoarea" in params and "start" in params and "end" in params:
            result = table.query(
                IndexName="DuoareaPeriodIndex",
                KeyConditionExpression=Key("duoarea").eq(params["duoarea"]) & Key("period").between(params["start"], params["end"])
            )
            items = result.get("Items", [])

        # Query by period only
        elif "period" in params:
            result = table.query(
                IndexName="PeriodIndex",
                KeyConditionExpression=Key("period").eq(params["period"])
            )
            items = result.get("Items", [])

        # Query by duoarea only
        elif "duoarea" in params:
            result = table.query(
                IndexName="DuoAreaIndex",
                KeyConditionExpression=Key("duoarea").eq(params["duoarea"])
            )
            items = result.get("Items", [])

        # Default: scan
        else:
            result = table.scan(Limit=50)
            items = result.get("Items", [])

        return response(200, {"items": items})

    except Exception as e:
        return response(400, {"error": str(e)})

# Custom encoder to handle Decimal
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body, cls=DecimalEncoder)
    }
