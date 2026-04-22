from nba_api.stats.endpoints import playercontractdetails
from nba_api.stats.static import players
import pandas as pd
import time

print("Getting all active players...")
all_players = players.get_active_players()
print(f"Total active players: {len(all_players)}")

salary_data = []

for i, player in enumerate(all_players):
    try:
        contract = playercontractdetails.PlayerContractDetails(
            player_id=player['id']
        )
        df = contract.get_data_frames()[0]
        if len(df) > 0:
            df['PLAYER_NAME'] = player['full_name']
            df['PLAYER_ID'] = player['id']
            salary_data.append(df)
        
        if i % 10 == 0:
            print(f"Progress: {i}/{len(all_players)} players done")
        
        time.sleep(0.5)
        
    except Exception as e:
        print(f"Error for {player['full_name']}: {e}")
        continue

df_salaries = pd.concat(salary_data, ignore_index=True)
df_salaries.to_csv('nba_salaries_api.csv', index=False)
print(f"\nDone! Got salary data for {len(df_salaries)} players")
print(df_salaries.head())