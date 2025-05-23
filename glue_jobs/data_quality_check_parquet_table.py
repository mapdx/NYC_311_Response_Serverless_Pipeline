import sys
import boto3
import awswrangler as wr

# Configurations
DATABASE = 'project_database'
TABLE = 'cleaned_parquet'

# 1. Null and Range Check SQL
dq_check_query = f"""
SELECT
    SUM(CASE WHEN created_timestamp IS NULL THEN 1 ELSE 0 END) AS missing_created_timestamp,
    SUM(CASE WHEN borough IS NULL THEN 1 ELSE 0 END) AS missing_borough,
    SUM(CASE WHEN complaint_type IS NULL THEN 1 ELSE 0 END) AS missing_complaint_type,
    SUM(CASE WHEN incident_duration_days < 0 THEN 1 ELSE 0 END) AS negative_durations,
    SUM(CASE WHEN incident_duration_days > 365 THEN 1 ELSE 0 END) AS excessive_durations
FROM {TABLE}
"""

# Execute Athena query
print("Running data quality checks...")
df = wr.athena.read_sql_query(sql=dq_check_query, database=DATABASE)

# Extract values
missing_created = df['missing_created_timestamp'][0]
missing_borough = df['missing_borough'][0]
missing_complaint = df['missing_complaint_type'][0]
negative_durations = df['negative_durations'][0]
excessive_durations = df['excessive_durations'][0]

# Print results
print(df)

# Evaluate checks
if any([missing_created, missing_borough, missing_complaint, negative_durations, excessive_durations]):
    print("Data Quality Check Failed:")
    if missing_created:
        print(f"- Missing created_timestamp: {missing_created}")
    if missing_borough:
        print(f"- Missing borough: {missing_borough}")
    if missing_complaint:
        print(f"- Missing complaint_type: {missing_complaint}")
    if negative_durations:
        print(f"- Negative durations: {negative_durations}")
    if excessive_durations:
        print(f"- Durations over 365 days: {excessive_durations}")
else:
    print("Data Quality Check Passed: All values clean.")
