import boto3
import sys
import time
import textwrap

client = boto3.client('athena')

# Configurations
SOURCE_TABLE_NAME = 'response_table_bucket'
NEW_TABLE_NAME = 'cleaned_parquet'
MY_DATABASE = 'project_database'
NEW_TABLE_S3_BUCKET = 's3://transformed-parquet_bucket/'
QUERY_RESULTS_S3_BUCKET = 's3://athena-query-results_bucket/'

query_string = textwrap.dedent(f'''
    CREATE TABLE {NEW_TABLE_NAME}
    WITH (
        format = 'PARQUET',
        external_location = '{NEW_TABLE_S3_BUCKET}',
        write_compression = 'SNAPPY',
        partitioned_by = ARRAY['year', 'month', 'day']
    )
    AS
    SELECT
        unique_key,
        agency,
        agency_name,
        complaint_type,
        descriptor,
        location_type,
        status,
        borough,
        latitude,
        longitude,
        CAST(from_iso8601_timestamp(created_date) AS timestamp) AS created_timestamp,
        CAST(from_iso8601_timestamp(closed_date) AS timestamp) AS closed_timestamp,
        ROUND(
            CAST(
                to_unixtime(CAST(from_iso8601_timestamp(closed_date) AS timestamp)) -
                to_unixtime(CAST(from_iso8601_timestamp(created_date) AS timestamp))
            AS DOUBLE
            ) / 86400.0,
            2
        ) AS incident_duration_days,
        CASE 
            WHEN HOUR(CAST(from_iso8601_timestamp(created_date) AS timestamp)) BETWEEN 6 AND 17 THEN 'Day'
            ELSE 'Evening'
        END AS time_of_day,
        CASE 
            WHEN day_of_week(CAST(from_iso8601_timestamp(created_date) AS timestamp)) IN (1, 7) THEN 'Weekend'
            ELSE 'Weekday'
        END AS day_type,
        year(CAST(from_iso8601_timestamp(created_date) AS timestamp)) AS year,
        month(CAST(from_iso8601_timestamp(created_date) AS timestamp)) AS month,
        day(CAST(from_iso8601_timestamp(created_date) AS timestamp)) AS day
    FROM {SOURCE_TABLE_NAME}
    WHERE created_date IS NOT NULL
''')

# Print query for debug
print("Final SQL sent to Athena:")
print(query_string)

# Start Athena query
queryStart = client.start_query_execution(
    QueryString=query_string,
    QueryExecutionContext={'Database': MY_DATABASE},
    ResultConfiguration={'OutputLocation': QUERY_RESULTS_S3_BUCKET}
)

# Poll for query completion
query_id = queryStart['QueryExecutionId']
print(f"Started Athena query execution: {query_id}")

# Wait for query to finish
final_states = ["FAILED", "SUCCEEDED", "CANCELLED"]
while True:
    response = client.get_query_execution(QueryExecutionId=query_id)
    state = response['QueryExecution']['Status']['State']
    if state in final_states:
        break
    print(f"Waiting... Current state: {state}")
    time.sleep(3)

# Check for failure
if state == 'FAILED':
    print("Athena query failed:")
    sys.exit(response['QueryExecution']['Status']['StateChangeReason'])

print(f"Query succeeded. Output stored at: {QUERY_RESULTS_S3_BUCKET}")