import os
import boto3
import sys

# Намагаємося завантажити змінні з .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

aws_region = os.environ.get('AWS_REGION', 'eu-central-1')
HISTORY_TABLE = os.environ.get('HISTORY_TABLE', "savchenko-andrii-17-history-table")

dynamodb = boto3.resource('dynamodb', region_name=aws_region)
table = dynamodb.Table(HISTORY_TABLE)

print("Fetching all items from history table...")
response = table.scan()
items = response.get('Items', [])

if not items:
    print("Table is already empty.")
else:
    print(f"Found {len(items)} items. Deleting...")
    with table.batch_writer() as batch:
        for item in items:
            batch.delete_item(
                Key={
                    # ЗМІНЕНО тут: тепер використовуємо device_id
                    'device_id': item['device_id'],
                    'timestamp': item['timestamp']
                }
            )
    print("Successfully deleted all old history metrics!")
