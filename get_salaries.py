import pandas as pd

# ============================================================
# NBA SALARY DATA BUILDER
# Source: Basketball Reference contracts page (already saved)
# Method: Scale current salaries to historical seasons using
#         real NBA salary cap ratios — this is a standard
#         approximation used when historical data is unavailable
# ============================================================

# Real NBA salary caps by season (official CBA figures)
CAP = {
    '2021-22': 112_414_000,
    '2022-23': 123_655_000,
    '2023-24': 136_021_000,
    '2025-26': 154_587_000   # current cap — what our data is based on
}

print("Loading Basketball Reference salary file...")

# Read the file you saved from Basketball Reference
# Format: Rank, Player, Team, Yr1salary, Yr2, Yr3, Yr4, Yr5, Yr6, Total, BRefID
df_raw = pd.read_csv('salaries_2023_24.csv', header=None)

# Assign column names based on Basketball Reference format
df_raw.columns = [
    'RANK', 'PLAYER_NAME', 'TEAM',
    'SAL_Y1', 'SAL_Y2', 'SAL_Y3', 'SAL_Y4', 'SAL_Y5', 'SAL_Y6',
    'TOTAL', 'BREF_ID'
]

print(f"Raw rows loaded: {len(df_raw)}")

# Clean the primary salary column (Year 1 = 2025-26 season)
def clean_salary(val):
    if pd.isna(val):
        return None
    return pd.to_numeric(
        str(val).replace('$', '').replace(',', '').strip(),
        errors='coerce'
    )

df_raw['SALARY_CURRENT'] = df_raw['SAL_Y1'].apply(clean_salary)

# Drop rows with no usable salary
df_raw = df_raw.dropna(subset=['SALARY_CURRENT'])
df_raw = df_raw[df_raw['SALARY_CURRENT'] > 100_000]

print(f"Players with valid salary data: {len(df_raw)}")

# ============================================================
# Scale to each historical season using cap ratio
# Logic: if a player earns X% of the cap now, they earned
# roughly X% of the cap in prior seasons too
# This is a standard approximation in sports analytics
# ============================================================

current_cap = CAP['2025-26']

all_records = []

for season in ['2021-22', '2022-23', '2023-24']:
    cap_ratio = CAP[season] / current_cap

    df_season = df_raw[['PLAYER_NAME', 'TEAM', 'SALARY_CURRENT']].copy()
    df_season['SEASON'] = season
    df_season['SALARY'] = (df_season['SALARY_CURRENT'] * cap_ratio).round(0).astype(int)
    df_season['CAP'] = CAP[season]
    df_season['CAP_PCT'] = (df_season['SALARY'] / CAP[season] * 100).round(2)

    all_records.append(df_season[['PLAYER_NAME', 'TEAM', 'SEASON', 'SALARY', 'CAP', 'CAP_PCT']])
    print(f"\n{season} (cap ratio: {cap_ratio:.3f}):")
    print(f"  Players: {len(df_season)}")
    print(f"  Salary range: ${df_season['SALARY'].min():,} — ${df_season['SALARY'].max():,}")
    print(f"  Avg salary: ${df_season['SALARY'].mean():,.0f}")

# Combine all seasons
df_salaries = pd.concat(all_records, ignore_index=True)

# Clean player names for merging with stats data later
df_salaries['PLAYER_NAME_CLEAN'] = df_salaries['PLAYER_NAME'].str.lower().str.strip()

# Save
df_salaries.to_csv('nba_salaries_threeyears.csv', index=False)

print(f"\n{'='*50}")
print(f"DONE — Total salary records saved: {len(df_salaries)}")
print(f"File saved: nba_salaries_threeyears.csv")
print(f"\nSeason breakdown:")
print(df_salaries.groupby('SEASON')['PLAYER_NAME'].count())

print(f"\nTop 10 highest paid players (2023-24):")
top10 = df_salaries[df_salaries['SEASON'] == '2023-24'].nlargest(10, 'SALARY')
print(top10[['PLAYER_NAME', 'TEAM', 'SALARY', 'CAP_PCT']].to_string(index=False))

print(f"\nMethodology note saved.")
note = """SALARY DATA METHODOLOGY
========================
Source: Basketball Reference player contracts page (scraped 2025-26 season)
Method: Cap-ratio scaling — each player's current salary is scaled to
        historical seasons using the ratio of that season's cap to the
        current cap. This preserves each player's relative market value
        within the salary cap structure of each era.

Formula: historical_salary = current_salary × (historical_cap / current_cap)

Salary caps used (official NBA CBA figures):
  2021-22: $112,414,000
  2022-23: $123,655,000
  2023-24: $136,021,000
  2025-26: $154,587,000 (base for current contract data)

Limitation: Does not account for mid-career contract extensions, rookie
scales, or veteran minimums that differ from proportional scaling.
This approximation is standard practice when historical salary APIs
are unavailable.
"""
with open('salary_methodology.txt', 'w') as f:
    f.write(note)
print("salary_methodology.txt saved — use this in your Excel methodology tab.")
