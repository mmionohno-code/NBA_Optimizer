from nba_api.stats.endpoints import leaguedashplayerstats
import pandas as pd
import time

seasons = ['2021-22', '2022-23', '2023-24']

# Recency weights — most recent season matters most
weights = {
    '2021-22': 0.20,
    '2022-23': 0.35,
    '2023-24': 0.45
}

all_seasons_traditional = []
all_seasons_advanced = []

for season in seasons:
    print(f"\nPulling traditional stats for {season}...")
    
    traditional = leaguedashplayerstats.LeagueDashPlayerStats(
        season=season,
        per_mode_detailed='PerGame',
        measure_type_detailed_defense='Base'
    )
    
    df_trad = traditional.get_data_frames()[0]
    df_trad['SEASON'] = season
    df_trad['SEASON_WEIGHT'] = weights[season]
    all_seasons_traditional.append(df_trad)
    
    print(f"Got {len(df_trad)} players for {season} traditional stats")
    time.sleep(3)
    
    print(f"Pulling advanced stats for {season}...")
    
    advanced = leaguedashplayerstats.LeagueDashPlayerStats(
        season=season,
        per_mode_detailed='PerGame',
        measure_type_detailed_defense='Advanced'
    )
    
    df_adv = advanced.get_data_frames()[0]
    df_adv['SEASON'] = season
    df_adv['SEASON_WEIGHT'] = weights[season]
    all_seasons_advanced.append(df_adv)
    
    print(f"Got {len(df_adv)} players for {season} advanced stats")
    time.sleep(3)

print("\nCombining all seasons...")

df_all_traditional = pd.concat(all_seasons_traditional, ignore_index=True)
df_all_advanced = pd.concat(all_seasons_advanced, ignore_index=True)

print("Merging traditional and advanced...")

df_merged = pd.merge(
    df_all_traditional,
    df_all_advanced,
    on=['PLAYER_ID', 'SEASON'],
    suffixes=('', '_adv')
)

print("Filtering to meaningful playing time...")
df_filtered = df_merged[
    (df_merged['GP'] >= 20) &
    (df_merged['MIN'] >= 10)
]

df_filtered.to_csv('nba_master_threeyears.csv', index=False)

print(f"\nDone! Total player seasons: {len(df_filtered)}")
print(f"Breakdown by season:")
print(df_filtered.groupby('SEASON')['PLAYER_ID'].count())