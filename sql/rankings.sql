-- Latest observation date across the database. Optional filters bind parameters, not SQL text.
SELECT n.zip_code, n.neighborhood_name, o.observed_on,
       o.investment_score, o.median_home_value, o.business_count,
       o.confidence_score, o.cluster, r.source_kind
FROM neighborhoods AS n
JOIN observations AS o ON o.zip_code = n.zip_code
JOIN import_runs AS r ON r.run_id = o.run_id
WHERE o.observed_on = COALESCE(:observed_on, (SELECT MAX(observed_on) FROM observations))
  AND o.investment_score >= :min_score
  AND (:max_price IS NULL OR o.median_home_value <= :max_price)
ORDER BY o.investment_score DESC, n.zip_code;
