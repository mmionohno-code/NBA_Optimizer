import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy.stats import spearmanr, pearsonr

print("=" * 60)
print("NBA PLAYER SCORING MODEL — FEATURE ENGINEERING")
print("=" * 60)

print("\nLoading complete master dataset...")
df = pd.read_csv('nba_complete_master.csv')
print(f"Total player-seasons loaded: {len(df)}")
print(f"Seasons: {sorted(df['SEASON'].unique())}")

# ============================================================
# STEP 1 — TEAM CONTEXT ADJUSTMENTS
# ============================================================

print("\n" + "=" * 40)
print("STEP 1: Team Context Adjustments")
print("=" * 40)

df = df.copy()

stats_to_adjust = ['OFF_RATING', 'DEF_RATING', 'NET_RATING',
                   'PIE', 'AST_PCT', 'DREB_PCT', 'OREB_PCT']

for stat in stats_to_adjust:
    if stat in df.columns:
        team_avg = df.groupby(['TEAM_ABBREVIATION', 'SEASON'])[stat].transform('mean')
        df[f'{stat}_ADJUSTED'] = df[stat] - team_avg
        print(f"  Adjusted: {stat}")

# DEF_RATING: lower is better for defense, so flip it
df['DEF_RATING_ADJUSTED'] = df['DEF_RATING_ADJUSTED'] * -1
print("  DEF_RATING_ADJUSTED flipped (higher = better defense)")

# Adjust PLUS_MINUS for team context (used in Framework 3)
pm_team_avg = df.groupby(['TEAM_ABBREVIATION', 'SEASON'])['PLUS_MINUS'].transform('mean')
df['PLUS_MINUS_ADJUSTED'] = df['PLUS_MINUS'] - pm_team_avg

# ============================================================
# STEP 2 — FILTER TS_PCT BY MINIMUM SHOT ATTEMPTS
# FGA in our dataset is per-game average.
# Total FGA = GP * FGA. Threshold = 100 total attempts.
# ============================================================

print("\n" + "=" * 40)
print("STEP 2: Filter Shooting Stats by Sample Size")
print("=" * 40)

# Calculate total field goal attempts
df['TOTAL_FGA'] = df['GP'] * df['FGA']

for season in df['SEASON'].unique():
    mask = df['SEASON'] == season
    reliable_mask = mask & (df['TOTAL_FGA'] >= 100)
    reliable_ts = df.loc[reliable_mask, 'TS_PCT'].dropna()

    if len(reliable_ts) > 0:
        league_avg_ts = reliable_ts.mean()
        low_mask = mask & (df['TOTAL_FGA'] < 100)
        df.loc[low_mask, 'TS_PCT'] = league_avg_ts
        print(f"  {season}: avg TS% = {league_avg_ts:.3f}, "
              f"replaced {low_mask.sum()} low-attempt players")
    else:
        print(f"  {season}: no reliable TS% found — skipping filter")

print(f"\nTS_PCT NaN count after fix: {df['TS_PCT'].isna().sum()}")

# ============================================================
# STEP 3 — THREE FRAMEWORK CORRELATION ANALYSIS
# ============================================================

print("\n" + "=" * 40)
print("STEP 3: Three-Framework Correlation Analysis")
print("=" * 40)

def safe_pearson(series_x, series_y):
    """Run pearsonr only if enough valid rows exist."""
    df_tmp = pd.DataFrame({'x': series_x, 'y': series_y}).dropna()
    if len(df_tmp) < 10:
        return None, None
    return pearsonr(df_tmp['x'], df_tmp['y'])

# Framework 1: Team-adjusted stats vs W_PCT
print("\nFramework 1: Team-adjusted stats vs W_PCT")
fw1_stats = ['OFF_RATING_ADJUSTED', 'DEF_RATING_ADJUSTED',
             'PIE_ADJUSTED', 'AST_PCT_ADJUSTED', 'DREB_PCT_ADJUSTED']
fw1_results = {}
for stat in fw1_stats:
    corr, pval = safe_pearson(df[stat], df['W_PCT'])
    if corr is not None:
        fw1_results[stat] = {'pearson': corr, 'pval': pval, 'significant': pval < 0.05}
        sig = "SIGNIFICANT" if pval < 0.05 else "not significant"
        print(f"  {stat}: r={corr:.3f}, p={pval:.4f} — {sig}")

# Framework 2: Individual stats vs W_PCT
print("\nFramework 2: Individual stats vs W_PCT")
fw2_stats = ['TS_PCT', 'STL', 'BLK', 'FG3_PCT', 'AST', 'REB', 'PTS']
fw2_results = {}
for stat in fw2_stats:
    if stat not in df.columns:
        print(f"  {stat}: column not found — skipping")
        continue
    corr, pval = safe_pearson(df[stat], df['W_PCT'])
    if corr is not None:
        fw2_results[stat] = {'pearson': corr, 'pval': pval, 'significant': pval < 0.05}
        sig = "SIGNIFICANT" if pval < 0.05 else "not significant"
        print(f"  {stat}: r={corr:.3f}, p={pval:.4f} — {sig}")
    else:
        print(f"  {stat}: insufficient data")

# Framework 3: Stats vs PLUS_MINUS_ADJUSTED
print("\nFramework 3: Stats vs PLUS_MINUS_ADJUSTED")
fw3_stats = ['OFF_RATING_ADJUSTED', 'DEF_RATING_ADJUSTED',
             'TS_PCT', 'PIE_ADJUSTED', 'AST_PCT_ADJUSTED',
             'DREB_PCT_ADJUSTED', 'STL', 'BLK', 'FG3_PCT']
fw3_results = {}
for stat in fw3_stats:
    if stat not in df.columns:
        continue
    corr, pval = safe_pearson(df[stat], df['PLUS_MINUS_ADJUSTED'])
    if corr is not None:
        fw3_results[stat] = {'pearson': corr, 'pval': pval, 'significant': pval < 0.05}
        sig = "SIGNIFICANT" if pval < 0.05 else "not significant"
        print(f"  {stat}: r={corr:.3f}, p={pval:.4f} — {sig}")

# ============================================================
# STEP 4 — SPEARMAN CORRELATION VALIDATION
# ============================================================

print("\n" + "=" * 40)
print("STEP 4: Spearman Correlation Validation")
print("=" * 40)

candidate_stats = ['OFF_RATING_ADJUSTED', 'DEF_RATING_ADJUSTED',
                   'TS_PCT', 'PIE_ADJUSTED', 'AST_PCT_ADJUSTED',
                   'DREB_PCT_ADJUSTED', 'STL', 'BLK', 'FG3_PCT']

spearman_results = {}
print("\nSpearman correlations with PLUS_MINUS_ADJUSTED:")
for stat in candidate_stats:
    if stat not in df.columns:
        continue
    tmp = df[[stat, 'PLUS_MINUS_ADJUSTED']].dropna()
    if len(tmp) < 10:
        continue
    corr, pval = spearmanr(tmp[stat], tmp['PLUS_MINUS_ADJUSTED'])
    spearman_results[stat] = {'spearman': corr, 'pval': pval, 'significant': pval < 0.05}
    sig = "SIGNIFICANT" if pval < 0.05 else "not significant"
    print(f"  {stat}: rho={corr:.3f}, p={pval:.4f} — {sig}")

# ============================================================
# STEP 5 — SELECT FINAL STATS FOR PCA
# ============================================================

print("\n" + "=" * 40)
print("STEP 5: Final Stat Selection for PCA")
print("=" * 40)

passed = set()
for stat, res in {**fw1_results, **fw2_results, **fw3_results}.items():
    if res['significant']:
        passed.add(stat)

spearman_passed = {s for s, r in spearman_results.items() if r['significant']}

# Include if significant in any framework AND validated by Spearman
final_stats = list(passed.intersection(spearman_passed))

# Always include OFF/DEF adjusted as anchor stats
for anchor in ['OFF_RATING_ADJUSTED', 'DEF_RATING_ADJUSTED']:
    if anchor not in final_stats:
        final_stats.append(anchor)

# Remove NET_RATING — it's derived from OFF + DEF (multicollinear)
final_stats = [s for s in final_stats if 'NET_RATING' not in s]

print(f"\nStats that passed at least one framework:  {sorted(passed)}")
print(f"Stats that passed Spearman:                {sorted(spearman_passed)}")
print(f"\nFINAL STATS GOING INTO PCA: {sorted(final_stats)}")

# ============================================================
# STEP 6 — INTERCORRELATION CHECK
# ============================================================

print("\n" + "=" * 40)
print("STEP 6: Intercorrelation Check")
print("=" * 40)

df_pca_input = df[final_stats + ['PLAYER_NAME', 'TEAM_ABBREVIATION',
                                  'SEASON', 'SALARY', 'W_PCT']].dropna()
print(f"Players with complete data for PCA: {len(df_pca_input)}")

intercorr = df_pca_input[final_stats].corr()
print("\nIntercorrelation matrix:")
print(intercorr.round(2))

print("\nRedundant pairs (|r| > 0.7):")
found_redundant = False
for i in range(len(final_stats)):
    for j in range(i + 1, len(final_stats)):
        val = intercorr.iloc[i, j]
        if abs(val) > 0.7:
            print(f"  {final_stats[i]} vs {final_stats[j]}: {val:.3f} — REDUNDANT")
            found_redundant = True
if not found_redundant:
    print("  None — all stats are sufficiently independent")

plt.figure(figsize=(10, 8))
sns.heatmap(intercorr, annot=True, fmt='.2f', cmap='coolwarm', center=0, square=True)
plt.title('Intercorrelation Matrix — Final PCA Stats', fontsize=13)
plt.tight_layout()
plt.savefig('intercorrelation_final.png')
plt.close()

# ============================================================
# STEP 7 — STANDARDIZE AND RUN PCA
# ============================================================

print("\n" + "=" * 40)
print("STEP 7: PCA — Deriving Composite Score Weights")
print("=" * 40)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_pca_input[final_stats])

pca = PCA()
pca.fit(X_scaled)

explained = pca.explained_variance_ratio_
print("\nVariance explained by each component:")
cumulative = 0
for i, var in enumerate(explained):
    cumulative += var
    print(f"  Component {i+1}: {var*100:.1f}%  (cumulative: {cumulative*100:.1f}%)")

weights_df = pd.DataFrame({
    'Stat': final_stats,
    'Weight': pca.components_[0]
}).sort_values('Weight', ascending=False)
print("\nPCA weights for Component 1:")
print(weights_df.to_string(index=False))

# ============================================================
# STEP 8 — COMPOSITE SCORE + VORPD
# ============================================================

print("\n" + "=" * 40)
print("STEP 8: Composite Score + VORPD")
print("=" * 40)

X_scored = pca.transform(X_scaled)
df_pca_input = df_pca_input.copy()
df_pca_input['COMPOSITE_SCORE'] = X_scored[:, 0]

score_min = df_pca_input['COMPOSITE_SCORE'].min()
score_max = df_pca_input['COMPOSITE_SCORE'].max()
df_pca_input['COMPOSITE_SCORE_NORM'] = (
    (df_pca_input['COMPOSITE_SCORE'] - score_min) /
    (score_max - score_min) * 100
).round(2)

replacement_level = df_pca_input['COMPOSITE_SCORE_NORM'].quantile(0.10)
print(f"Replacement level (10th percentile): {replacement_level:.2f}")

df_pca_input['VAR'] = (df_pca_input['COMPOSITE_SCORE_NORM'] - replacement_level).clip(lower=0)
df_pca_input['VORPD'] = (df_pca_input['VAR'] / (df_pca_input['SALARY'] / 1_000_000)).round(4)

# ============================================================
# STEP 9 — VALIDATION
# ============================================================

print("\n" + "=" * 40)
print("STEP 9: Real-World Validation")
print("=" * 40)

df_sorted = df_pca_input.sort_values('COMPOSITE_SCORE_NORM', ascending=False)

print("\nTop 20 players in 2023-24 by composite score:")
top_2324 = df_sorted[df_sorted['SEASON'] == '2023-24'][
    ['PLAYER_NAME', 'TEAM_ABBREVIATION', 'COMPOSITE_SCORE_NORM', 'SALARY', 'VORPD']
].head(20)
print(top_2324.to_string(index=False))

print("\nTop 10 best VALUE players in 2023-24 (highest VORPD):")
best_value = df_sorted[df_sorted['SEASON'] == '2023-24'].sort_values(
    'VORPD', ascending=False)[
    ['PLAYER_NAME', 'TEAM_ABBREVIATION', 'COMPOSITE_SCORE_NORM', 'SALARY', 'VORPD']
].head(10)
print(best_value.to_string(index=False))

# ============================================================
# STEP 10 — SAVE OUTPUTS AND CHARTS
# ============================================================

df_pca_input.to_csv('nba_scored_complete.csv', index=False)
print("\nSaved: nba_scored_complete.csv")

plt.figure(figsize=(10, 6))
colors = ['steelblue' if w > 0 else 'tomato' for w in weights_df['Weight']]
plt.bar(weights_df['Stat'], weights_df['Weight'], color=colors)
plt.title('PCA-Derived Weights Per Stat\n(No manual guessing — derived entirely from data)',
          fontsize=13)
plt.xticks(rotation=20, ha='right')
plt.tight_layout()
plt.savefig('pca_weights_final.png')
plt.close()

top20_plot = df_sorted[df_sorted['SEASON'] == '2023-24'].head(20).copy()
top20_plot['Label'] = top20_plot['PLAYER_NAME'] + ' (' + top20_plot['TEAM_ABBREVIATION'] + ')'
plt.figure(figsize=(12, 8))
plt.barh(top20_plot['Label'], top20_plot['COMPOSITE_SCORE_NORM'], color='steelblue')
plt.xlabel('Composite Score (0-100)')
plt.title('Top 20 Most Valuable NBA Players — 2023-24\n(PCA-Derived, Team-Context Adjusted)',
          fontsize=13)
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig('top20_players_final.png')
plt.close()

plt.figure(figsize=(8, 5))
plt.bar(range(1, len(explained) + 1), explained * 100, color='steelblue', alpha=0.7)
plt.plot(range(1, len(explained) + 1), np.cumsum(explained) * 100, 'ro-', label='Cumulative')
plt.xlabel('PCA Component')
plt.ylabel('Variance Explained (%)')
plt.title('PCA Variance Explained Per Component', fontsize=13)
plt.legend()
plt.tight_layout()
plt.savefig('pca_variance_explained.png')
plt.close()

print("\n" + "=" * 60)
print("FEATURE ENGINEERING COMPLETE")
print(f"Total players scored: {len(df_pca_input)}")
print(f"Stats used in PCA: {sorted(final_stats)}")
print(f"Component 1 explains: {explained[0]*100:.1f}% of variance")
print("=" * 60)
