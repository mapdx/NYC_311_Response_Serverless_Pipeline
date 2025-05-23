import sys
import boto3

#configuration
BUCKET_TO_DEL = 's3://transformed-parquet_bucket/'
DATABASE_TO_DEL = 'project_database'
TABLE_TO_DEL = 'cleaned_parquet'
QUERY_OUTPUT_BUCKET = 's3://athena-query-results_bucket/'


# delete all objects in the bucket
s3_client = boto3.client('s3')

while True:
    objects = s3_client.list_objects(Bucket=BUCKET_TO_DEL)
    content = objects.get('Contents', [])
    if len(content) == 0:
        break
    for obj in content:
        s3_client.delete_object(Bucket=BUCKET_TO_DEL, Key=obj['Key'])


# drop the table too
client = boto3.client('athena')

query_str =  f"""DROP TABLE IF EXISTS {DATABASE_TO_DEL}.{TABLE_TO_DEL}"""
print(f"Executing query: {query_str}")

queryStart = client.start_query_execution(
    QueryString=query_str,
    QueryExecutionContext={'Database': DATABASE_TO_DEL},
    ResultConfiguration={'OutputLocation': QUERY_OUTPUT_BUCKET}
)

#Monitor query
query_id = queryStart["QueryExecutionId"]
resp = ["FAILED", "SUCCEEDED", "CANCELLED"]

# get the response
while True:
    response = client.get_query_execution(QueryExecutionId=query_id)
    state = response["QueryExecution"]["Status"]["State"]
    if state in resp:
        break
        

# if it fails, exit and give the Athena error message in the logs
if state == 'FAILED':
    sys.exit(response["QueryExecutionId"]["Status"]["StateChangedReason"])
    
print("Table dropped and bucket cleared successfully")