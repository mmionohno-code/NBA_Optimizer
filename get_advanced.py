from nba_api.stats.endpoints import leaguedashplayerstats
import pandas as pd
import time

print("Pulling advanced stats...")

advanced = leaguedashplayerstats.LeagueDashPlayerStats(
    season='2023-24',
    per_mode_detailed='Per100Possessions',
    measure_type_detailed_defense='Advanced'
)

time.sleep(2)

df_advanced = advanced.get_data_frames()[0]

df_advanced.to_csv('player_advanced.csv', index=False)
print("Advanced stats saved!")
print(df_advanced.columns.tolist())