import sys; sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import pandas as pd, numpy as np

df = pd.read_csv('nba_complete_master.csv')
df = df.sort_values('GP', ascending=False).drop_duplicates(['PLAYER_ID', 'SEASON'])

PAIRS = [('2021-22', '2022-23'), ('2022-23', '2023-24')]

def build(stat, n_func, shooter_filter=None):
    rows = []
    for s_tr, s_te in PAIRS:
        a = df[df['SEASON'] == s_tr].set_index('PLAYER_ID')
        b = df[df['SEASON'] == s_te].set_index('PLAYER_ID')
        for pid in a.index.intersection(b.index):
            ra, rb = a.loc[pid], b.loc[pid]
            n_tr, n_te = n_func(ra), n_func(rb)
            rt, te = ra[stat], rb[stat]
            if any(pd.isna(v) for v in (n_tr, n_te, rt, te)):
                continue
            if shooter_filter and not (shooter_filter(ra) and shooter_filter(rb)):
                continue
            rows.append((s_tr, n_tr, rt, n_te, te))
    return pd.DataFrame(rows, columns=['season', 'n_tr', 'raw_tr', 'n_te', 'raw_te'])

def optimal_k(p, mu_by_season, kgrid):
    mu = p['season'].map(mu_by_season).values
    n_tr, raw_tr, raw_te, w = (p['n_tr'].values, p['raw_tr'].values,
                               p['raw_te'].values, p['n_te'].values)
    res = []
    for K in kgrid:
        shrunk = (n_tr * raw_tr + K * mu) / (n_tr + K)
        mse = np.average((shrunk - raw_te) ** 2, weights=w)
        res.append((K, mse))
    res = np.array(res)
    kstar = res[res[:, 1].argmin(), 0]
    # baseline MSE at K=0 (no shrinkage) for context
    mse0 = res[0, 1]
    mse_star = res[:, 1].min()
    return kstar, mse0, mse_star, res

def season_mean(mask_func, col):
    out = {}
    for s in df['SEASON'].unique():
        sub = df[(df['SEASON'] == s) & df.apply(mask_func, axis=1)]
        out[s] = sub[col].mean()
    return out

print("=" * 64)
print("EMPIRICAL PRIOR (K) DERIVATION VIA SEASON-TO-SEASON MSE")
print("=" * 64)

# ---- TS% (validate method should land near your known 275) ----
ts_mu = season_mean(lambda r: r['GP'] * r['FGA'] >= 100, 'TS_PCT')
p_ts = build('TS_PCT', lambda r: r['GP'] * r['FGA'])
k_ts, m0, ms, _ = optimal_k(p_ts, ts_mu, range(0, 805, 5))
print(f"\nTS%   (counter = total FGA, mu = reliable league mean)")
print(f"  pairs used: {len(p_ts)}")
print(f"  optimal K* = {k_ts:.0f} FGA   | MSE no-shrink={m0:.5f} -> best={ms:.5f}")
print(f"  (your pipeline currently uses PRIOR_WEIGHT = 275)")

# ---- FG3% (you set 82 via NBA qualification; what does MSE say?) ----
fg3_mu = season_mean(lambda r: r['FG3A'] >= 0.5, 'FG3_PCT')
p_fg3 = build('FG3_PCT', lambda r: r['GP'] * r['FG3A'],
              shooter_filter=lambda r: r['FG3A'] >= 0.5)
k_fg3, m0, ms, _ = optimal_k(p_fg3, fg3_mu, range(0, 805, 5))
print(f"\nFG3%  (counter = total 3PA, mu = shooter league mean)")
print(f"  pairs used: {len(p_fg3)}")
print(f"  optimal K* = {k_fg3:.0f} 3PA   | MSE no-shrink={m0:.5f} -> best={ms:.5f}")
print(f"  (your pipeline currently uses PRIOR_3PA = 82, NBA qualification standard)")

# ---- The four minute-based adjusted stats (mu = 0) ----
zero_mu = {s: 0.0 for s in df['SEASON'].unique()}
print(f"\nMINUTE-WEIGHTED STATS (counter = total minutes GP*MIN, mu = 0)")
for stat in ['OFF_RATING', 'DEF_RATING', 'AST_PCT']:
    if stat not in df.columns:
        print(f"  {stat}: not in master (adjusted version built in pipeline) — skipping")
        continue
    p = build(stat, lambda r: r['GP'] * r['MIN'])
    # center each season to mimic the *_ADJUSTED form (subtract season mean)
    smean = p.groupby('season')['raw_tr'].transform('mean')
    p['raw_tr'] = p['raw_tr'] - smean
    smean_te = p.groupby('season')['raw_te'].transform('mean')
    p['raw_te'] = p['raw_te'] - smean_te
    k, m0, ms, _ = optimal_k(p, zero_mu, range(0, 4050, 50))
    print(f"  {stat:<12} optimal K* = {k:>5.0f} min (~{k/30:.0f} games) | "
          f"pairs={len(p)} | MSE {m0:.3f}->{ms:.3f}")

# ON_OFF_DIFF lives in nba_onoff.csv, one value per player-season
try:
    onoff = pd.read_csv('nba_onoff.csv')[['PLAYER_ID', 'SEASON', 'ON_OFF_DIFF']]
    minutes = df[['PLAYER_ID', 'SEASON', 'GP', 'MIN']]
    oo = onoff.merge(minutes, on=['PLAYER_ID', 'SEASON'], how='inner')
    oo = oo.sort_values('GP', ascending=False).drop_duplicates(['PLAYER_ID', 'SEASON'])
    rows = []
    for s_tr, s_te in PAIRS:
        a = oo[oo['SEASON'] == s_tr].set_index('PLAYER_ID')
        b = oo[oo['SEASON'] == s_te].set_index('PLAYER_ID')
        for pid in a.index.intersection(b.index):
            ra, rb = a.loc[pid], b.loc[pid]
            rows.append((s_tr, ra['GP'] * ra['MIN'], ra['ON_OFF_DIFF'],
                         rb['GP'] * rb['MIN'], rb['ON_OFF_DIFF']))
    p = pd.DataFrame(rows, columns=['season', 'n_tr', 'raw_tr', 'n_te', 'raw_te']).dropna()
    k, m0, ms, _ = optimal_k(p, zero_mu, range(0, 6050, 50))
    print(f"  {'ON_OFF_DIFF':<12} optimal K* = {k:>5.0f} min (~{k/30:.0f} games) | "
          f"pairs={len(p)} | MSE {m0:.3f}->{ms:.3f}")
except Exception as e:
    print(f"  ON_OFF_DIFF: {e}")

print("\n" + "=" * 64)
print("Current judgment pick KAPPA_MIN = 500 total minutes (~17 games).")
print("Compare to the K* values above to see if 500 is well-calibrated.")
print("=" * 64)
