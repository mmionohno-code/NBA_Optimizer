import pandas as pd

print("Loading scored file...")
df = pd.read_csv('nba_scored_complete.csv')
print(f"Rows before dedup: {len(df)}")

# Remove exact duplicate rows
df = df.drop_duplicates()
print(f"Rows after removing exact duplicates: {len(df)}")

# Check for player-season duplicates (same player, same season, different row)
dupes = df.duplicated(subset=['PLAYER_NAME', 'SEASON'], keep=False)
if dupes.sum() > 0:
    print(f"\nPlayer-season duplicates remaining: {dupes.sum()}")
    print(df[dupes][['PLAYER_NAME', 'SEASON', 'COMPOSITE_SCORE_NORM']].head(10))
    # Keep the row with the higher composite score (player's best team in a traded season)
    df = df.sort_values('COMPOSITE_SCORE_NORM', ascending=False)
    df = df.drop_duplicates(subset=['PLAYER_NAME', 'SEASON'], keep='first')
    print(f"Rows after player-season dedup: {len(df)}")
else:
    print("No player-season duplicates found.")

# Flag players whose salary was imputed (league minimum)
# League minimums we assigned:
LEAGUE_MIN = {
    '2021-22': 925_258,
    '2022-23': 1_017_781,
    '2023-24': 1_119_563
}
df['SALARY_IMPUTED'] = df.apply(
    lambda row: row['SALARY'] == LEAGUE_MIN.get(row['SEASON'], 0),
    axis=1
)
imputed_count = df['SALARY_IMPUTED'].sum()
print(f"\nPlayers with imputed (minimum) salary: {imputed_count}")

# Recalculate VORPD — exclude imputed salaries from top value list
# (they're not real bargains, just missing data)
replacement_level = df['COMPOSITE_SCORE_NORM'].quantile(0.10)
df['VAR'] = (df['COMPOSITE_SCORE_NORM'] - replacement_level).clip(lower=0)
df['VORPD'] = (df['VAR'] / (df['SALARY'] / 1_000_000)).round(4)
df['VORPD_RELIABLE'] = df['VORPD'].where(~df['SALARY_IMPUTED'], other=None)

# Save clean version
df.to_csv('nba_scored_complete.csv', index=False)
print(f"\nClean file saved. Final row count: {len(df)}")

# Show corrected VORPD top 10 (reliable salaries only)
print("\nTop 10 best VALUE players in 2023-24 (reliable salary data only):")
best = df[
    (df['SEASON'] == '2023-24') & (~df['SALARY_IMPUTED'])
].sort_values('VORPD', ascending=False)[
    ['PLAYER_NAME', 'TEAM_ABBREVIATION', 'COMPOSITE_SCORE_NORM', 'SALARY', 'VORPD']
].head(10)
print(best.to_string(index=False))

print("\nTop 20 by composite score in 2023-24 (unchanged):")
top20 = df[df['SEASON'] == '2023-24'].sort_values(
    'COMPOSITE_SCORE_NORM', ascending=False)[
    ['PLAYER_NAME', 'TEAM_ABBREVIATION', 'COMPOSITE_SCORE_NORM', 'SALARY', 'VORPD']
].head(20)
print(top20.to_string(index=False))
