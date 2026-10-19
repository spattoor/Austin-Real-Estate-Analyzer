-- A window function compares each dated observation with the previous available one.
SELECT observed_on, investment_score, median_home_value,
       ROUND(investment_score - LAG(investment_score) OVER (ORDER BY observed_on), 2)
           AS score_change,
       ROUND(median_home_value - LAG(median_home_value) OVER (ORDER BY observed_on), 2)
           AS home_value_change
FROM observations
WHERE zip_code = :zip_code
ORDER BY observed_on;
