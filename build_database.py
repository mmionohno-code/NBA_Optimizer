"""
Build SQLite database from NBA Optimizer pipeline CSVs.
Creates a professional relational database with tables, views, and pre-built queries.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import sqlite3
import pandas as pd
import os

DB_FILE = 'nba_optimizer.db'

print("=" * 60)
print("BUILDING NBA OPTIMIZER DATABASE")
print("=" * 60)

# Remove old DB if exists
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
    print(f"Removed old {DB_FILE}")

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# ============================================================
# TABLE 1 — PLAYERS (unique players across all seasons)
# ============================================================

print("\n--- Table: players ---")
df_master = pd.read_csv('nba_complete_master.csv')

# Build unique player table
players = (df_master.sort_values('SEASON', ascending=False)
           .drop_duplicates('PLAYER_ID')
           [['PLAYER_ID', 'PLAYER_NAME']]
           .reset_index(drop=True))

players.to_sql('players', conn, index=False, if_exists='replace')
print(f"  {len(players)} unique players")

# ============================================================
# TABLE 2 — PLAYER_SEASONS (scored data — all 3 seasons)
# ============================================================

print("\n--- Table: player_seasons ---")
df_scored = pd.read_csv('nba_scored_complete.csv')

cols_seasons = [
    'PLAYER_NAME', 'PLAYER_ID', 'TEAM_ABBREVIATION', 'SEASON',
    'COMPOSITE_SCORE_NORM', 'SALARY', 'VORPD',
    'OFF_RATING_ADJUSTED', 'DEF_RATING_ADJUSTED',
    'ON_OFF_DIFF', 'INFLUENCE_SCORE',
    'TS_PCT', 'BLK', 'STL', 'AST_PCT_ADJUSTED', 'FG3_PCT',
    'IS_SHOOTER', 'SEASON_WEIGHT'
]
# Only keep columns that exist
cols_seasons = [c for c in cols_seasons if c in df_scored.columns]
df_scored[cols_seasons].to_sql('player_seasons', conn, index=False, if_exists='replace')
print(f"  {len(df_scored)} player-seasons")

# ============================================================
# TABLE 3 — ARCHETYPES (clustered data — all 3 seasons)
# ============================================================

print("\n--- Table: player_archetypes ---")
df_clustered = pd.read_csv('nba_clustered.csv')

cols_arch = [
    'PLAYER_NAME', 'PLAYER_ID', 'TEAM_ABBREVIATION', 'SEASON',
    'ARCHETYPE', 'CLUSTER', 'COMPOSITE_SCORE_NORM', 'SALARY', 'VORPD',
    'OFF_RATING_ADJUSTED', 'DEF_RATING_ADJUSTED',
    'ON_OFF_DIFF', 'INFLUENCE_SCORE',
    'TS_PCT', 'BLK', 'STL', 'AST_PCT_ADJUSTED', 'FG3_PCT',
    'IS_SHOOTER'
]
cols_arch = [c for c in cols_arch if c in df_clustered.columns]
df_clustered[cols_arch].to_sql('player_archetypes', conn, index=False, if_exists='replace')
print(f"  {len(df_clustered)} player-seasons with archetypes")

# ============================================================
# TABLE 4 — OPTIMIZED ROSTERS (all 10 scenarios)
# ============================================================

print("\n--- Table: optimized_rosters ---")
all_rosters = []
for key in 'ABCDEFGHIJ':
    filepath = f'optimized_roster_syn_{key}.csv'
    if os.path.exists(filepath):
        roster = pd.read_csv(filepath)
        roster['SCENARIO'] = key
        all_rosters.append(roster)

if all_rosters:
    df_rosters = pd.concat(all_rosters, ignore_index=True)
    df_rosters.to_sql('optimized_rosters', conn, index=False, if_exists='replace')
    print(f"  {len(df_rosters)} roster slots across {len(all_rosters)} scenarios")

# ============================================================
# TABLE 5 — SYNERGY PAIRS (2023-24 pairwise chemistry)
# ============================================================

print("\n--- Table: synergy_pairs ---")
df_synergy = pd.read_csv('nba_synergy_2324.csv')
df_synergy.to_sql('synergy_pairs', conn, index=False, if_exists='replace')
print(f"  {len(df_synergy)} synergy pairs")

# ============================================================
# TABLE 6 — SYNERGY PROFILES (player-level)
# ============================================================

print("\n--- Table: synergy_profiles ---")
df_profile = pd.read_csv('nba_def_synergy_profile.csv')
df_profile.to_sql('synergy_profiles', conn, index=False, if_exists='replace')
print(f"  {len(df_profile)} player synergy profiles")

# ============================================================
# TABLE 7 — ARCHETYPE SYNERGY (archetype-pair averages)
# ============================================================

print("\n--- Table: archetype_synergy ---")
df_arch_syn = pd.read_csv('nba_archetype_synergy.csv')
df_arch_syn.to_sql('archetype_synergy', conn, index=False, if_exists='replace')
print(f"  {len(df_arch_syn)} archetype pair combinations")

# ============================================================
# TABLE 8 — SCENARIOS (metadata for each optimization scenario)
# ============================================================

print("\n--- Table: scenarios ---")
scenarios = pd.DataFrame([
    {'scenario': 'A', 'name': 'Hard Cap',           'salary_cap': 136021000, 'objective': 'composite',  'variant': 'standard'},
    {'scenario': 'B', 'name': 'Luxury Tax',          'salary_cap': 165294000, 'objective': 'composite',  'variant': 'standard'},
    {'scenario': 'C', 'name': 'Budget Team',          'salary_cap':  90000000, 'objective': 'composite',  'variant': 'standard'},
    {'scenario': 'D', 'name': 'Rebuild Mode',         'salary_cap': 136021000, 'objective': 'composite',  'variant': 'rebuild'},
    {'scenario': 'E', 'name': 'Win-Now',              'salary_cap': 165294000, 'objective': 'composite',  'variant': 'win_now'},
    {'scenario': 'F', 'name': 'Defensive Identity',   'salary_cap': 136021000, 'objective': 'defense',    'variant': 'standard'},
    {'scenario': 'G', 'name': 'Offensive Identity',   'salary_cap': 136021000, 'objective': 'offense',    'variant': 'standard'},
    {'scenario': 'H', 'name': 'Three-Point Era',      'salary_cap': 136021000, 'objective': 'composite',  'variant': 'three_point'},
    {'scenario': 'I', 'name': 'Small Ball',            'salary_cap': 136021000, 'objective': 'composite',  'variant': 'small_ball'},
    {'scenario': 'J', 'name': 'Value / Efficiency',   'salary_cap': 136021000, 'objective': 'vorpd',      'variant': 'standard'},
])
scenarios.to_sql('scenarios', conn, index=False, if_exists='replace')
print(f"  {len(scenarios)} scenarios")

# ============================================================
# VIEWS — Pre-built queries for common analysis
# ============================================================

print("\n--- Creating Views ---")

# View 1: 2023-24 player rankings
cursor.execute("""
CREATE VIEW v_rankings_2024 AS
SELECT
    ROW_NUMBER() OVER (ORDER BY pa.COMPOSITE_SCORE_NORM DESC) AS rank,
    pa.PLAYER_NAME,
    pa.TEAM_ABBREVIATION AS team,
    pa.ARCHETYPE,
    ROUND(pa.COMPOSITE_SCORE_NORM, 2) AS score,
    pa.SALARY,
    ROUND(pa.VORPD, 2) AS vorpd,
    ROUND(pa.OFF_RATING_ADJUSTED, 2) AS off_rtg_adj,
    ROUND(pa.DEF_RATING_ADJUSTED, 2) AS def_rtg_adj,
    ROUND(pa.ON_OFF_DIFF, 2) AS on_off_diff,
    ROUND(pa.INFLUENCE_SCORE, 4) AS influence,
    ROUND(pa.BLK, 1) AS blk,
    ROUND(pa.STL, 1) AS stl,
    pa.IS_SHOOTER
FROM player_archetypes pa
WHERE pa.SEASON = '2023-24'
ORDER BY pa.COMPOSITE_SCORE_NORM DESC
""")
print("  Created: v_rankings_2024")

# View 2: Archetype summary stats
cursor.execute("""
CREATE VIEW v_archetype_summary AS
SELECT
    ARCHETYPE,
    COUNT(*) AS player_count,
    ROUND(AVG(COMPOSITE_SCORE_NORM), 1) AS avg_score,
    ROUND(AVG(SALARY), 0) AS avg_salary,
    ROUND(AVG(VORPD), 2) AS avg_vorpd,
    ROUND(AVG(OFF_RATING_ADJUSTED), 2) AS avg_off_rtg,
    ROUND(AVG(DEF_RATING_ADJUSTED), 2) AS avg_def_rtg,
    ROUND(AVG(BLK), 2) AS avg_blk,
    ROUND(AVG(STL), 2) AS avg_stl
FROM player_archetypes
WHERE SEASON = '2023-24'
GROUP BY ARCHETYPE
ORDER BY avg_score DESC
""")
print("  Created: v_archetype_summary")

# View 3: Roster comparison across scenarios
cursor.execute("""
CREATE VIEW v_roster_comparison AS
SELECT
    r.SCENARIO,
    s.name AS scenario_name,
    s.salary_cap,
    COUNT(*) AS roster_size,
    ROUND(SUM(r.SALARY), 0) AS total_salary,
    ROUND(SUM(r.SALARY) * 100.0 / s.salary_cap, 1) AS cap_pct_used,
    ROUND(SUM(r.COMPOSITE_SCORE_NORM), 2) AS total_base_score,
    ROUND(AVG(r.COMPOSITE_SCORE_NORM), 2) AS avg_score
FROM optimized_rosters r
JOIN scenarios s ON r.SCENARIO = s.scenario
GROUP BY r.SCENARIO
ORDER BY r.SCENARIO
""")
print("  Created: v_roster_comparison")

# View 4: Top synergy pairs
cursor.execute("""
CREATE VIEW v_top_synergy_pairs AS
SELECT
    GROUP_NAME AS pair_name,
    ROUND(NET_SYNERGY, 2) AS net_synergy,
    ROUND(DEF_SYNERGY, 2) AS def_synergy,
    ROUND(OFF_SYNERGY, 2) AS off_synergy,
    MIN AS shared_minutes,
    ARCHETYPE_A,
    ARCHETYPE_B
FROM synergy_pairs
ORDER BY NET_SYNERGY DESC
""")
print("  Created: v_top_synergy_pairs")

# View 5: Best value players (highest VORPD)
cursor.execute("""
CREATE VIEW v_best_value AS
SELECT
    PLAYER_NAME,
    TEAM_ABBREVIATION AS team,
    ARCHETYPE,
    ROUND(COMPOSITE_SCORE_NORM, 2) AS score,
    SALARY,
    ROUND(VORPD, 2) AS vorpd,
    ROUND(COMPOSITE_SCORE_NORM / (SALARY / 1000000.0), 2) AS score_per_million
FROM player_archetypes
WHERE SEASON = '2023-24' AND SALARY > 0
ORDER BY VORPD DESC
""")
print("  Created: v_best_value")

# View 6: Player trajectory across seasons
cursor.execute("""
CREATE VIEW v_player_trajectory AS
SELECT
    PLAYER_NAME,
    SEASON,
    TEAM_ABBREVIATION AS team,
    ROUND(COMPOSITE_SCORE_NORM, 2) AS score,
    SALARY,
    ARCHETYPE
FROM player_archetypes
ORDER BY PLAYER_NAME, SEASON
""")
print("  Created: v_player_trajectory")

conn.commit()

# ============================================================
# SAVE SAMPLE QUERIES FILE
# ============================================================

queries_file = 'sql_queries.sql'
with open(queries_file, 'w', encoding='utf-8') as f:
    f.write("""-- ============================================================
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
""")

print(f"\nSaved: {queries_file} (20 sample queries)")

# ============================================================
# VERIFY
# ============================================================

print("\n--- Verification ---")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()
print(f"Tables: {[t[0] for t in tables]}")

cursor.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")
views = cursor.fetchall()
print(f"Views: {[v[0] for v in views]}")

# Test a query
cursor.execute("SELECT * FROM v_rankings_2024 LIMIT 5")
rows = cursor.fetchall()
print(f"\nTop 5 players (from v_rankings_2024):")
for row in rows:
    print(f"  #{row[0]} {row[1]:<28} {row[3]:<22} Score: {row[4]}")

conn.close()

print(f"\n{'=' * 60}")
print(f"DATABASE SAVED: {DB_FILE}")
print(f"{'=' * 60}")
print(f"\nTo explore:")
print(f"  1. Download 'DB Browser for SQLite' (free): https://sqlitebrowser.org/")
print(f"  2. Open {DB_FILE}")
print(f"  3. Go to 'Execute SQL' tab and run any query from {queries_file}")
print(f"\nOr from Python:")
print(f"  import sqlite3")
print(f"  conn = sqlite3.connect('{DB_FILE}')")
print(f"  pd.read_sql('SELECT * FROM v_rankings_2024 LIMIT 10', conn)")
