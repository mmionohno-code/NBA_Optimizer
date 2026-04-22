import pandas as pd

print("Loading three-year stats file...")
df_stats = pd.read_csv('nba_master_threeyears.csv')
print(f"Stats rows: {len(df_stats)}")

print("Loading salary data...")
df_sal = pd.read_csv('nba_salaries_threeyears.csv')
print(f"Salary rows: {len(df_sal)}")

# ============================================================
# CLEAN PLAYER NAMES FOR MERGING
# Names often mismatch between sources:
#   "Jaren Jackson Jr." vs "Jaren Jackson Jr"
#   "Nicolas Claxton" vs "Nic Claxton"
# We lowercase and strip whitespace to reduce mismatches
# ============================================================

df_stats['PLAYER_NAME_CLEAN'] = df_stats['PLAYER_NAME'].str.lower().str.strip()
df_sal['PLAYER_NAME_CLEAN'] = df_sal['PLAYER_NAME_CLEAN'].str.lower().str.strip()

# ============================================================
# MERGE ON PLAYER NAME + SEASON
# Left join keeps all stat rows — players without salary
# data get NaN, which we fill with league minimum below
# ============================================================

print("\nMerging on player name + season...")
df_merged = pd.merge(
    df_stats,
    df_sal[['PLAYER_NAME_CLEAN', 'SEASON', 'SALARY', 'CAP', 'CAP_PCT']],
    on=['PLAYER_NAME_CLEAN', 'SEASON'],
    how='left'
)

print(f"Merged rows: {len(df_merged)}")

matched = df_merged['SALARY'].notna().sum()
unmatched = df_merged['SALARY'].isna().sum()
print(f"Players with salary:    {matched}")
print(f"Players without salary: {unmatched}")

if unmatched > 0:
    missing = df_merged[df_merged['SALARY'].isna()][['PLAYER_NAME', 'SEASON']].drop_duplicates()
    print(f"\nFirst 20 unmatched players (will receive league minimum):")
    print(missing.head(20).to_string(index=False))

# ============================================================
# FILL MISSING SALARIES WITH LEAGUE MINIMUM
# Players who didn't match are likely on minimum contracts
# or two-way contracts
# Official NBA CBA league minimum by season
# ============================================================

LEAGUE_MIN = {
    '2021-22': 925_258,
    '2022-23': 1_017_781,
    '2023-24': 1_119_563
}

CAP_BY_SEASON = {
    '2021-22': 112_414_000,
    '2022-23': 123_655_000,
    '2023-24': 136_021_000
}

for season in ['2021-22', '2022-23', '2023-24']:
    min_sal = LEAGUE_MIN[season]
    cap = CAP_BY_SEASON[season]
    # Fill missing salaries with league minimum
    mask = (df_merged['SEASON'] == season) & (df_merged['SALARY'].isna())
    df_merged.loc[mask, 'SALARY'] = min_sal
    df_merged.loc[mask, 'CAP'] = cap
    df_merged.loc[mask, 'CAP_PCT'] = round(min_sal / cap * 100, 2)
    # Apply salary floor — no player can earn below league minimum
    # (cap-ratio scaling can push some salaries below the floor)
    season_mask = df_merged['SEASON'] == season
    df_merged.loc[season_mask, 'SALARY'] = df_merged.loc[season_mask, 'SALARY'].clip(lower=min_sal)

print(f"\nMissing salaries after fill: {df_merged['SALARY'].isna().sum()}")

# ============================================================
# FINAL FILTER — meaningful playing time
# ============================================================

df_final = df_merged[
    (df_merged['GP'] >= 20) &
    (df_merged['MIN'] >= 10)
].copy()

print(f"\nFinal dataset after playing time filter: {len(df_final)} player-seasons")
print(f"\nBreakdown by season:")
print(df_final.groupby('SEASON')['PLAYER_NAME'].count())

print(f"\nSalary stats by season:")
print(df_final.groupby('SEASON')['SALARY'].describe()[['min', 'mean', 'max']].round(0))

df_final.to_csv('nba_complete_master.csv', index=False)
print(f"\nSaved to nba_complete_master.csv")
print(f"Total columns: {len(df_final.columns)}")
print(f"Total player-seasons: {len(df_final)}")
