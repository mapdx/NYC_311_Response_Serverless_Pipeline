SELECT
  DATE(created_timestamp) AS time,
  COUNT(*) AS total_complaints
FROM nyc_311_cleaned_parquet_prod_2025_05_07__00_21_07
WHERE created_timestamp BETWEEN DATE '2025-03-24' AND DATE '2025-04-08'
GROUP BY DATE(created_timestamp)
ORDER BY time