import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import pandas as pd
import numpy as np

print("Loading clustered dataset...")
df = pd.read_csv('nba_clustered.csv')

# ============================================================
# DYNAMIC ARCHETYPE LABELING
#
# The old approach used hardcoded cluster numbers → label mappings.
# This broke every time the data changed (dedup, salary fix, etc.)
# because K-means assigns arbitrary cluster IDs.
#
# New approach: identify each cluster by its statistical fingerprint.
# Rules are based on stable centroid properties, not cluster numbers.
# ============================================================

centroids = df.groupby('CLUSTER').agg({
    'COMPOSITE_SCORE_NORM': 'mean',
    'OFF_RATING_ADJUSTED': 'mean',
    'DEF_RATING_ADJUSTED': 'mean',
    'BLK': 'mean',
    'STL': 'mean',
    'ON_OFF_DIFF': 'mean',
    'AST_PCT_ADJUSTED': 'mean',
}).round(4)
centroids['SIZE'] = df.groupby('CLUSTER').size()

print("\nCluster centroids:")
print(centroids.to_string())

# ── Assign labels based on centroid statistics ───────────────────────────
labels = {}
used = set()

# 1. Elite Playmaker — highest COMPOSITE_SCORE_NORM
elite_id = centroids['COMPOSITE_SCORE_NORM'].idxmax()
labels[elite_id] = 'Elite Playmaker'
used.add(elite_id)

# 2. Two-Way Big — highest BLK (always BLK > 1.0)
remaining = centroids.drop(index=list(used))
big_id = remaining['BLK'].idxmax()
labels[big_id] = 'Two-Way Big'
used.add(big_id)

# 3. Defensive Wing — highest DEF_RATING_ADJUSTED among remaining
remaining = centroids.drop(index=list(used))
def_wing_id = remaining['DEF_RATING_ADJUSTED'].idxmax()
labels[def_wing_id] = 'Defensive Wing'
used.add(def_wing_id)

# 4. Versatile Scorer — highest STL among remaining (guard/wing playmakers)
remaining = centroids.drop(index=list(used))
versatile_id = remaining['STL'].idxmax()
labels[versatile_id] = 'Versatile Scorer'
used.add(versatile_id)

# 5. Perimeter Scorer — highest OFF_RATING_ADJUSTED among remaining
remaining = centroids.drop(index=list(used))
perim_id = remaining['OFF_RATING_ADJUSTED'].idxmax()
labels[perim_id] = 'Perimeter Scorer'
used.add(perim_id)

# 6-7. Remaining clusters → Bench / Role Player
for cid in centroids.index:
    if cid not in used:
        labels[cid] = 'Bench / Role Player'

df['ARCHETYPE'] = df['CLUSTER'].map(labels)

print("\nDynamic label assignment:")
for cid in sorted(labels.keys()):
    c = centroids.loc[cid]
    print(f"  Cluster {cid} → {labels[cid]:<22} "
          f"(comp={c['COMPOSITE_SCORE_NORM']:.1f}, BLK={c['BLK']:.2f}, "
          f"STL={c['STL']:.2f}, DEF_ADJ={c['DEF_RATING_ADJUSTED']:.2f}, "
          f"OFF_ADJ={c['OFF_RATING_ADJUSTED']:.2f}, n={int(c['SIZE'])})")

print("\nArchetype distribution:")
print(df['ARCHETYPE'].value_counts())

print("\nVerification — Top 5 players per archetype in 2023-24:")
df_2324 = df[df['SEASON'] == '2023-24']
for archetype in ['Elite Playmaker', 'Two-Way Big', 'Versatile Scorer',
                   'Perimeter Scorer', 'Defensive Wing', 'Bench / Role Player']:
    players = df_2324[df_2324['ARCHETYPE'] == archetype].sort_values(
        'COMPOSITE_SCORE_NORM', ascending=False
    )[['PLAYER_NAME', 'COMPOSITE_SCORE_NORM', 'ON_OFF_DIFF']].head(5)
    print(f"\n  {archetype}:")
    if len(players) > 0:
        print(players.to_string(index=False))
    else:
        print("  (no 2023-24 players)")

df.to_csv('nba_clustered.csv', index=False)
print("\nSaved corrected labels to nba_clustered.csv")
print("\nCLUSTERING PHASE COMPLETE")
