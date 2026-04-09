import pandas as pd

print("Loading all files...")

df_stats = pd.read_csv('player_stats.csv')
df_advanced = pd.read_csv('player_advanced.csv')

print("Merging stats...")
df_merged = pd.merge(df_stats, df_advanced, on='PLAYER_ID', suffixes=('', '_adv'))

print("Filtering to meaningful playing time...")
df_final = df_merged[(df_merged['GP'] >= 20) & (df_merged['MIN'] >= 10)]

df_final.to_csv('nba_master.csv', index=False)
print("Master file saved with", len(df_final), "players")
print(df_final.head())