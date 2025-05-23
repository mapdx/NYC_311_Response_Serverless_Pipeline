SELECT
  incident_duration_days,
  COUNT(*) as total_complaints
FROM nyc_311_cleaned_parquet_prod_2025_05_07__00_21_07
WHERE incident_duration_days IS NOT NULL
AND incident_duration_days >= 0
AND created_timestamp BETWEEN DATE '2025-02-25' AND DATE '2025-04-06'
GROUP by incident_duration_days
ORDER BY incident_duration_days