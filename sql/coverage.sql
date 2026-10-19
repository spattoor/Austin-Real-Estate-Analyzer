-- LEFT JOIN retains previously imported ZIP areas absent from the selected snapshot.
SELECT n.zip_code, n.neighborhood_name,
       COUNT(o.zip_code) AS observations_on_date,
       CASE WHEN COUNT(o.zip_code) = 0 THEN 'Absent'
            WHEN o.median_home_value IS NULL THEN 'Missing price'
            ELSE 'Price available' END AS price_coverage
FROM neighborhoods AS n
LEFT JOIN observations AS o
  ON o.zip_code = n.zip_code
 AND o.observed_on = COALESCE(:observed_on, (SELECT MAX(observed_on) FROM observations))
GROUP BY n.zip_code, n.neighborhood_name, o.median_home_value
ORDER BY n.zip_code;
