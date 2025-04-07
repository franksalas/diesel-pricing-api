import json
import boto3
from decimal import Decimal
from tqdm import tqdm

# Configuration
region = 'us-east-1'
table_name = 'DieselPrices'
json_file = 'data.json'

# Initialize DynamoDB resource and table
dynamodb = boto3.resource('dynamodb', region_name=region)
table = dynamodb.Table(table_name)

# Step 1: Delete all existing items
def delete_all_items():
    print("Deleting existing items from table...")
    scan = table.scan()
    items = scan.get('Items', [])
    if not items:
        print("No items to delete.")
        return

    with table.batch_writer() as batch:
        for item in tqdm(items, desc="Deleting", unit="item"):
            key = {k['AttributeName']: item[k['AttributeName']] for k in table.key_schema}
            batch.delete_item(Key=key)
    print(f"Deleted {len(items)} items.")

# Step 2: Load and insert new data
def load_new_data():
    print("Loading new data from file...")
    with open(json_file, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    with table.batch_writer() as batch:
        for line in tqdm(lines, desc="Uploading", unit="item"):
            item = json.loads(line, parse_float=Decimal)
            batch.put_item(Item=item)

    print(f"Uploaded {len(lines)} new items.")

# Run both steps
if __name__ == '__main__':
    delete_all_items()
    load_new_data()
