-- ============================================================
-- NBA OPTIMIZER — SAMPLE SQL QUERIES
-- Database: nba_optimizer.db (SQLite)
-- Run with: sqlite3 nba_optimizer.db < sql_queries.sql
-- Or open in DB Browser for SQLite (free GUI tool)
-- ============================================================

-- ============================================================
-- BASIC QUERIES
-- ============================================================

-- 1. Top 20 players in 2023-24
SELECT * FROM v_rankings_2024 LIMIT 20;

-- 2. All Elite Playmakers
SELECT player_name, team, score, salary
FROM v_rankings_2024
WHERE archetype = 'Elite Playmaker'
ORDER BY score DESC;

-- 3. Best value players (most score per dollar)
SELECT * FROM v_best_value LIMIT 20;

-- 4. Archetype summary
SELECT * FROM v_archetype_summary;

-- ============================================================
-- SALARY ANALYSIS
-- ============================================================

-- 5. Players under $10M with score > 60
SELECT player_name, team, archetype, score, salary
FROM v_rankings_2024
WHERE salary < 10000000 AND score > 60
ORDER BY score DESC;

-- 6. Overpaid players (high salary, low score)
SELECT player_name, team, archetype, score, salary,
       ROUND(salary / 1000000.0, 1) AS salary_millions
FROM v_rankings_2024
WHERE salary > 30000000 AND score < 60
ORDER BY salary DESC;

-- 7. Underpaid stars (high score, low salary)
SELECT player_name, team, archetype, score, salary,
       ROUND(salary / 1000000.0, 1) AS salary_millions
FROM v_rankings_2024
WHERE score > 70 AND salary < 15000000
ORDER BY score DESC;

-- ============================================================
-- ARCHETYPE ANALYSIS
-- ============================================================

-- 8. Top 5 players per archetype
SELECT *
FROM (
    SELECT player_name, team, archetype, score, salary,
           ROW_NUMBER() OVER (PARTITION BY archetype ORDER BY score DESC) AS arch_rank
    FROM v_rankings_2024
)
WHERE arch_rank <= 5
ORDER BY archetype, arch_rank;

-- 9. Archetype salary comparison
SELECT archetype,
       COUNT(*) AS count,
       ROUND(AVG(salary), 0) AS avg_salary,
       ROUND(MIN(salary), 0) AS min_salary,
       ROUND(MAX(salary), 0) AS max_salary
FROM v_rankings_2024
GROUP BY archetype
ORDER BY avg_salary DESC;

-- 10. Defensive specialists (high BLK or STL)
SELECT player_name, team, archetype, score, blk, stl,
       ROUND(blk + stl, 1) AS total_stocks
FROM v_rankings_2024
WHERE blk >= 1.0 OR stl >= 1.5
ORDER BY (blk + stl) DESC;

-- ============================================================
-- ROSTER / OPTIMIZER QUERIES
-- ============================================================

-- 11. Compare all 10 scenario rosters
SELECT * FROM v_roster_comparison;

-- 12. Scenario A roster (Hard Cap)
SELECT PLAYER_NAME, ARCHETYPE, COMPOSITE_SCORE_NORM AS score, SALARY
FROM optimized_rosters
WHERE SCENARIO = 'A'
ORDER BY COMPOSITE_SCORE_NORM DESC;

-- 13. Players selected in the most scenarios
SELECT PLAYER_NAME, COUNT(*) AS times_selected,
       GROUP_CONCAT(SCENARIO) AS scenarios
FROM optimized_rosters
GROUP BY PLAYER_NAME
ORDER BY times_selected DESC
LIMIT 20;

-- 14. Players NEVER selected in any scenario
SELECT pa.PLAYER_NAME, pa.ARCHETYPE, pa.COMPOSITE_SCORE_NORM AS score, pa.SALARY
FROM player_archetypes pa
WHERE pa.SEASON = '2023-24'
  AND pa.PLAYER_NAME NOT IN (SELECT PLAYER_NAME FROM optimized_rosters)
ORDER BY pa.COMPOSITE_SCORE_NORM DESC
LIMIT 20;

-- ============================================================
-- SYNERGY QUERIES
-- ============================================================

-- 15. Top 20 positive synergy pairs
SELECT * FROM v_top_synergy_pairs
WHERE net_synergy > 0
LIMIT 20;

-- 16. Worst synergy pairs (negative chemistry)
SELECT * FROM v_top_synergy_pairs
ORDER BY net_synergy ASC
LIMIT 20;

-- 17. Synergy profiles — best team-elevators
SELECT PLAYER_NAME, ROUND(NET_SYNERGY_PROFILE, 2) AS net_synergy_profile
FROM synergy_profiles
ORDER BY NET_SYNERGY_PROFILE DESC
LIMIT 15;

-- ============================================================
-- PLAYER TRAJECTORY (across seasons)
-- ============================================================

-- 18. Jokic across all 3 seasons
SELECT * FROM v_player_trajectory
WHERE PLAYER_NAME LIKE '%Joki%';

-- 19. Biggest score improvements year-over-year
SELECT
    a.PLAYER_NAME,
    a.score AS score_2223,
    b.score AS score_2324,
    ROUND(b.score - a.score, 2) AS improvement
FROM v_player_trajectory a
JOIN v_player_trajectory b
    ON a.PLAYER_NAME = b.PLAYER_NAME
WHERE a.SEASON = '2022-23' AND b.SEASON = '2023-24'
ORDER BY improvement DESC
LIMIT 15;

-- 20. Players who changed archetypes between seasons
SELECT
    a.PLAYER_NAME,
    a.SEASON AS season_1, a.ARCHETYPE AS archetype_1,
    b.SEASON AS season_2, b.ARCHETYPE AS archetype_2
FROM v_player_trajectory a
JOIN v_player_trajectory b
    ON a.PLAYER_NAME = b.PLAYER_NAME
    AND a.SEASON < b.SEASON
WHERE a.ARCHETYPE != b.ARCHETYPE
ORDER BY a.PLAYER_NAME, a.SEASON;
