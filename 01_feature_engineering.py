import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
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
# MERGE ON/OFF DIFFERENTIAL
# Computed from 5-man lineup data — captures gravity and
# real court impact beyond what box scores show
# ============================================================

df_onoff = pd.read_csv('nba_onoff.csv')[['PLAYER_ID', 'SEASON', 'ON_OFF_DIFF']]
df = df.merge(df_onoff, on=['PLAYER_ID', 'SEASON'], how='left')
matched = df['ON_OFF_DIFF'].notna().sum()
print(f"ON_OFF_DIFF merged: {matched} of {len(df)} player-seasons matched")
print(f"Unmatched (will be excluded from PCA): {len(df) - matched}")

# ============================================================
# STEP 1 — TEAM CONTEXT ADJUSTMENTS
# ============================================================

print("\n" + "=" * 40)
print("STEP 1: Team Context Adjustments")
print("=" * 40)

df = df.copy()

stats_to_adjust = ['OFF_RATING', 'DEF_RATING', 'NET_RATING',
                   'PIE', 'AST_PCT', 'OREB_PCT']

for stat in stats_to_adjust:
    if stat in df.columns:
        team_avg = df.groupby(['TEAM_ABBREVIATION', 'SEASON'])[stat].transform('mean')
        df[f'{stat}_ADJUSTED'] = df[stat] - team_avg
        print(f"  Adjusted: {stat}")

# DEF_RATING: lower is better for defense, so flip it
df['DEF_RATING_ADJUSTED'] = df['DEF_RATING_ADJUSTED'] * -1
print("  DEF_RATING_ADJUSTED flipped (higher = better defense)")

# DREB_PCT: use position-group adjustment instead of team adjustment.
# Team adjustment inflates centers on guard-heavy teams and deflates them
# on big-heavy teams — confounding height with skill. Instead, compare
# each player to position-group peers (guards, wings, bigs) per season.
# Position groups defined by DREB_PCT percentile cuts per season:
#   Guards  = bottom 33rd percentile  (DREB% ~3-8%)
#   Wings   = 33rd-66th percentile    (DREB% ~8-15%)
#   Bigs    = top 33rd percentile     (DREB% >15%)
def assign_pos_group(series):
    p33 = series.quantile(0.33)
    p66 = series.quantile(0.66)
    return pd.cut(series, bins=[-np.inf, p33, p66, np.inf],
                  labels=['Guard', 'Wing', 'Big'])

df['POS_GROUP'] = (df.groupby('SEASON')['DREB_PCT']
                     .transform(assign_pos_group))

pos_avg = df.groupby(['POS_GROUP', 'SEASON'])['DREB_PCT'].transform('mean')
df['DREB_PCT_ADJUSTED'] = df['DREB_PCT'] - pos_avg
print("  Adjusted: DREB_PCT (position-group peers, not team — removes positional height inflation)")
print(f"    Position group counts: {df['POS_GROUP'].value_counts().to_dict()}")

# Adjust PLUS_MINUS for team context (used in Framework 3)
pm_team_avg = df.groupby(['TEAM_ABBREVIATION', 'SEASON'])['PLUS_MINUS'].transform('mean')
df['PLUS_MINUS_ADJUSTED'] = df['PLUS_MINUS'] - pm_team_avg

# ============================================================
# STEP 2 — BAYESIAN TS_PCT SHRINKAGE
#
# PROBLEM IDENTIFIED: Hard cutoff (< 100 FGA → league avg) still
# allows low-volume players (3-5 FGA/game, all dunks) to carry
# artificially high TS% that inflates their composite score.
# Lively: 0.728 TS% on 3.2 FGA/game = 99th percentile TS%
# purely because he only takes layups — not a scoring skill signal.
#
# FIX: Bayesian shrinkage pulls every player's TS% toward the
# league mean proportionally to their shot volume.
# Formula: TS_ADJ = (FGA × TS + PRIOR × LEAGUE_AVG) / (FGA + PRIOR)
# where PRIOR = 150 shots (~2/game for a full season).
#
# Effect:
#   Player with 800 FGA: TS_ADJ ≈ actual TS%  (barely changes)
#   Player with 150 FGA: TS_ADJ = midpoint between TS% and league avg
#   Player with  30 FGA: TS_ADJ ≈ league avg  (highly uncertain)
# ============================================================

print("\n" + "=" * 40)
print("STEP 2: Bayesian TS_PCT Shrinkage (volume-weighted)")
print("=" * 40)

PRIOR_WEIGHT = 150   # equivalent shots of prior information

df['TOTAL_FGA'] = df['GP'] * df['FGA']

for season in df['SEASON'].unique():
    mask = df['SEASON'] == season
    reliable_mask = mask & (df['TOTAL_FGA'] >= 100)
    league_avg_ts = df.loc[reliable_mask, 'TS_PCT'].dropna().mean()

    if pd.isna(league_avg_ts):
        print(f"  {season}: no reliable TS% — skipping")
        continue

    # Apply Bayesian shrinkage to ALL players in this season
    total_fga = df.loc[mask, 'TOTAL_FGA'].fillna(0)
    raw_ts     = df.loc[mask, 'TS_PCT'].fillna(league_avg_ts)
    df.loc[mask, 'TS_PCT'] = (
        (total_fga * raw_ts + PRIOR_WEIGHT * league_avg_ts) /
        (total_fga + PRIOR_WEIGHT)
    )

    # Show impact on low-volume players
    low_mask = mask & (df['TOTAL_FGA'] < 200)
    avg_shrink = (df.loc[low_mask, 'TS_PCT'] - raw_ts[low_mask.loc[mask].values]).abs().mean()
    print(f"  {season}: league avg TS% = {league_avg_ts:.3f}  |  "
          f"low-vol players shrunk (n={low_mask.sum()}, avg shift = {avg_shrink:.3f})")

print(f"\nTS_PCT NaN count after Bayesian shrinkage: {df['TS_PCT'].isna().sum()}")

# ============================================================
# STEP 2A — FG3_PCT NON-SHOOTER NEUTRALIZATION
#
# PROBLEM IDENTIFIED: Centers with 0 three-point attempts are
# recorded as 0.000 FG3_PCT = 0th percentile.
# This penalizes rim-anchored bigs for correctly not shooting
# threes, which is their defined role in team construction.
# Gobert, Gafford, Poeltl, Lively all score 0th percentile
# for playing their position as designed.
#
# FIX: If a player takes fewer than 0.5 three-point attempts
# per game (FG3A < 0.5), replace FG3_PCT with the league
# average — same treatment as low-sample TS%.
# This encodes "no information about 3-point shooting"
# rather than "definitively a poor 3-point shooter."
# ============================================================

print("\n" + "=" * 40)
print("STEP 2A: FG3_PCT Non-Shooter Neutralization")
print("=" * 40)

# Flag real 3PT shooters BEFORE neutralization overwrites FG3_PCT
# Optimizer uses IS_SHOOTER (not FG3_PCT) to enforce shooter constraints.
df['IS_SHOOTER'] = (df['FG3A'] >= 0.5).astype(int)

for season in df['SEASON'].unique():
    mask = df['SEASON'] == season
    # Only neutralize if they essentially never attempt 3s
    non_shooter_mask = mask & (df['FG3A'] < 0.5)
    shooter_mask     = mask & (df['FG3A'] >= 0.5)

    if shooter_mask.sum() > 0:
        league_avg_fg3 = df.loc[shooter_mask, 'FG3_PCT'].dropna().mean()
        df.loc[non_shooter_mask, 'FG3_PCT'] = league_avg_fg3
        print(f"  {season}: neutralized {non_shooter_mask.sum()} non-shooters  "
              f"→ set to league avg FG3% = {league_avg_fg3:.3f}")

# ============================================================
# STEP 2B — W_PCT RESIDUALIZATION OF TEAM-CONTEXT STATS
#
# PROBLEM IDENTIFIED (audit findings):
#   W_PCT vs OFF_RATING_ADJUSTED: r = 0.181
#   W_PCT vs ON_OFF_DIFF:         r = 0.158
# Both team-context stats carry a team quality signal that
# inflates scores for players on good teams and deflates
# scores for players on bad teams — independent of their
# individual contribution.
#
# Mechanism 2 (star halo): KCP has OFF_RATING_ADJ = +7.85
#   because he plays with Jokic — not because he drives offense.
# Mechanism 6 (ON_OFF bias): Dante Exum ON_OFF = +12.49
#   because his ON minutes = when Luka plays.
# Mechanism 3 (bad team deflation): Wembanyama OFF_RATING = +0.09
#   because SAS is bad overall — he's not being credited.
#
# FIX: OLS residualization — regress each stat on W_PCT and
# use the residuals. This removes the shared variance between
# the stat and team quality, leaving only the player-specific
# contribution signal.
#
# Frisch-Waugh Theorem: the residual from regressing X on Z
# is the component of X orthogonal to Z — i.e., the part
# of X that CANNOT be explained by Z (team quality).
# After residualization, correlation with W_PCT → 0.
# ============================================================

print("\n" + "=" * 40)
print("STEP 2B: W_PCT Residualization of Team-Context Stats")
print("=" * 40)

from numpy.linalg import lstsq

def residualize_on_wpt(series_stat, series_wpt):
    """Remove W_PCT signal from a stat via OLS residualization."""
    tmp = pd.DataFrame({'stat': series_stat, 'wpt': series_wpt}).dropna()
    if len(tmp) < 10:
        return series_stat  # not enough data — leave unchanged
    X = np.column_stack([np.ones(len(tmp)), tmp['wpt'].values])
    y = tmp['stat'].values
    beta, _, _, _ = lstsq(X, y, rcond=None)
    residuals = y - X @ beta
    result = series_stat.copy()
    result.loc[tmp.index] = residuals
    return result

# OFF_RATING_ADJUSTED: already has team-average subtracted (team avg removed in STEP 1)
# Residualizing it further removes too much signal from legitimate stars on good teams
# (Tatum and AD both dropped significantly — incorrect overcorrection)
#
# ON_OFF_DIFF: confirmed star proximity bias from audit — Exum +12.49 (Luka effect),
# KCP +15.63 (Jokic effect), Tre Jones +11.88 (Wemby effect) — residualize ONLY this
for stat in ['ON_OFF_DIFF']:
    if stat not in df.columns:
        continue
    original = df[stat].copy()
    df[stat] = residualize_on_wpt(df[stat], df['W_PCT'])

    # Verify correlation is near zero after
    tmp = pd.DataFrame({'stat': df[stat], 'wpt': df['W_PCT']}).dropna()
    from scipy.stats import pearsonr as pr
    r_after, _ = pr(tmp['stat'], tmp['wpt'])
    print(f"  {stat}: r(W_PCT) before residualization → after = {r_after:.4f}  (target: ~0)")

print("\nResiduals interpretation:")
print("  Positive = player outperforms what their team quality predicts")
print("  Negative = player underperforms what their team quality predicts")
print("  Wembanyama: ON_OFF_DIFF residual RISES (good player on bad team)")
print("  KCP/Exum:   ON_OFF_DIFF residual FALLS (role player on great team)")

# ============================================================
# INFLUENCE SCORE = USG_PCT x TS_PCT
# Measures how much productive offensive work a player is
# responsible for. High usage alone is not enough — the player
# must also convert efficiently (Curry vs LaMelo distinction).
# ============================================================

df['INFLUENCE_SCORE'] = df['USG_PCT'] * df['TS_PCT']
print(f"\nINFLUENCE_SCORE created (USG_PCT x TS_PCT)")
print(f"  Range: {df['INFLUENCE_SCORE'].min():.4f} - {df['INFLUENCE_SCORE'].max():.4f}")
print(f"  Mean:  {df['INFLUENCE_SCORE'].mean():.4f}")

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
fw2_stats = ['TS_PCT', 'STL', 'BLK', 'FG3_PCT', 'AST', 'REB', 'PTS', 'INFLUENCE_SCORE', 'ON_OFF_DIFF']
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
             'DREB_PCT_ADJUSTED', 'STL', 'BLK', 'FG3_PCT', 'INFLUENCE_SCORE', 'ON_OFF_DIFF']
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
                   'DREB_PCT_ADJUSTED', 'STL', 'BLK', 'FG3_PCT', 'INFLUENCE_SCORE', 'ON_OFF_DIFF']

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

# Remove PIE_ADJUSTED if INFLUENCE_SCORE is present — they correlate at 0.78
# INFLUENCE_SCORE (USG% x TS%) is more interpretable and analytically defensible
# PIE is partially derived from USG%, so the overlap is genuine double-counting
if 'INFLUENCE_SCORE' in final_stats and 'PIE_ADJUSTED' in final_stats:
    final_stats = [s for s in final_stats if s != 'PIE_ADJUSTED']
    print("  Removed PIE_ADJUSTED (r=0.78 with INFLUENCE_SCORE — redundant)")

print(f"\nStats that passed at least one framework:  {sorted(passed)}")
print(f"Stats that passed Spearman:                {sorted(spearman_passed)}")
print(f"\nFINAL STATS GOING INTO PCA: {sorted(final_stats)}")

# ============================================================
# STEP 6 — INTERCORRELATION CHECK
# ============================================================

print("\n" + "=" * 40)
print("STEP 6: Intercorrelation Check")
print("=" * 40)

# --- FIX: deduplicate before PCA ---
# Some players appear 2-3x with identical stats (NBA API download artifact).
# Keep highest-GP row per player-season to avoid inflating their PCA influence.
df_deduped = df.sort_values('GP', ascending=False).drop_duplicates(
    subset=['PLAYER_ID', 'SEASON'], keep='first')
n_removed = len(df) - len(df_deduped)
if n_removed:
    print(f"  Deduplication: removed {n_removed} duplicate player-season rows")

df_pca_input = df_deduped[final_stats + ['PLAYER_NAME', 'PLAYER_ID', 'TEAM_ABBREVIATION',
                                          'SEASON', 'SALARY', 'W_PCT',
                                          'SEASON_WEIGHT', 'IS_SHOOTER']].dropna(
    subset=final_stats)
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
plt.savefig('charts/intercorrelation_final.png')
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
# Multi-component weighted PCA scoring:
#   PC1..PC3 each scored, then weighted by their share of
#   variance explained (PC1: ~47%, PC2: ~29%, PC3: ~24%).
#   This addresses the 30.5% variance problem from PC1-only.
# ============================================================

print("\n" + "=" * 40)
print("STEP 8: Composite Score + VORPD (Multi-Component PCA)")
print("=" * 40)

X_scored = pca.transform(X_scaled)
df_pca_input = df_pca_input.copy()

# Use top 3 components; weight each by |correlation with PLUS_MINUS_ADJUSTED|
n_components_use = min(3, X_scored.shape[1])
pc_cols = [f'PC{i+1}' for i in range(n_components_use)]
for i in range(n_components_use):
    df_pca_input[pc_cols[i]] = X_scored[:, i]

# Weight each PC by its share of variance explained among the top 3.
# Variance-explained weighting is principled: PC1 captures the dominant
# basketball excellence dimension (ON_OFF_DIFF, OFF_RATING, INFLUENCE_SCORE)
# and deserves the most influence. PC2/PC3 add independent information
# without overriding PC1's signal.
var_weights_raw = explained[:n_components_use]
total_var = var_weights_raw.sum()
pc_weights = [v / total_var for v in var_weights_raw]

print(f"\nMulti-component PC weights (by variance explained share):")
for col, w in zip(pc_cols, pc_weights):
    print(f"  {col}: {w:.3f}")

# Weighted composite
df_pca_input['COMPOSITE_SCORE'] = sum(
    w * df_pca_input[col] for w, col in zip(pc_weights, pc_cols)
)

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
plt.savefig('charts/pca_weights_final.png')
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
plt.savefig('charts/top20_players_final.png')
plt.close()

plt.figure(figsize=(8, 5))
plt.bar(range(1, len(explained) + 1), explained * 100, color='steelblue', alpha=0.7)
plt.plot(range(1, len(explained) + 1), np.cumsum(explained) * 100, 'ro-', label='Cumulative')
plt.xlabel('PCA Component')
plt.ylabel('Variance Explained (%)')
plt.title('PCA Variance Explained Per Component', fontsize=13)
plt.legend()
plt.tight_layout()
plt.savefig('charts/pca_variance_explained.png')
plt.close()

print("\n" + "=" * 60)
print("FEATURE ENGINEERING COMPLETE")
print(f"Total players scored: {len(df_pca_input)}")
print(f"Stats used in PCA: {sorted(final_stats)}")
print(f"PC1 explains: {explained[0]*100:.1f}%  |  PC1+PC2+PC3: {sum(explained[:3])*100:.1f}% of variance")
print(f"PC weights used: {[round(w,3) for w in pc_weights]}")
print("=" * 60)
