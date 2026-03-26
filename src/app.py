import os
import json
import boto3
from datetime import datetime
import uuid
from botocore.config import Config

dynamodb = boto3.client('dynamodb', region_name='eu-central-1')
sns = boto3.client('sns', region_name='eu-central-1')
polly = boto3.client('polly', region_name='eu-central-1')
s3 = boto3.client('s3', region_name='eu-central-1', config=Config(signature_version='s3v4'))

TABLE_NAME = os.environ.get('TABLE_NAME')
HISTORY_TABLE = os.environ.get('HISTORY_TABLE')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')
AUDIO_BUCKET = os.environ.get('AUDIO_BUCKET')

def get_cors_headers():
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

def lambda_handler(event, context):
    try:
        http_method = event.get('requestContext', {}).get('http', {}).get('method', 'POST')
        path = event.get('requestContext', {}).get('http', {}).get('path', '/')

        if http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': get_cors_headers(),
                'body': ''
            }

        # GET /metrics - Повертаємо єдину історію за пристроями
        if http_method == 'GET' and path == '/metrics':
            response = dynamodb.scan(TableName=HISTORY_TABLE)
            items = response.get('Items', [])
            
            parsed_items = []
            for item in items:
                parsed_items.append({
                    'device_id': item['device_id']['S'],
                    'timestamp': item['timestamp']['S'],
                    'metrics': json.loads(item['metrics_json']['S']),
                    'is_alert': item['is_alert']['BOOL']
                })
                
            parsed_items.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return {
                'statusCode': 200,
                'headers': get_cors_headers(),
                'body': json.dumps({'history': parsed_items})
            }

        # GET /alerts/{device_id}/audio - Озвучити всі алерти пристрою в один час
        if http_method == 'GET' and path.startswith('/alerts/') and path.endswith('/audio'):
            parts = path.split('/')
            device_id = parts[2] if len(parts) > 2 else 'unknown'
            
            query_params = event.get('queryStringParameters') or {}
            timestamp = query_params.get('time')
            
            try:
                latest = None
                
                if timestamp:
                    response = dynamodb.get_item(
                        TableName=HISTORY_TABLE,
                        Key={
                            'device_id': {'S': device_id},
                            'timestamp': {'S': timestamp}
                        }
                    )
                    latest = response.get('Item')
                
                if not latest:
                    # Fallback on latest record
                    response = dynamodb.query(
                        TableName=HISTORY_TABLE,
                        KeyConditionExpression="device_id = :d",
                        ExpressionAttributeValues={":d": {"S": device_id}},
                        ScanIndexForward=False,
                        Limit=1
                    )
                    items = response.get('Items', [])
                    if items:
                        latest = items[0]
                
                if not latest:
                    return {
                        'statusCode': 404,
                        'headers': get_cors_headers(),
                        'body': json.dumps({'message': 'No history found for this device'})
                    }
                
                alert_text = latest.get('alert_message', {}).get('S')
                if not alert_text:
                    alert_text = "Attention. An alert was recorded, but the details are missing."
                
                # Call Polly
                polly_response = polly.synthesize_speech(
                    Text=alert_text,
                    OutputFormat="mp3",
                    VoiceId="Joanna"
                )
                
                audio_stream = polly_response['AudioStream'].read()
                
                audio_key = f"audio/{device_id}-{uuid.uuid4().hex[:6]}.mp3"
                s3.put_object(
                    Bucket=AUDIO_BUCKET,
                    Key=audio_key,
                    Body=audio_stream,
                    ContentType='audio/mpeg'
                )
                
                url = f"https://{AUDIO_BUCKET}.s3.eu-central-1.amazonaws.com/{audio_key}"
                
                return {
                    'statusCode': 200,
                    'headers': get_cors_headers(),
                    'body': json.dumps({'message': 'Audio generated', 'audio_url': url})
                }
            except Exception as e:
                print(f"Polly/S3 Error: {str(e)}")
                return {
                    'statusCode': 500,
                    'headers': get_cors_headers(),
                    'body': json.dumps({'message': f'Error generating or saving audio: {str(e)}'})
                }

        # POST /metrics - Отримання комплексного корисного навантаження (усі метрики разом)
        if http_method == 'POST':
            body = event.get('body', '{}')
            if event.get('isBase64Encoded', False):
                import base64
                body = base64.b64decode(body).decode('utf-8')
                
            data = json.loads(body)
            device_id = data.get('device_id')
            metrics = data.get('metrics', {}) # dict
            
            if not device_id or not metrics:
                return {
                    'statusCode': 400,
                    'headers': get_cors_headers(),
                    'body': json.dumps({'message': "Missing 'device_id' or 'metrics' dict"})
                }
                
            timestamp = datetime.utcnow().isoformat()
            
            # Отримуємо конфігурацію (пороги) ОДНИМ запитом через Scan
            # Це нормально для маленької конфігураційної таблиці (2-10 записів)
            config_response = dynamodb.scan(TableName=TABLE_NAME)
            thresholds = {}
            for item in config_response.get('Items', []):
                thresholds[item['metric_name']['S']] = float(item['threshold']['N'])
            
            is_alert = False
            triggered_messages = []
            
            for metric, value in metrics.items():
                thresh = thresholds.get(metric)
                if thresh is not None and float(value) > thresh:
                    is_alert = True
                    triggered_messages.append(f"the metric {metric} has risen to {value}, above the {thresh} limit")

            alert_text = "All systems green."
            if is_alert:
                alert_text = f"Attention! Device {device_id} reported issues: " + ", and ".join(triggered_messages) + "."
            
            # Зберігаємо "пачку" метрик в історію як єдиний рядок для device_id
            dynamodb.put_item(
                TableName=HISTORY_TABLE,
                Item={
                    'device_id': {'S': str(device_id)},
                    'timestamp': {'S': timestamp},
                    'metrics_json': {'S': json.dumps(metrics)},
                    'is_alert': {'BOOL': is_alert},
                    'alert_message': {'S': alert_text}
                }
            )
            
            if is_alert:
                sns.publish(
                    TopicArn=SNS_TOPIC_ARN,
                    Subject=f"Alert: Issues detected on {device_id}",
                    Message=alert_text
                )
            
            return {
                'statusCode': 200,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'message': 'Combined metrics recorded',
                    'is_alert': is_alert,
                    'device_id': device_id,
                    'timestamp': timestamp
                })
            }

        return {
            'statusCode': 404,
            'headers': get_cors_headers(),
            'body': json.dumps({'message': 'Not Found'})
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'message': f'Internal Server Error: {str(e)}'})
        }
