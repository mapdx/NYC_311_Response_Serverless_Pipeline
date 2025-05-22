# NYC 311 AWS Serverless Pipeline + Grafana Dashboard Project

This project showcases an end-to-end data engineering pipeline that ingests, transforms, and visualizes New York City's 311 service request data using AWS services and Grafana.

The dataset includes approximately one month of 311 service requests across all five NYC boroughs. Each record contains metadata such as complaint type, agency, timestamps, geographic location, and status. The dataset was filtered to reduce record count for project scope and resource constraints.


---

:chart_with_upwards_trend: System Architecture Overview

Source: NYC Open Data 311 API

Ingestion: AWS Lambda + Kinesis Firehose

Storage: Amazon S3 (raw + transformed)

Processing: AWS Glue (ETL pipeline + quality checks)

Query Engine: AWS Athena

Visualization: Grafana



---

:rocket: Project Objectives

Ingest 1 month of NYC 311 complaint data

Clean, enrich, and transform the data using SQL (CTAS in Glue)

Add calculated fields (e.g., day vs. night, duration, partition fields)

Perform data quality checks (nulls, negative durations, excessive durations)

Publish a production-ready Parquet dataset

Visualize insights in Grafana with multiple chart types



---

:label: Key Fields Added During Transformation

created_timestamp, closed_timestamp

incident_duration_days

time_of_day: Day (6AM–5PM) or Evening

day_type: Weekday or Weekend

year, month, day: for partitioning



---

:gear: Glue Jobs

create_nyc311_transformed_parquet.py: CTAS job using Athena

data_quality_check_parquet_table.py: Counts nulls and data issues

delete_nyc311_parquet_table.py: Clears output bucket and drops table

publish_prod_parquet_response_table.py: Copies clean data into timestamped production path



---

:bar_chart: Visualizations in Grafana

1. Top Complaint Types (Bar Chart)


2. Top 5 Complaints by Borough (Grouped Bar Chart)


3. Complaint Counts Over Time (Time Series)


4. Day vs. Night Complaint Volume (Bar Chart)


5. Incident Duration Distribution (Histogram)


6. Complaint Location Map (Geomap)


7. Single Stat: Total Complaints Collected




---

:warning: Challenges Faced

Athena SQL compatibility (e.g., casting ISO timestamps, using Unix time)

Glue job failures due to malformed CTAS or field types

Grafana limitations in field overrides and legend matching

AWS Glue query debugging and role permissions



---

:file_folder: Repository Structure

project_repo/
├── lambda/
│   └── nyc_311_response_lambda.py
├── glue_jobs/
│   ├── create_nyc311_transformed_parquet.py
│   ├── delete_nyc311_parquet_table.py
│   ├── data_quality_check_parquet_table.py
│   └── publish_prod_parquet_response_table.py
├── athena_queries/
│   └── [Your saved SQL files]
├── grafana_dashboards/
│   └── screenshots/ [PNG exports of panels]
├── docs/
│   └── README.md


---

:bulb: Next Steps / Enhancements

Parameterize Glue jobs for date range or incremental ingestion

Automate the workflow using Glue Triggers or Step Functions

Upload Grafana dashboard JSON for live replay

Consider CI/CD integration (e.g., with GitHub Actions)


---

:mailbox: Contact

Created by Matt Wood — for questions or collaborations, feel free to open an issue or reach out on GitHub.


