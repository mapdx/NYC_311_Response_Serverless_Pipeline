SELECT
  latitude,
  longitude,
  complaint_type
FROM nyc_311_cleaned_parquet_prod_2025_05_07__00_21_07
WHERE latitude IS NOT NULL
AND longitude IS NOT NULL
AND created_timestamp BETWEEN DATE '2025-02-25' AND DATE '2025-04-06'
AND complaint_type IN ('Illegal Parking', 'Noise - Residential', 'HEAT/HOT WATER', 'Noise - Street/Sidewalk', 'Blocked Driveway')
LIMIT 10000