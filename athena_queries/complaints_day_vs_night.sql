SELECT time_of_day,
       COUNT(*) as total_complaints
FROM nyc_311_cleaned_parquet_prod_2025_05_07__00_21_07
where created_timestamp BETWEEN DATE '2025-03-24' AND DATE '2025-04-08'
GROUP BY time_of_day