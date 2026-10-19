-- NULL prices remain missing; AVG ignores them and coverage is reported explicitly.
SELECT COALESCE(o.cluster, 'Unassigned') AS cluster,
       COUNT(*) AS area_count,
       ROUND(AVG(o.investment_score), 2) AS average_score,
       COUNT(o.median_home_value) AS areas_with_price,
       ROUND(AVG(o.median_home_value), 2) AS average_home_value
FROM observations AS o
WHERE o.observed_on = COALESCE(:observed_on, (SELECT MAX(observed_on) FROM observations))
GROUP BY COALESCE(o.cluster, 'Unassigned')
ORDER BY average_score DESC, cluster;
