import os
import boto3
import sys

# Намагаємося завантажити змінні з .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def seed_data():
    aws_region = os.environ.get('AWS_REGION', 'eu-central-1')
    table_name = os.environ.get('TABLE_NAME')
    
    if not table_name:
        print("Помилка: TABLE_NAME не знайдено! Створіть файл .env або пропишіть змінну середовища.")
        sys.exit(1)

    dynamodb = boto3.client('dynamodb', region_name=aws_region)
    items = [
        {"metric_name": {"S": "cpu_usage"}, "threshold": {"N": "80"}},
        {"metric_name": {"S": "memory_usage"}, "threshold": {"N": "90"}},
        {"metric_name": {"S": "disk_usage"}, "threshold": {"N": "95"}},
        {"metric_name": {"S": "error_rate"}, "threshold": {"N": "5"}}
    ]
    
    for item in items:
        print(f"Adding item: {item['metric_name']['S']} -> {item['threshold']['N']}")
        dynamodb.put_item(TableName=table_name, Item=item)
    
    print("Seed complete.")

if __name__ == "__main__":
    seed_data()
