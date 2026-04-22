import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

print("=" * 60)
print("NBA PLAYER ARCHETYPE CLUSTERING — K-MEANS")
print("=" * 60)

print("\nLoading scored dataset...")
df = pd.read_csv('nba_scored_complete.csv')
print(f"Total player-seasons: {len(df)}")

# ============================================================
# THE 9 STATS WE USE FOR CLUSTERING
# Same stats that went into PCA — each captures a different
# dimension of player skill
# ============================================================

CLUSTER_STATS = [
    'OFF_RATING_ADJUSTED',   # offensive impact above team avg
    'DEF_RATING_ADJUSTED',   # defensive impact above team avg
    'AST_PCT_ADJUSTED',      # playmaking above team avg
    'DREB_PCT_ADJUSTED',     # rebounding above team avg
    'BLK',                   # shot blocking
    'STL',                   # perimeter disruption
    'TS_PCT',                # shooting efficiency
    'FG3_PCT',               # three-point shooting
    'PIE_ADJUSTED',          # overall impact above team avg
]

# Drop rows with missing values in any cluster stat
df_cluster = df[CLUSTER_STATS + ['PLAYER_NAME', 'TEAM_ABBREVIATION',
                                  'SEASON', 'COMPOSITE_SCORE_NORM',
                                  'SALARY', 'VORPD']].dropna()
print(f"Players with complete data for clustering: {len(df_cluster)}")

# ============================================================
# STANDARDIZE STATS
# K-Means is distance-based — stats on different scales would
# distort cluster assignments. StandardScaler fixes that.
# ============================================================

scaler = StandardScaler()
X = scaler.fit_transform(df_cluster[CLUSTER_STATS])

# ============================================================
# ELBOW METHOD — Find optimal number of clusters
# We plot inertia (sum of squared distances to cluster center)
# vs K. The "elbow" where improvement slows = optimal K.
# ============================================================

print("\nRunning elbow method (K=2 to 12)...")

inertias = []
k_range = range(2, 13)

for k in k_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(X)
    inertias.append(km.inertia_)
    print(f"  K={k}: inertia={km.inertia_:.1f}")

plt.figure(figsize=(10, 5))
plt.plot(list(k_range), inertias, 'bo-', linewidth=2, markersize=8)
plt.xlabel('Number of Clusters (K)', fontsize=12)
plt.ylabel('Inertia (lower = tighter clusters)', fontsize=12)
plt.title('Elbow Method — Finding Optimal Number of Archetypes', fontsize=13)
plt.xticks(list(k_range))
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('elbow_method.png')
plt.close()
print("Elbow chart saved: elbow_method.png")

# ============================================================
# RUN K-MEANS WITH K=7
# 7 captures the main NBA archetypes without over-splitting:
# We'll validate this choice against basketball intuition
# ============================================================

K = 7
print(f"\nRunning K-Means with K={K}...")

kmeans = KMeans(n_clusters=K, random_state=42, n_init=20)
df_cluster = df_cluster.copy()
df_cluster['CLUSTER'] = kmeans.fit_predict(X)

# ============================================================
# ANALYZE EACH CLUSTER
# Look at the average stats per cluster to understand
# what basketball archetype each cluster represents
# ============================================================

print("\n" + "=" * 40)
print("CLUSTER ANALYSIS — Average Stats Per Cluster")
print("=" * 40)

cluster_summary = df_cluster.groupby('CLUSTER')[CLUSTER_STATS + ['COMPOSITE_SCORE_NORM']].mean().round(3)
cluster_sizes = df_cluster.groupby('CLUSTER').size().rename('SIZE')
cluster_summary = cluster_summary.join(cluster_sizes)

print("\nCluster averages (sorted by composite score):")
print(cluster_summary.sort_values('COMPOSITE_SCORE_NORM', ascending=False).to_string())

print("\nTop 5 players per cluster (by composite score in 2023-24):")
for cluster_id in range(K):
    cluster_players = df_cluster[
        (df_cluster['CLUSTER'] == cluster_id) &
        (df_cluster['SEASON'] == '2023-24')
    ].sort_values('COMPOSITE_SCORE_NORM', ascending=False)

    print(f"\n  Cluster {cluster_id} (size: {(df_cluster['CLUSTER'] == cluster_id).sum()}):")
    if len(cluster_players) > 0:
        print(cluster_players[['PLAYER_NAME', 'COMPOSITE_SCORE_NORM',
                                 'SALARY']].head(5).to_string(index=False))
    else:
        print("  No 2023-24 players in this cluster")

# ============================================================
# ASSIGN ARCHETYPE NAMES
# Based on the cluster stats, we label each cluster with a
# meaningful basketball role. You can rename these after
# reviewing the output — this is the analytical judgment step.
# ============================================================

print("\n" + "=" * 40)
print("ARCHETYPE LABELING")
print("=" * 40)

# We assign names based on which stats are highest in each cluster.
# The logic: find the 2-3 defining characteristics per cluster.

archetype_map = {}

for cluster_id in range(K):
    stats = cluster_summary.loc[cluster_id, CLUSTER_STATS]

    # Rank this cluster on each stat relative to all clusters
    # to find its defining strengths
    ranks = {}
    for stat in CLUSTER_STATS:
        col_vals = cluster_summary[stat]
        ranks[stat] = (col_vals.rank(ascending=True)[cluster_id]) / K

    # Identify top 3 defining stats (above 0.7 percentile among clusters)
    defining = [s for s, r in sorted(ranks.items(), key=lambda x: -x[1]) if r >= 0.6][:3]

    # Auto-label based on dominant stats
    if 'AST_PCT_ADJUSTED' in defining[:2] and 'FG3_PCT' in defining:
        label = 'Perimeter Playmaker'
    elif 'AST_PCT_ADJUSTED' in defining[:1] and 'OFF_RATING_ADJUSTED' in defining:
        label = 'Playmaking Hub'
    elif 'BLK' in defining[:2] and 'DREB_PCT_ADJUSTED' in defining:
        label = 'Rim Protector'
    elif 'DREB_PCT_ADJUSTED' in defining[:2] and 'PIE_ADJUSTED' in defining:
        label = 'Rebounding Big'
    elif 'FG3_PCT' in defining[:2] and 'STL' in defining:
        label = '3-and-D Wing'
    elif 'FG3_PCT' in defining[:2]:
        label = 'Floor Spacer'
    elif 'STL' in defining[:2] and 'AST_PCT_ADJUSTED' in defining:
        label = 'Two-Way Guard'
    elif 'OFF_RATING_ADJUSTED' in defining[:1] and 'TS_PCT' in defining:
        label = 'Scoring Wing'
    elif 'PIE_ADJUSTED' in defining[:1] and 'OFF_RATING_ADJUSTED' in defining:
        label = 'Impact Big'
    else:
        label = f'Role Player (C{cluster_id})'

    archetype_map[cluster_id] = label
    print(f"  Cluster {cluster_id} → '{label}'  |  Defining stats: {defining}")

df_cluster['ARCHETYPE'] = df_cluster['CLUSTER'].map(archetype_map)

print("\nArchetype distribution:")
print(df_cluster['ARCHETYPE'].value_counts())

# ============================================================
# VISUALIZE CLUSTERS IN 2D USING PCA
# We reduce 9 stats to 2 dimensions just for plotting.
# This is only for visualization — clustering was done
# on all 9 stats.
# ============================================================

print("\nBuilding cluster visualization...")

pca_2d = PCA(n_components=2)
coords = pca_2d.fit_transform(X)
df_cluster['PCA_X'] = coords[:, 0]
df_cluster['PCA_Y'] = coords[:, 1]

colors = plt.cm.Set1(np.linspace(0, 1, K))
archetype_colors = {archetype_map[i]: colors[i] for i in range(K)}

plt.figure(figsize=(14, 9))
for cluster_id in range(K):
    mask = df_cluster['CLUSTER'] == cluster_id
    label = archetype_map[cluster_id]
    plt.scatter(
        df_cluster.loc[mask, 'PCA_X'],
        df_cluster.loc[mask, 'PCA_Y'],
        c=[colors[cluster_id]],
        label=f"{label} (n={mask.sum()})",
        alpha=0.6,
        s=40
    )

# Annotate notable players
notable = ['Nikola Jokić', 'Joel Embiid', 'Victor Wembanyama',
           'Luka Dončić', 'Stephen Curry', 'LeBron James',
           'Rudy Gobert', 'Shai Gilgeous-Alexander', 'Giannis Antetokounmpo']
df_2324 = df_cluster[df_cluster['SEASON'] == '2023-24']
for name in notable:
    row = df_2324[df_2324['PLAYER_NAME'] == name]
    if len(row) > 0:
        plt.annotate(
            name.split()[-1],
            (row['PCA_X'].values[0], row['PCA_Y'].values[0]),
            fontsize=8, fontweight='bold',
            xytext=(5, 5), textcoords='offset points'
        )

plt.xlabel(f'PCA Dimension 1 ({pca_2d.explained_variance_ratio_[0]*100:.1f}% variance)', fontsize=11)
plt.ylabel(f'PCA Dimension 2 ({pca_2d.explained_variance_ratio_[1]*100:.1f}% variance)', fontsize=11)
plt.title('NBA Player Archetypes — K-Means Clustering (K=7)\n3 Seasons Combined, 9 Stats', fontsize=13)
plt.legend(loc='upper right', fontsize=9)
plt.tight_layout()
plt.savefig('cluster_visualization.png')
plt.close()
print("Cluster visualization saved: cluster_visualization.png")

# ============================================================
# RADAR CHART — Average stat profile per archetype
# ============================================================

stats_for_radar = ['OFF_RATING_ADJUSTED', 'DEF_RATING_ADJUSTED',
                   'AST_PCT_ADJUSTED', 'DREB_PCT_ADJUSTED',
                   'BLK', 'STL', 'TS_PCT', 'FG3_PCT']

# Normalize each stat to 0-1 across all players for radar
df_radar = df_cluster[stats_for_radar].copy()
for col in stats_for_radar:
    col_min = df_radar[col].min()
    col_max = df_radar[col].max()
    df_radar[col] = (df_radar[col] - col_min) / (col_max - col_min)

df_radar['ARCHETYPE'] = df_cluster['ARCHETYPE'].values

radar_means = df_radar.groupby('ARCHETYPE')[stats_for_radar].mean()

fig, axes = plt.subplots(2, 4, figsize=(18, 10), subplot_kw=dict(polar=True))
axes = axes.flatten()

labels = [s.replace('_ADJUSTED', '').replace('_', '\n') for s in stats_for_radar]
N = len(stats_for_radar)
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]

for idx, (archetype, row) in enumerate(radar_means.iterrows()):
    if idx >= len(axes):
        break
    ax = axes[idx]
    values = row.tolist() + [row.tolist()[0]]
    ax.plot(angles, values, linewidth=2, color=colors[idx % K])
    ax.fill(angles, values, alpha=0.25, color=colors[idx % K])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, size=7)
    ax.set_ylim(0, 1)
    ax.set_title(archetype, size=10, fontweight='bold', pad=15)
    ax.set_yticks([])

# Hide unused subplots
for idx in range(len(radar_means), len(axes)):
    axes[idx].set_visible(False)

plt.suptitle('NBA Archetype Stat Profiles — Radar Charts', fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig('archetype_radar_charts.png', bbox_inches='tight')
plt.close()
print("Radar charts saved: archetype_radar_charts.png")

# ============================================================
# SAVE FINAL LABELED DATASET
# ============================================================

df_cluster.to_csv('nba_clustered.csv', index=False)
print("\nLabeled dataset saved: nba_clustered.csv")

print("\n" + "=" * 60)
print("CLUSTERING COMPLETE")
print(f"Total players clustered: {len(df_cluster)}")
print(f"Archetypes discovered:")
for cid, name in archetype_map.items():
    n = (df_cluster['CLUSTER'] == cid).sum()
    print(f"  {name}: {n} player-seasons")
print("=" * 60)
print("\nNEXT STEP: Review the archetype labels above.")
print("If any label doesn't match the players listed, let me know")
print("and we'll rename it to match the basketball reality.")
