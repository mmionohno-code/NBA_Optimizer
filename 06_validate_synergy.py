import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import pandas as pd
import numpy as np
from scipy.stats import pearsonr, spearmanr

print("=" * 60)
print("SYNERGY METRIC VALIDATION")
print("=" * 60)
print()
print("Question: Which synergy metric — DEF, OFF, or NET —")
print("has the strongest statistical correlation with W_PCT?")
print("This determines which should be used in the optimizer.")
print()

# ============================================================
# LOAD DATA
# ============================================================

df_lineups = pd.read_csv('nba_lineups_2man.csv')
df_master  = pd.read_csv('nba_complete_master.csv')

# Individual player baselines (OFF_RATING, DEF_RATING per season)
individual = (df_master[['PLAYER_ID','SEASON','PLAYER_NAME',
                          'TEAM_ABBREVIATION','OFF_RATING','DEF_RATING','W_PCT','MIN']]
              .sort_values('MIN', ascending=False)
              .drop_duplicates(['PLAYER_ID','SEASON'])
              .reset_index(drop=True))

# Team W_PCT per season
team_wpct = (df_master.groupby(['TEAM_ABBREVIATION','SEASON'])['W_PCT']
             .mean().reset_index())

# ============================================================
# STEP 1 — RECOMPUTE SYNERGY FOR ALL 3 SEASONS
# ============================================================

print("=" * 40)
print("STEP 1: Recomputing synergy for all seasons")
print("=" * 40)

df = df_lineups.copy()

df = df.merge(
    individual[['PLAYER_ID','SEASON','OFF_RATING','DEF_RATING']].rename(
        columns={'PLAYER_ID':'PLAYER_A_ID','OFF_RATING':'A_OFF','DEF_RATING':'A_DEF'}),
    on=['PLAYER_A_ID','SEASON'], how='left'
)
df = df.merge(
    individual[['PLAYER_ID','SEASON','OFF_RATING','DEF_RATING']].rename(
        columns={'PLAYER_ID':'PLAYER_B_ID','OFF_RATING':'B_OFF','DEF_RATING':'B_DEF'}),
    on=['PLAYER_B_ID','SEASON'], how='left'
)

df = df.dropna(subset=['A_DEF','B_DEF','A_OFF','B_OFF']).copy()

df['EXPECTED_DEF'] = (df['A_DEF'] + df['B_DEF']) / 2
df['EXPECTED_OFF'] = (df['A_OFF'] + df['B_OFF']) / 2

df['DEF_SYNERGY'] = df['EXPECTED_DEF'] - df['DEF_RATING']   # positive = better D
df['OFF_SYNERGY'] = df['OFF_RATING']  - df['EXPECTED_OFF']  # positive = better O
df['NET_SYNERGY'] = df['DEF_SYNERGY'] + df['OFF_SYNERGY']

df = df[df['MIN'] >= 100].copy()
print(f"Pairs with MIN>=100: {len(df)}")

# ============================================================
# STEP 2 — TEAM-LEVEL SYNERGY AGGREGATION
#
# For each team-season: compute the average DEF, OFF, NET synergy
# across their most-played 2-man pairs. This is the team's
# "synergy quality" which we then correlate with W_PCT.
# ============================================================

print("\n" + "=" * 40)
print("STEP 2: Team-level synergy aggregation")
print("=" * 40)

team_syn = (df.groupby(['TEAM_ABBREVIATION','SEASON'])
            .agg(
                AVG_DEF_SYNERGY = ('DEF_SYNERGY','mean'),
                AVG_OFF_SYNERGY = ('OFF_SYNERGY','mean'),
                AVG_NET_SYNERGY = ('NET_SYNERGY','mean'),
                TOTAL_PAIR_MIN  = ('MIN','sum'),
                N_PAIRS         = ('MIN','count'),
                # Weighted versions (weight by minutes together)
                W_DEF_SYNERGY   = ('DEF_SYNERGY', lambda x:
                    np.average(x, weights=df.loc[x.index,'MIN'])),
                W_OFF_SYNERGY   = ('OFF_SYNERGY', lambda x:
                    np.average(x, weights=df.loc[x.index,'MIN'])),
                W_NET_SYNERGY   = ('NET_SYNERGY', lambda x:
                    np.average(x, weights=df.loc[x.index,'MIN'])),
            )
            .reset_index())

team_syn = team_syn.merge(team_wpct, on=['TEAM_ABBREVIATION','SEASON'], how='left')
team_syn = team_syn.dropna(subset=['W_PCT'])

print(f"Team-seasons: {len(team_syn)}")
print(f"\nSample (2023-24, sorted by W_PCT):")
s = team_syn[team_syn['SEASON']=='2023-24'].sort_values('W_PCT', ascending=False)
print(s[['TEAM_ABBREVIATION','W_PCT','AVG_DEF_SYNERGY','AVG_OFF_SYNERGY',
         'AVG_NET_SYNERGY']].head(10).to_string(index=False))

# ============================================================
# STEP 3 — CORRELATION ANALYSIS
#
# Test all six metrics (unweighted + minutes-weighted)
# against W_PCT using both Pearson and Spearman.
# ============================================================

print("\n" + "=" * 40)
print("STEP 3: Correlation with W_PCT")
print("=" * 40)

metrics = {
    'AVG_DEF_SYNERGY (unweighted)': 'AVG_DEF_SYNERGY',
    'AVG_OFF_SYNERGY (unweighted)': 'AVG_OFF_SYNERGY',
    'AVG_NET_SYNERGY (unweighted)': 'AVG_NET_SYNERGY',
    'W_DEF_SYNERGY   (min-weighted)': 'W_DEF_SYNERGY',
    'W_OFF_SYNERGY   (min-weighted)': 'W_OFF_SYNERGY',
    'W_NET_SYNERGY   (min-weighted)': 'W_NET_SYNERGY',
}

results = {}
print(f"\n{'Metric':<40} {'Pearson r':>10} {'p-value':>10} {'Spearman':>10} {'Verdict'}")
print("-" * 80)

for label, col in metrics.items():
    tmp = team_syn[['W_PCT', col]].dropna()
    pr,  pp  = pearsonr( tmp[col], tmp['W_PCT'])
    sr,  sp  = spearmanr(tmp[col], tmp['W_PCT'])
    sig = "SIGNIFICANT" if pp < 0.05 else "not sig"
    print(f"{label:<40} {pr:>+10.4f} {pp:>10.4f} {sr:>+10.4f}  {sig}")
    results[label] = {'pearson': pr, 'pval': pp, 'spearman': sr, 'col': col}

# ============================================================
# STEP 4 — PER-SEASON BREAKDOWN
# Does the relationship hold in each season or just in aggregate?
# ============================================================

print("\n" + "=" * 40)
print("STEP 4: Per-season correlation stability")
print("=" * 40)

for season in sorted(team_syn['SEASON'].unique()):
    sub = team_syn[team_syn['SEASON'] == season]
    print(f"\n  {season}  (n={len(sub)} teams):")
    for label, col in metrics.items():
        tmp = sub[['W_PCT', col]].dropna()
        if len(tmp) < 5:
            continue
        pr, pp = pearsonr(tmp[col], tmp['W_PCT'])
        sig = '*' if pp < 0.05 else ' '
        print(f"    {label:<40} r={pr:>+.4f}  p={pp:.4f} {sig}")

# ============================================================
# STEP 5 — DEF vs OFF INTERCORRELATION
#
# Are DEF_SYNERGY and OFF_SYNERGY themselves correlated?
# If they're negatively correlated, using only one misses
# the trade-off between defensive and offensive pair chemistry.
# ============================================================

print("\n" + "=" * 40)
print("STEP 5: DEF vs OFF synergy intercorrelation")
print("=" * 40)

tmp = df[['DEF_SYNERGY','OFF_SYNERGY','NET_SYNERGY']].dropna()
print("\nPair-level intercorrelations:")
print(tmp.corr().round(4).to_string())

# Team-level
tmp_t = team_syn[['AVG_DEF_SYNERGY','AVG_OFF_SYNERGY','AVG_NET_SYNERGY']].dropna()
print("\nTeam-level intercorrelations:")
print(tmp_t.corr().round(4).to_string())

# ============================================================
# STEP 6 — WHICH METRIC IS STATISTICALLY BEST?
# ============================================================

print("\n" + "=" * 40)
print("STEP 6: Statistical Verdict")
print("=" * 40)

best_pearson  = max(results.items(), key=lambda x: abs(x[1]['pearson']))
best_spearman = max(results.items(), key=lambda x: abs(x[1]['spearman']))

print(f"\nHighest Pearson |r|:  {best_pearson[0]}")
print(f"  r = {best_pearson[1]['pearson']:+.4f}, p = {best_pearson[1]['pval']:.4f}")
print(f"\nHighest Spearman |r|: {best_spearman[0]}")
print(f"  r = {best_spearman[1]['spearman']:+.4f}")

# Compare DEF vs OFF vs NET directly
print("\nDirect comparison (unweighted):")
for key in ['AVG_DEF_SYNERGY (unweighted)',
            'AVG_OFF_SYNERGY (unweighted)',
            'AVG_NET_SYNERGY (unweighted)']:
    r = results[key]
    print(f"  {key}: pearson r = {r['pearson']:+.4f}, spearman = {r['spearman']:+.4f}")

print("\nConclusion:")
def_r   = abs(results['AVG_DEF_SYNERGY (unweighted)']['pearson'])
off_r   = abs(results['AVG_OFF_SYNERGY (unweighted)']['pearson'])
net_r   = abs(results['AVG_NET_SYNERGY (unweighted)']['pearson'])
best_r  = max(def_r, off_r, net_r)

if best_r == def_r:
    print("  DEF_SYNERGY has the strongest W_PCT correlation.")
    print("  Current optimizer choice is STATISTICALLY JUSTIFIED.")
elif best_r == off_r:
    print("  OFF_SYNERGY has the strongest W_PCT correlation.")
    print("  Optimizer should switch from DEF_SYNERGY to OFF_SYNERGY.")
else:
    print("  NET_SYNERGY has the strongest W_PCT correlation.")
    print("  Optimizer should use NET_SYNERGY (both ends equally important).")

print("\n" + "=" * 60)
print("VALIDATION COMPLETE")
print("=" * 60)
