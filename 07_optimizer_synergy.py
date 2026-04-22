import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import pandas as pd
import numpy as np
from pulp import *

print("=" * 60)
print("NBA ROSTER OPTIMIZER — SYNERGY MODEL")
print("=" * 60)
print()
print("Synergy layer (on top of individual composite scores):")
print("  1. Player-level NET_SYNERGY profile added to individual score")
print("  2. Pairwise W_NET_SYNERGY bonus — linearized y_ij = x_i * x_j")
print("     Validated: W_NET_SYNERGY r=+0.568 vs W_PCT (strongest signal)")
print("  3. Defensive coverage zone constraints (BLK, STL, switchability)")
print()
print("Methodology note:")
print("  NET_SYNERGY is used because it has the highest W_PCT correlation")
print("  across all 3 seasons — not to compensate for weak DEF_RATING.")
print("  Individual defensive limitations (DEF_RATING_ADJUSTED weight=0.039)")
print("  remain documented as a public data constraint. Advanced defensive")
print("  metrics (D-EPM, D-LEBRON) require proprietary tracking data.")
print()

# ============================================================
# LOAD ALL DATA
# ============================================================

df_2324     = pd.read_csv('nba_clustered.csv')
# --- FIX: Deduplicate scored data before optimizer sees it ---
# Duplicate player-season rows (NBA API artifact) caused the same player
# to be selected twice. Keep the higher-composite row per player.
df_2324 = (df_2324[df_2324['SEASON'] == '2023-24']
           .sort_values('COMPOSITE_SCORE_NORM', ascending=False)
           .drop_duplicates('PLAYER_NAME', keep='first')
           .copy()
           .reset_index(drop=True))

df_synergy  = pd.read_csv('nba_synergy_2324.csv')
df_profile  = pd.read_csv('nba_def_synergy_profile.csv')
df_arch_syn = pd.read_csv('nba_archetype_synergy.csv')
df_master   = pd.read_csv('nba_complete_master.csv')

# Get BLK and STL from master for 2023-24
df_master_2324 = (df_master[df_master['SEASON'] == '2023-24']
                  .sort_values('MIN', ascending=False)
                  .drop_duplicates('PLAYER_NAME')
                  [['PLAYER_NAME', 'PLAYER_ID', 'BLK', 'STL']])

# Merge PLAYER_ID and AGE from master (not in clustered)
df_2324 = df_2324.merge(df_master_2324[['PLAYER_NAME', 'PLAYER_ID']],
                        on='PLAYER_NAME', how='left')

# Get AGE from master for 2023-24
age_map = (df_master[df_master['SEASON'] == '2023-24']
           .sort_values('MIN', ascending=False)
           .drop_duplicates('PLAYER_NAME')
           [['PLAYER_NAME', 'AGE']])
df_2324 = df_2324.merge(age_map, on='PLAYER_NAME', how='left')

print(f"Players loaded: {len(df_2324)}")
print(f"Synergy pairs (2023-24): {len(df_synergy)}")
print(f"Player synergy profiles: {len(df_profile)}")

# ============================================================
# STEP 1 — PROFILE-ADJUSTED COMPOSITE SCORE
#
# Add each player's average defensive synergy profile to their
# composite score. This rewards defensive multipliers (OG Anunoby,
# Jonathan Isaac) and penalizes defensive liabilities (Queta, Pippen Jr.)
# at the INDIVIDUAL level — no linearization needed.
#
# PROFILE_WEIGHT = 0.4 means a player with avg NET_SYNERGY of +5
# gets +2.0 added to their composite score.
# ============================================================

PROFILE_WEIGHT = 0.4

df_2324 = df_2324.merge(
    df_profile[['PLAYER_NAME', 'NET_SYNERGY_PROFILE']],
    on='PLAYER_NAME', how='left'
)
df_2324['NET_SYNERGY_PROFILE'] = df_2324['NET_SYNERGY_PROFILE'].fillna(0.0)

df_2324['COMPOSITE_SYNERGY'] = (
    df_2324['COMPOSITE_SCORE_NORM'] +
    PROFILE_WEIGHT * df_2324['NET_SYNERGY_PROFILE']
).round(4)

# Show impact on key players
print("\nProfile adjustment impact (selected players):")
check_players = [
    'Victor Wembanyama', 'Nikola Jokić', 'OG Anunoby', 'Neemias Queta',
    'Dereck Lively II', 'Marcus Smart', 'Tari Eason', 'Jonathan Isaac',
    'Scotty Pippen Jr.', 'Shai Gilgeous-Alexander'
]
for name in check_players:
    row = df_2324[df_2324['PLAYER_NAME'].str.contains(name.split()[0], na=False)]
    if len(row) > 0:
        r = row.iloc[0]
        delta = r['COMPOSITE_SYNERGY'] - r['COMPOSITE_SCORE_NORM']
        sign = '+' if delta >= 0 else ''
        print(f"  {r['PLAYER_NAME']:<30} base={r['COMPOSITE_SCORE_NORM']:.2f}  "
              f"synergy_adj={r['COMPOSITE_SYNERGY']:.2f}  ({sign}{delta:.2f})")

# ============================================================
# STEP 2 — BUILD PAIRWISE SYNERGY LOOKUP
#
# For pairs with observed 2-man lineup data, compute y_ij bonus.
# Filter to pairs where both players are in optimizer pool
# and |W_NET_SYNERGY_SCALED| >= 1.0 (meaningful threshold).
# ============================================================

print("\n" + "=" * 40)
print("STEP 2: Pairwise Synergy Matrix")
print("=" * 40)

# Map player IDs to optimizer indices
id_to_idx = {}
for idx, row in df_2324.iterrows():
    pid = row.get('PLAYER_ID')
    if pd.notna(pid):
        id_to_idx[int(pid)] = idx

PAIR_MIN_SYNERGY = 1.0  # |W_NET_SYNERGY_SCALED| threshold

seen_pairs = set()
synergy_pairs = []
for _, row in df_synergy.iterrows():
    a_id = int(row['PLAYER_A_ID'])
    b_id = int(row['PLAYER_B_ID'])
    if a_id in id_to_idx and b_id in id_to_idx:
        syn_val = float(row['W_NET_SYNERGY_SCALED'])
        if abs(syn_val) >= PAIR_MIN_SYNERGY:
            ci = min(id_to_idx[a_id], id_to_idx[b_id])
            cj = max(id_to_idx[a_id], id_to_idx[b_id])
            if (ci, cj) not in seen_pairs:
                seen_pairs.add((ci, cj))
                synergy_pairs.append({
                    'i': ci,
                    'j': cj,
                    'name': row['GROUP_NAME'],
                    'NET_SYNERGY': syn_val,
                })

print(f"Synergy pairs after filter (|NET_SYN|>={PAIR_MIN_SYNERGY}): {len(synergy_pairs)}")
print(f"Positive pairs: {sum(1 for p in synergy_pairs if p['NET_SYNERGY'] > 0)}")
print(f"Negative pairs: {sum(1 for p in synergy_pairs if p['NET_SYNERGY'] < 0)}")

# ============================================================
# OPTIMIZER CONFIGURATION
# ============================================================

ROSTER_SIZE     = 15
SYNERGY_WEIGHT  = 0.5   # weight on pairwise synergy bonus vs individual score

BASE_ARCHETYPE_MINIMUMS = {
    'Elite Playmaker':    1,
    'Versatile Scorer':   2,
    'Defensive Wing':     1,
    'Perimeter Scorer':   2,
    'Two-Way Big':        2,
    'Bench / Role Player':1,
}

BIG_MAN_ARCHETYPES = ['Two-Way Big']

# Defensive coverage thresholds
BLK_PAINT_THRESHOLD = 1.5   # at least 1 player above this
STL_PERIMETER_THRESHOLD = 1.3  # at least 2 players above this
SWITCH_ARCHETYPES = ['Versatile Scorer', 'Defensive Wing', 'Two-Way Big']
MIN_SWITCHABLE = 4

SCENARIOS = {
    'A': {'name': 'A - Hard Cap ($136M)',       'cap': 136_021_000, 'objective': 'composite', 'variant': None},
    'B': {'name': 'B - Luxury Tax ($165M)',      'cap': 165_294_000, 'objective': 'composite', 'variant': None},
    'C': {'name': 'C - Budget Team ($90M)',      'cap':  90_000_000, 'objective': 'composite', 'variant': None},
    'D': {'name': 'D - Rebuild Mode ($136M)',    'cap': 136_021_000, 'objective': 'composite', 'variant': 'rebuild'},
    'E': {'name': 'E - Win-Now ($165M)',         'cap': 165_294_000, 'objective': 'composite', 'variant': 'win_now'},
    'F': {'name': 'F - Defensive Identity',      'cap': 136_021_000, 'objective': 'defense',   'variant': None},
    'G': {'name': 'G - Offensive Identity',      'cap': 136_021_000, 'objective': 'offense',   'variant': None},
    'H': {'name': 'H - Three-Point Era',         'cap': 136_021_000, 'objective': 'composite', 'variant': 'three_point'},
    'I': {'name': 'I - Small Ball',              'cap': 136_021_000, 'objective': 'composite', 'variant': 'small_ball'},
    'J': {'name': 'J - Value / Efficiency',      'cap': 136_021_000, 'objective': 'vorpd',     'variant': None},
}

league_avg_fg3 = df_2324['FG3_PCT'].mean()
print(f"\nLeague avg FG3%: {league_avg_fg3:.3f}")

all_results = {}

# ============================================================
# RUN ALL SCENARIOS
# ============================================================

for key, cfg in SCENARIOS.items():
    print(f"\n{'=' * 60}")
    print(f"SCENARIO {key} — {cfg['name']}")
    print(f"{'=' * 60}")

    CAP     = cfg['cap']
    variant = cfg['variant']
    obj     = cfg['objective']

    prob = LpProblem(f"NBA_Synergy_{key}", LpMaximize)

    # Binary decision variables: x[i] = 1 if player i is selected
    x = {i: LpVariable(f"x_{key}_{i}", cat='Binary') for i in df_2324.index}

    # --------------------------------------------------------
    # PAIRWISE SYNERGY VARIABLES (linearization of x_i * x_j)
    # y[i][j] = x[i] * x[j] — both on roster
    # Constraints: y <= x_i, y <= x_j, y >= x_i + x_j - 1
    # Use scenario key in variable/constraint names to avoid conflicts.
    # --------------------------------------------------------
    y = {}
    for pair in synergy_pairs:
        i, j = pair['i'], pair['j']
        if i not in y:
            y[i] = {}
        yij = LpVariable(f"y_{key}_{i}_{j}", cat='Binary')
        y[i][j] = yij
        prob += (yij <= x[i], f"syn_a_{key}_{i}_{j}")
        prob += (yij <= x[j], f"syn_b_{key}_{i}_{j}")
        prob += (yij >= x[i] + x[j] - 1, f"syn_c_{key}_{i}_{j}")

    # --------------------------------------------------------
    # OBJECTIVE FUNCTION
    # = individual synergy-adjusted score
    # + SYNERGY_WEIGHT * pairwise defensive synergy bonus
    # --------------------------------------------------------
    individual_term = lpSum(df_2324.loc[i, 'COMPOSITE_SYNERGY'] * x[i]
                            for i in df_2324.index)

    synergy_term = lpSum(
        pair['NET_SYNERGY'] * y[pair['i']].get(pair['j'], 0)
        for pair in synergy_pairs
        if pair['i'] in y and pair['j'] in y.get(pair['i'], {})
    )

    if obj == 'composite':
        prob += individual_term + SYNERGY_WEIGHT * synergy_term
    elif obj == 'defense':
        prob += lpSum(df_2324.loc[i, 'DEF_RATING_ADJUSTED'] * x[i]
                      for i in df_2324.index) + SYNERGY_WEIGHT * synergy_term
    elif obj == 'offense':
        prob += lpSum(df_2324.loc[i, 'OFF_RATING_ADJUSTED'] * x[i]
                      for i in df_2324.index)
    elif obj == 'vorpd':
        replacement = df_2324['COMPOSITE_SYNERGY'].quantile(0.10)
        prob += lpSum(
            ((df_2324.loc[i, 'COMPOSITE_SYNERGY'] - replacement) /
             (df_2324.loc[i, 'SALARY'] / 1_000_000)) * x[i]
            for i in df_2324.index
        )

    # --------------------------------------------------------
    # HARD CONSTRAINTS
    # --------------------------------------------------------

    # Roster size
    prob += (lpSum(x[i] for i in df_2324.index) == ROSTER_SIZE, "RosterSize")

    # Salary cap
    prob += (lpSum(df_2324.loc[i, 'SALARY'] * x[i]
                   for i in df_2324.index) <= CAP, "SalaryCap")

    # Max 2 players per team (diversity)
    for team in df_2324['TEAM_ABBREVIATION'].unique():
        team_idx = df_2324[df_2324['TEAM_ABBREVIATION'] == team].index.tolist()
        if team_idx:
            prob += (lpSum(x[i] for i in team_idx) <= 2, f"TeamLimit_{team}")

    # Archetype minimums
    archetype_mins = dict(BASE_ARCHETYPE_MINIMUMS)
    if variant == 'small_ball':
        archetype_mins.pop('Two-Way Big', None)

    for archetype, min_count in archetype_mins.items():
        arch_idx = df_2324[df_2324['ARCHETYPE'] == archetype].index.tolist()
        if arch_idx:
            prob += (lpSum(x[i] for i in arch_idx) >= min_count,
                     f"MinArchetype_{archetype.replace(' ','_').replace('/','')}")

    # Big man cap
    big_idx = df_2324[df_2324['ARCHETYPE'].isin(BIG_MAN_ARCHETYPES)].index.tolist()
    max_bigs = 1 if variant == 'small_ball' else 5
    prob += (lpSum(x[i] for i in big_idx) <= max_bigs, "MaxBigMen")

    # --------------------------------------------------------
    # DEFENSIVE COVERAGE ZONE CONSTRAINTS (NEW)
    # --------------------------------------------------------

    # 1. PAINT PROTECTION: at least 1 player with BLK >= 1.5
    paint_idx = df_2324[df_2324['BLK'] >= BLK_PAINT_THRESHOLD].index.tolist()
    if paint_idx:
        prob += (lpSum(x[i] for i in paint_idx) >= 1, "PaintProtector")
        print(f"  Paint blocker constraint: {len(paint_idx)} eligible")

    # 2. PERIMETER DISRUPTION: at least 2 players with STL >= 1.3
    perimeter_idx = df_2324[df_2324['STL'] >= STL_PERIMETER_THRESHOLD].index.tolist()
    if perimeter_idx:
        prob += (lpSum(x[i] for i in perimeter_idx) >= 2, "PerimeterDisruptors")
        print(f"  Perimeter disruptor constraint: {len(perimeter_idx)} eligible")

    # 3. SWITCHABILITY: at least 4 players from defensive archetypes
    switch_idx = df_2324[df_2324['ARCHETYPE'].isin(SWITCH_ARCHETYPES)].index.tolist()
    if switch_idx:
        prob += (lpSum(x[i] for i in switch_idx) >= MIN_SWITCHABLE, "Switchability")
        print(f"  Switchability constraint (>=4 defensive archetypes): {len(switch_idx)} eligible")

    # --------------------------------------------------------
    # SCENARIO-SPECIFIC VARIANT CONSTRAINTS
    # --------------------------------------------------------

    if variant == 'rebuild':
        young_idx = df_2324[df_2324['AGE'] <= 24].index.tolist()
        prob += (lpSum(x[i] for i in young_idx) >= 9, "MinYoungPlayers")
        print(f"  Rebuild: >=9 players age <=24 ({len(young_idx)} eligible)")

    elif variant == 'win_now':
        vet_idx = df_2324[df_2324['AGE'] >= 28].index.tolist()
        prob += (lpSum(x[i] for i in vet_idx) >= 9, "MinVeterans")
        print(f"  Win-Now: >=9 veterans age >=28 ({len(vet_idx)} eligible)")

    elif variant == 'three_point':
        # Use IS_SHOOTER flag (FG3A >= 0.5 per game, set before neutralization)
        # NOT FG3_PCT, which was neutralized to league avg for non-shooters.
        if 'IS_SHOOTER' in df_2324.columns:
            shooter_idx = df_2324[df_2324['IS_SHOOTER'] == 1].index.tolist()
            print(f"  Three-Point: >=10 real shooters (FG3A>=0.5/gm, {len(shooter_idx)} eligible)")
        else:
            shooter_idx = df_2324[df_2324['FG3_PCT'] >= league_avg_fg3].index.tolist()
            print(f"  Three-Point: >=10 shooters FG3%>={league_avg_fg3:.3f} ({len(shooter_idx)} eligible)")
        prob += (lpSum(x[i] for i in shooter_idx) >= 10, "MinThreePointShooters")

    # --------------------------------------------------------
    # SOLVE
    # --------------------------------------------------------

    prob.solve(PULP_CBC_CMD(msg=0))
    status = LpStatus[prob.status]
    print(f"\n  Solver: {status}")

    if status != 'Optimal':
        print(f"  WARNING: non-optimal solution for scenario {key}")
        continue

    selected = [i for i in df_2324.index if value(x[i]) > 0.5]
    roster = df_2324.loc[selected].copy()
    roster = roster.sort_values('COMPOSITE_SYNERGY', ascending=False)

    # Compute active pairwise synergy bonus
    active_syn = 0.0
    active_pairs = []
    for pair in synergy_pairs:
        i, j = pair['i'], pair['j']
        if i in selected and j in selected:
            active_syn += pair['NET_SYNERGY']
            active_pairs.append(pair['name'])

    total_salary  = roster['SALARY'].sum()
    total_score   = roster['COMPOSITE_SYNERGY'].sum()
    base_score    = roster['COMPOSITE_SCORE_NORM'].sum()
    avg_age       = roster['AGE'].mean()
    replacement   = df_2324['COMPOSITE_SYNERGY'].quantile(0.10)
    total_vorpd   = ((roster['COMPOSITE_SYNERGY'] - replacement).clip(lower=0) /
                     (roster['SALARY'] / 1_000_000)).sum()
    shooters_pct  = (roster['FG3_PCT'] >= league_avg_fg3).mean() * 100

    print(f"\n  {'PLAYER_NAME':<28} {'ARCHETYPE':<22} {'AGE':>3}  {'SCORE':>7}  {'NET_SYN':>7}  {'SALARY':>12}")
    print(f"  {'-'*90}")
    for _, r in roster.iterrows():
        print(f"  {r['PLAYER_NAME']:<28} {r['ARCHETYPE']:<22} {r['AGE']:>3.0f}  "
              f"{r['COMPOSITE_SYNERGY']:>7.2f}  {r['NET_SYNERGY_PROFILE']:>7.2f}  "
              f"${r['SALARY']:>11,.0f}")

    print(f"\n  --- SUMMARY ---")
    print(f"  Total salary:     ${total_salary:>14,.0f}  ({total_salary/CAP*100:.1f}% of cap)")
    print(f"  Cap:              ${CAP:>14,.0f}")
    print(f"  Base score:        {base_score:.2f}")
    print(f"  Synergy adj score: {total_score:.2f}  (+{total_score - base_score:.2f})")
    print(f"  Active pair syns:  {active_syn:.2f} pts/100 poss defensive gain from {len(active_pairs)} pairs")
    print(f"  Total VORPD:       {total_vorpd:.2f}")
    print(f"  Avg age:           {avg_age:.1f}")
    print(f"  3PT shooters:      {shooters_pct:.0f}%")

    arch_counts = roster['ARCHETYPE'].value_counts()
    print(f"\n  Archetypes: {dict(arch_counts)}")

    if active_pairs:
        print(f"\n  Active positive synergy pairs:")
        for pair in synergy_pairs:
            i, j = pair['i'], pair['j']
            if i in selected and j in selected and pair['NET_SYNERGY'] > 0:
                print(f"    {pair['name']:<40} NET_SYN={pair['NET_SYNERGY']:+.2f}")

    roster['SCENARIO'] = key
    roster.to_csv(f'optimized_roster_syn_{key}.csv', index=False)
    all_results[key] = {
        'name': cfg['name'],
        'cap':  CAP,
        'used_pct': total_salary / CAP * 100,
        'base_score': base_score,
        'syn_score': total_score,
        'pair_syn': active_syn,
        'vorpd': total_vorpd,
        'avg_age': avg_age,
    }

# ============================================================
# SCENARIO COMPARISON
# ============================================================

print(f"\n{'=' * 80}")
print("SCENARIO COMPARISON — SYNERGY OPTIMIZER")
print(f"{'=' * 80}")
print(f"\n{'Key':<4} {'Scenario':<35} {'Cap':>6}  {'Used%':>6}  "
      f"{'Base':>7}  {'SynAdj':>7}  {'PairSyn':>8}  {'Age':>5}  {'VORPD':>7}")
print("-" * 90)
for key, r in all_results.items():
    print(f"{key:<4} {r['name']:<35} "
          f"${r['cap']//1_000_000:>4}M  {r['used_pct']:>5.1f}%  "
          f"{r['base_score']:>7.2f}  {r['syn_score']:>7.2f}  "
          f"{r['pair_syn']:>+8.2f}  {r['avg_age']:>5.1f}  {r['vorpd']:>7.2f}")

print(f"\nAll synergy rosters saved: optimized_roster_syn_[A-J].csv")
print("\n" + "=" * 60)
print("SYNERGY OPTIMIZER COMPLETE")
print("=" * 60)
