"""
09_verify_pipeline.py — Automated Pipeline Verification
=========================================================
Run after the full pipeline (01→08) to catch cascading errors.

Checks ~25 conditions across all intermediate and final outputs.
Any failure prints exactly what broke and where.

Usage:  python 09_verify_pipeline.py
"""

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import os
import pandas as pd
import re

# ── Config ───────────────────────────────────────────────────────────────────

VALID_ARCHETYPES = {
    'Elite Playmaker', 'Two-Way Big', 'Versatile Scorer',
    'Perimeter Scorer', 'Defensive Wing', 'Bench / Role Player'
}

STALE_ARCHETYPES = {
    'Two-Way Guard', 'Floor Spacer', 'Rim Protector',
    'Role Player (C0)', 'Role Player (C1)', 'Role Player (C6)'
}

SCENARIO_CAPS = {
    'A': 136_021_000, 'B': 165_294_000, 'C': 90_000_000,
    'D': 136_021_000, 'E': 165_294_000, 'F': 136_021_000,
    'G': 136_021_000, 'H': 136_021_000, 'I': 136_021_000,
    'J': 136_021_000,
}

ARCHETYPE_MINIMUMS = {
    'Elite Playmaker': 1, 'Versatile Scorer': 2, 'Defensive Wing': 1,
    'Perimeter Scorer': 2, 'Two-Way Big': 2, 'Bench / Role Player': 1,
}

# Small-ball (I) relaxes Two-Way Big minimum
SMALL_BALL_EXEMPT = {'I'}

LEAGUE_MIN = 1_119_563

# Known superstars for sanity checks (partial name match)
TOP_3_POOL = ['Joki', 'Gilgeous-Alexander', 'Luka']   # partial match handles ć/č
TOP_10_POOL = ['Embiid', 'Giannis', 'LeBron', 'Brunson', 'Haliburton',
               'Mitchell', 'LaMelo']

# ── Test Framework ───────────────────────────────────────────────────────────

passed = 0
failed = 0
errors = []

def check(condition, description, detail=''):
    global passed, failed
    if condition:
        passed += 1
        print(f"  [PASS] {description}")
    else:
        failed += 1
        msg = f"  [FAIL] {description}"
        if detail:
            msg += f"\n         → {detail}"
        print(msg)
        errors.append(description)

def name_match(player_name, search_term):
    return search_term.lower() in player_name.lower()

# ── Load Data ────────────────────────────────────────────────────────────────

print("=" * 60)
print("NBA PIPELINE VERIFICATION")
print("=" * 60)

# Check files exist
scored_path = 'nba_scored_complete.csv'
clustered_path = 'nba_clustered.csv'
synergy_path = 'nba_synergy_2324.csv'
profile_path = 'nba_def_synergy_profile.csv'
arch_syn_path = 'nba_archetype_synergy.csv'

for path in [scored_path, clustered_path, synergy_path, profile_path, arch_syn_path]:
    check(os.path.exists(path), f"File exists: {path}")

df_scored = pd.read_csv(scored_path)
df_clust = pd.read_csv(clustered_path)
df_syn = pd.read_csv(synergy_path)
df_prof = pd.read_csv(profile_path)

# ── 1. Data Integrity ────────────────────────────────────────────────────────

print("\n--- 1. DATA INTEGRITY ---")

for label, df in [('scored', df_scored), ('clustered', df_clust)]:
    for season in ['2021-22', '2022-23', '2023-24']:
        sub = df[df['SEASON'] == season]
        dupes = len(sub) - sub['PLAYER_NAME'].nunique()
        check(dupes == 0,
              f"No duplicates in {label} ({season})",
              f"Found {dupes} duplicate player rows" if dupes else '')

    total = len(df)
    check(1100 <= total <= 1300,
          f"Total rows in {label}: {total} (expected ~1185)",
          f"Got {total}" if not (1100 <= total <= 1300) else '')

    for season in ['2021-22', '2022-23', '2023-24']:
        n = len(df[df['SEASON'] == season])
        check(370 <= n <= 420,
              f"Player count {label} {season}: {n} (expected 380-410)",
              f"Got {n}" if not (370 <= n <= 420) else '')

# NaN checks
for col in ['COMPOSITE_SCORE_NORM', 'SALARY']:
    nans = df_scored[col].isna().sum()
    check(nans == 0, f"No NaN in scored.{col}", f"Found {nans} NaN" if nans else '')

for col in ['COMPOSITE_SCORE_NORM', 'SALARY', 'ARCHETYPE']:
    nans = df_clust[col].isna().sum()
    check(nans == 0, f"No NaN in clustered.{col}", f"Found {nans} NaN" if nans else '')

# Score range
score_min = df_scored['COMPOSITE_SCORE_NORM'].min()
score_max = df_scored['COMPOSITE_SCORE_NORM'].max()
check(score_min >= 0 and score_max <= 100,
      f"Composite score range: {score_min:.1f}-{score_max:.1f} (expected 0-100)",
      f"Out of range: {score_min:.1f}-{score_max:.1f}" if not (score_min >= 0 and score_max <= 100) else '')

# ── 2. Column Flow ──────────────────────────────────────────────────────────

print("\n--- 2. COLUMN FLOW ---")

scored_required = ['IS_SHOOTER', 'PLAYER_ID', 'COMPOSITE_SCORE_NORM',
                    'SALARY', 'SEASON_WEIGHT', 'VORPD']
for col in scored_required:
    check(col in df_scored.columns,
          f"scored has {col}",
          f"MISSING — downstream scripts need this" if col not in df_scored.columns else '')

clust_required = ['IS_SHOOTER', 'PLAYER_ID', 'ARCHETYPE', 'CLUSTER',
                   'COMPOSITE_SCORE_NORM', 'SALARY']
for col in clust_required:
    check(col in df_clust.columns,
          f"clustered has {col}",
          f"MISSING — optimizer/dashboard needs this" if col not in df_clust.columns else '')

# ── 3. Archetype Integrity ──────────────────────────────────────────────────

print("\n--- 3. ARCHETYPE INTEGRITY ---")

actual_archs = set(df_clust['ARCHETYPE'].dropna().unique())
check(actual_archs == VALID_ARCHETYPES,
      f"Exactly 6 valid archetypes",
      f"Got: {actual_archs}" if actual_archs != VALID_ARCHETYPES else '')

stale_found = actual_archs & STALE_ARCHETYPES
check(len(stale_found) == 0,
      "No stale archetype names",
      f"Found stale labels: {stale_found}" if stale_found else '')

# Check that Elite Playmaker contains actual superstars (2023-24 only)
df_2324 = df_clust[df_clust['SEASON'] == '2023-24']
elite_2324 = df_2324[df_2324['ARCHETYPE'] == 'Elite Playmaker']
elite_names = elite_2324['PLAYER_NAME'].tolist()
jokic_in_elite = any(name_match(n, 'Joki') for n in elite_names)
check(jokic_in_elite,
      f"Jokic is in Elite Playmaker (2023-24, {len(elite_names)} players)",
      f"Elite Playmaker 2023-24: {elite_names[:5]}" if not jokic_in_elite else '')

# ── 4. Rankings Sanity ──────────────────────────────────────────────────────

print("\n--- 4. RANKINGS SANITY ---")

top20 = df_2324.sort_values('COMPOSITE_SCORE_NORM', ascending=False).head(20)
top3_names = top20.head(3)['PLAYER_NAME'].tolist()
top10_names = top20.head(10)['PLAYER_NAME'].tolist()

top3_matches = sum(1 for pool in TOP_3_POOL
                   if any(name_match(n, pool) for n in top3_names))
check(top3_matches >= 2,
      f"Top 3 includes >=2 of Jokic/SGA/Luka (found {top3_matches})",
      f"Top 3: {top3_names}" if top3_matches < 2 else '')

top10_matches = sum(1 for pool in TOP_10_POOL
                    if any(name_match(n, pool) for n in top10_names))
check(top10_matches >= 3,
      f"Top 10 includes >=3 known stars (found {top10_matches})",
      f"Top 10: {top10_names}" if top10_matches < 3 else '')

min_score_top20 = top20['COMPOSITE_SCORE_NORM'].min()
check(min_score_top20 >= 50,
      f"No fringe player in top 20 (min score: {min_score_top20:.1f})",
      f"Lowest score in top 20: {min_score_top20:.1f}" if min_score_top20 < 50 else '')

# ── 5. Salary Sanity ────────────────────────────────────────────────────────

print("\n--- 5. SALARY SANITY ---")

butler = df_2324[df_2324['PLAYER_NAME'].str.contains('Butler', case=False, na=False)]
if len(butler):
    sal = butler.iloc[0]['SALARY']
    check(sal > 40_000_000,
          f"Jimmy Butler salary: ${sal:,.0f}",
          f"Expected >$40M, got ${sal:,.0f}" if sal <= 40_000_000 else '')

# High-PPG players at league min (need PTS from master)
if 'PTS' in df_2324.columns:
    bad_salary = df_2324[(df_2324['PTS'] > 15) & (df_2324['SALARY'] == LEAGUE_MIN)]
    check(len(bad_salary) == 0,
          "No stars (PTS>15) at league minimum",
          f"Found {len(bad_salary)}: {bad_salary['PLAYER_NAME'].tolist()}" if len(bad_salary) else '')
else:
    # PTS may not be in clustered — check scored
    df_scored_2324 = df_scored[df_scored['SEASON'] == '2023-24']
    if 'PTS' in df_scored_2324.columns:
        bad_salary = df_scored_2324[(df_scored_2324['PTS'] > 15) & (df_scored_2324['SALARY'] == LEAGUE_MIN)]
        check(len(bad_salary) == 0,
              "No stars (PTS>15) at league minimum",
              f"Found {len(bad_salary)}" if len(bad_salary) else '')
    else:
        print("  [SKIP] PTS column not in scored/clustered — checking master directly")
        df_master = pd.read_csv('nba_complete_master.csv')
        df_m24 = df_master[df_master['SEASON'] == '2023-24']
        bad_salary = df_m24[(df_m24['PTS'] > 15) & (df_m24['SALARY'] == LEAGUE_MIN)]
        check(len(bad_salary) == 0,
              "No stars (PTS>15) at league minimum in master data",
              f"Found: {bad_salary['PLAYER_NAME'].tolist()}" if len(bad_salary) else '')

sal_max = df_2324['SALARY'].max()
check(sal_max < 55_000_000,
      f"Max salary reasonable: ${sal_max:,.0f}",
      f"Suspiciously high: ${sal_max:,.0f}" if sal_max >= 55_000_000 else '')

sal_min = df_2324['SALARY'].min()
check(sal_min > 0,
      f"Min salary > $0: ${sal_min:,.0f}",
      f"Invalid salary: ${sal_min:,.0f}" if sal_min <= 0 else '')

# ── 6. Optimizer Rosters ────────────────────────────────────────────────────

print("\n--- 6. OPTIMIZER ROSTERS ---")

for key, cap in SCENARIO_CAPS.items():
    path = f'optimized_roster_syn_{key}.csv'
    if not os.path.exists(path):
        check(False, f"Roster {key} file exists")
        continue

    roster = pd.read_csv(path)

    # 15 unique players
    check(len(roster) == 15 and roster['PLAYER_NAME'].nunique() == 15,
          f"Roster {key}: 15 unique players",
          f"Got {len(roster)} rows, {roster['PLAYER_NAME'].nunique()} unique" if
          not (len(roster) == 15 and roster['PLAYER_NAME'].nunique() == 15) else '')

    # Salary under cap
    total_sal = roster['SALARY'].sum()
    check(total_sal <= cap,
          f"Roster {key}: salary ${total_sal/1e6:.1f}M <= cap ${cap/1e6:.1f}M",
          f"Over cap by ${(total_sal-cap)/1e6:.1f}M" if total_sal > cap else '')

    # Valid archetypes only
    roster_archs = set(roster['ARCHETYPE'].unique())
    invalid = roster_archs - VALID_ARCHETYPES
    check(len(invalid) == 0,
          f"Roster {key}: all archetypes valid",
          f"Invalid: {invalid}" if invalid else '')

    # Archetype minimums (skip Two-Way Big min for small ball)
    for arch, min_count in ARCHETYPE_MINIMUMS.items():
        if key in SMALL_BALL_EXEMPT and arch == 'Two-Way Big':
            continue
        actual_count = (roster['ARCHETYPE'] == arch).sum()
        check(actual_count >= min_count,
              f"Roster {key}: {arch} >= {min_count} (has {actual_count})",
              f"Only {actual_count}, need {min_count}" if actual_count < min_count else '')

    # Defensive constraints (BLK/STL come from master merge — check if available)
    if 'BLK' in roster.columns:
        paint = (roster['BLK'] >= 1.5).sum()
        check(paint >= 1,
              f"Roster {key}: paint protector (BLK>=1.5): {paint}",
              f"No player with BLK>=1.5" if paint < 1 else '')

    if 'STL' in roster.columns:
        perim = (roster['STL'] >= 1.3).sum()
        check(perim >= 2,
              f"Roster {key}: perimeter disruptors (STL>=1.3): {perim}",
              f"Only {perim}, need 2" if perim < 2 else '')

    # Team diversity
    team_max = roster['TEAM_ABBREVIATION'].value_counts().max()
    check(team_max <= 2,
          f"Roster {key}: max players per team = {team_max} (<=2)",
          f"Team has {team_max} players" if team_max > 2 else '')

# ── 7. Synergy Files ────────────────────────────────────────────────────────

print("\n--- 7. SYNERGY FILES ---")

check(len(df_syn) >= 1000,
      f"Synergy pairs: {len(df_syn)} (expected >1000)",
      f"Only {len(df_syn)}" if len(df_syn) < 1000 else '')

check(len(df_prof) >= 300,
      f"Player synergy profiles: {len(df_prof)} (expected >300)",
      f"Only {len(df_prof)}" if len(df_prof) < 300 else '')

check(os.path.exists(arch_syn_path),
      "Archetype synergy file exists")

# Check synergy file has required columns
syn_required = ['PLAYER_A_ID', 'PLAYER_B_ID', 'W_NET_SYNERGY_SCALED']
for col in syn_required:
    check(col in df_syn.columns,
          f"Synergy file has {col}",
          f"MISSING" if col not in df_syn.columns else '')

prof_required = ['PLAYER_ID', 'PLAYER_NAME', 'NET_SYNERGY_PROFILE']
for col in prof_required:
    check(col in df_prof.columns,
          f"Profile file has {col}",
          f"MISSING" if col not in df_prof.columns else '')

# ── Summary ──────────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
total = passed + failed
if failed == 0:
    print(f"RESULT: ALL {total} CHECKS PASSED")
else:
    print(f"RESULT: {passed}/{total} passed, {failed} FAILED")
    print("\nFailed checks:")
    for e in errors:
        print(f"  - {e}")
print("=" * 60)

sys.exit(1 if failed else 0)
