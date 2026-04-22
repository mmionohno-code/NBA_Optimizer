import pandas as pd

print("Loading clustered dataset...")
df = pd.read_csv('nba_clustered.csv')

# ============================================================
# CORRECTED ARCHETYPE LABELS
# Based on analysis of each cluster's average stats
# and the basketball identity of the players in each cluster
# ============================================================

correct_labels = {
    0: 'Bench / Fringe Player',    # Low impact, fringe roster spots
    1: 'Elite Two-Way Big',         # Embiid, Jokic, Wembanyama, AD, Giannis
    2: 'Defensive Specialist',      # OG Anunoby, Josh Hart, Covington — elite DEF_RATING
    3: 'Perimeter Playmaker',       # SGA, Luka, LeBron, Kawhi — high OFF_RATING + STL
    4: 'Rim Protector',             # Gobert, Gafford, Drummond, Duren — high BLK + DREB
    5: '3-and-D Wing',              # Gordon, Allen, DiVincenzo — FG3_PCT + STL
    6: 'Stretch Big',               # KAT, Markkanen, Jonas — bigs who shoot threes
}

df['ARCHETYPE'] = df['CLUSTER'].map(correct_labels)

print("\nCorrected archetype distribution:")
print(df['ARCHETYPE'].value_counts())

print("\nVerification — Top 5 players per archetype in 2023-24:")
df_2324 = df[df['SEASON'] == '2023-24']
for archetype in correct_labels.values():
    players = df_2324[df_2324['ARCHETYPE'] == archetype].sort_values(
        'COMPOSITE_SCORE_NORM', ascending=False
    )[['PLAYER_NAME', 'COMPOSITE_SCORE_NORM', 'SALARY']].head(5)
    print(f"\n  {archetype}:")
    if len(players) > 0:
        print(players.to_string(index=False))
    else:
        print("  (no 2023-24 players)")

df.to_csv('nba_clustered.csv', index=False)
print("\nSaved corrected labels to nba_clustered.csv")
print("\nCLUSTERING PHASE COMPLETE")
print("Ready for Week 4 — MILP Optimization")
