CREATE VIEW IF NOT EXISTS country_mental_health_division AS
SELECT
    m.country AS country_name,
    h.ISO3,
    h."Human Development Groups" AS hdi_tier,
    h."Human Development Index (2021)" AS national_hdi,
    h."Gross National Income Per Capita (2021)" AS national_gni,
    AVG(m.mental_health_score) AS avg_mental_health_score,
    STDDEV(m.mental_health_score) AS mental_health_variance,
    COUNT(m.user_id) AS sample_size_per_country,
    AVG(s.daily_usage_hours) AS avg_daily_social_media_hours
FROM mental_health_dataset m
JOIN social_media_usage_genz s ON m.country = s.country
JOIN hdi h ON LOWER(m.country) = LOWER(h."Country")
GROUP BY m.country, h.ISO3, h."Human Development Groups", h."Human Development Index (2021)", h."Gross National Income Per Capita (2021)"
HAVING sample_size_per_country >= 10;
