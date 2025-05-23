import json
import boto3
import urllib.request
from datetime import datetime, timedelta
import time

# CONFIGURATION

#Name of your Firehose stream in AWS
FIREHOSE_STREAM_NAME = 'NYC_311_Firehose_Stream'

#NYC 311 API endpoint for fetching data
NYC_311_API_URL = 'https://data.cityofnewyork.us/resource/erm2-nwe9.json'

# Number of records to fetch from the NYC 311 API in each request
FIREHOSE_BATCH_SIZE = 500
API_BATCH_SIZE = 50000


firehose = boto3.client('firehose')

def lambda_handler(event, context):
    # Define time window: Last 7 days
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)

    total_sent = 0
    offset = 0

    while True:
        params = urllib.parse.urlencode({
            '$limit': API_BATCH_SIZE,
            '$offset': offset,
            '$where': (
                f"created_date >= '{start_date.strftime('%Y-%m-%dT%H:%M:%S')}' "
                f"AND created_date < '{end_date.strftime('%Y-%m-%dT%H:%M:%S')}'"
            ),
            '$order': 'created_date ASC'
        })

        url = f"{NYC_311_API_URL}?{params}"

        try:
            with urllib.request.urlopen(url) as response:
                body = response.read()
                records = json.loads(body.decode('utf-8'))
        except Exception as e:
            raise Exception(f"API call failed at offset {offset}: {e}")

        if not records:
            print("No more records returned.")
            break

        print(f"Fetched {len(records)} records from offset {offset}")

        # Send to Firehose in 500-record chunks
        for i in range(0, len(records), FIREHOSE_BATCH_SIZE):
            chunk = records[i:i+FIREHOSE_BATCH_SIZE]
            payload = [{'Data': json.dumps(rec) + '\n'} for rec in chunk]

            response = firehose.put_record_batch(
                DeliveryStreamName=FIREHOSE_STREAM_NAME,
                Records=payload
            )

            if response['FailedPutCount'] > 0:
                print(f"Warning: {response['FailedPutCount']} records failed to send.")

        total_sent += len(records)
        offset += API_BATCH_SIZE
        time.sleep(0.2)

    return {
        'statusCode': 200,
        'body': f"Sent {total_sent} records from {start_date.date()} to {end_date.date()} to Firehose stream {FIREHOSE_STREAM_NAME}"
    }