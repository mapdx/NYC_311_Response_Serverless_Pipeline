WITH top5 AS (
  SELECT complaint_type
  FROM (
    SELECT complaint_type, COUNT(*) AS total_complaints,
           ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS rank
    FROM nyc_311_cleaned_parquet_prod_2025_05_07__00_21_07
    WHERE created_timestamp BETWEEN DATE '2025-03-25' AND DATE '2025-04-26'
    GROUP BY complaint_type
  )
  WHERE rank <= 5
),
base_data AS (
  SELECT borough, complaint_type, COUNT(*) AS total_complaints
  FROM nyc_311_cleaned_parquet_prod_2025_05_07__00_21_07
  WHERE complaint_type IN (SELECT complaint_type FROM top5)
  AND created_timestamp BETWEEN DATE '2025-03-25' AND DATE '2025-04-26'
  GROUP BY borough, complaint_type
)
SELECT
  borough,
  SUM(CASE WHEN complaint_type = 'Illegal Parking' THEN total_complaints ELSE 0 END) AS "Illegal Parking",
  SUM(CASE WHEN complaint_type = 'Noise - Residential' THEN total_complaints ELSE 0 END) AS "Noise - Residential",
  SUM(CASE WHEN complaint_type = 'HEAT/HOT WATER' THEN total_complaints ELSE 0 END) AS "HEAT/HOT WATER",
  SUM(CASE WHEN complaint_type = 'Noise - Street/Sidewalk' THEN total_complaints ELSE 0 END) AS "Noise - Street/Sidewalk",
  SUM(CASE WHEN complaint_type = 'Blocked Driveway' THEN total_complaints ELSE 0 END) AS "Blocked Driveway"
FROM base_data
WHERE borough IS NOT NULL and borough != 'Unspecified'
GROUP BY borough
ORDER BY borough