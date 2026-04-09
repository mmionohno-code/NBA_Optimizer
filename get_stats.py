from nba_api.stats.endpoints import leaguedashplayerstats
import pandas as pd

print("Pulling player stats from NBA.com... this may take 30 seconds")

stats = leaguedashplayerstats.LeagueDashPlayerStats(
    season='2023-24',
    per_mode_detailed='PerGame'
)

df = stats.get_data_frames()[0]

print("Success! Here are the first 5 players:")
print(df.head())

print("Total players pulled:", len(df))

df.to_csv('player_stats.csv', index=False)
print("Saved to player_stats.csv")