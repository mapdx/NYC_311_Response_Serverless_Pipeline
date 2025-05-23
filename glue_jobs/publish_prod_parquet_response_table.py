import sys
import boto3
from datetime import datetime

# Configs for NYC 311
QUERY_RESULTS_BUCKET = 's3://athena-query-results_bucket/'
MY_DATABASE = 'project_database'
SOURCE_PARQUET_TABLE_NAME = 'cleaned_parquet'
NEW_PROD_PARQUET_TABLE_NAME = 'cleaned_parquet_prod'
NEW_PROD_PARQUET_TABLE_S3_BUCKET = 's3://prod-parquet_bucket/'

# Generate versioned suffix from datetime
DATETIME_NOW_INT_STR = datetime.utcnow().strftime('%Y_%m_%d__%H_%M_%S')

client = boto3.client('athena')

# Run CTAS to publish to versioned PROD location
queryStart = client.start_query_execution(
    QueryString=f"""
    CREATE TABLE {NEW_PROD_PARQUET_TABLE_NAME}_{DATETIME_NOW_INT_STR}
    WITH (
        external_location = '{NEW_PROD_PARQUET_TABLE_S3_BUCKET}{DATETIME_NOW_INT_STR}/',
        format = 'PARQUET',
        write_compression = 'SNAPPY',
        partitioned_by = ARRAY['year', 'month', 'day']
    )
    AS
    SELECT *
    FROM "{MY_DATABASE}"."{SOURCE_PARQUET_TABLE_NAME}"
    WHERE incident_duration_days >=0;
    """,
    QueryExecutionContext={'Database': MY_DATABASE},
    ResultConfiguration={'OutputLocation': QUERY_RESULTS_BUCKET}
)

# Monitor status
query_id = queryStart["QueryExecutionId"]
final_states = ["FAILED", "SUCCEEDED", "CANCELLED"]

while True:
    response = client.get_query_execution(QueryExecutionId=query_id)
    state = response["QueryExecution"]["Status"]["State"]
    if state in final_states:
        break

# Fail if CTAS fails
if state == 'FAILED':
    sys.exit(response["QueryExecution"]["Status"]["StateChangeReason"])

print(f"PROD publish succeeded! Table name: {NEW_PROD_PARQUET_TABLE_NAME}_{DATETIME_NOW_INT_STR}")