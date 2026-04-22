import sys
import pandas as pd
import numpy as np
from pulp import LpProblem, LpMaximize, LpVariable, LpStatus, lpSum, value, PULP_CBC_CMD

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

print("=" * 60)
print("NBA ROSTER OPTIMIZER - EXPANDED (10 SCENARIOS)")
print("=" * 60)

# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv('nba_clustered.csv')

# AGE was not carried into clustered file - merge it back in
df_age = (pd.read_csv('nba_master_threeyears.csv')
          [['PLAYER_NAME', 'SEASON', 'AGE']]
          .drop_duplicates(subset=['PLAYER_NAME', 'SEASON']))

df = df.merge(df_age, on=['PLAYER_NAME', 'SEASON'], how='left')

df_2324 = (df[df['SEASON'] == '2023-24']
           .sort_values('COMPOSITE_SCORE_NORM', ascending=False)
           .drop_duplicates('PLAYER_NAME', keep='first')
           .copy()
           .reset_index(drop=True))
N = len(df_2324)

print(f"\nPlayers available for selection: {N}")
print(f"Archetypes: {sorted(df_2324['ARCHETYPE'].unique())}")
print(f"Salary range: ${df_2324['SALARY'].min():,.0f} - ${df_2324['SALARY'].max():,.0f}")
print(f"Age range:    {df_2324['AGE'].min():.0f} - {df_2324['AGE'].max():.0f}  (avg {df_2324['AGE'].mean():.1f})")
print(f"Players age <= 24: {(df_2324['AGE'] <= 24).sum()}")
print(f"Players age >= 28: {(df_2324['AGE'] >= 28).sum()}")

# VORPD - fill NaN and clip negatives to 0
df_2324['VORPD'] = df_2324['VORPD'].fillna(0).clip(lower=0)

# League-average FG3% - used as threshold for three-point era constraint
league_avg_fg3 = df_2324['FG3_PCT'].mean()
print(f"League avg FG3%: {league_avg_fg3:.3f}")

TEAMS = df_2324['TEAM_ABBREVIATION'].unique()

# ============================================================
# SHARED CONSTRAINT DEFINITIONS
# These apply to every scenario unless explicitly overridden
# ============================================================

BASE_ARCHETYPE_MINIMUMS = {
    'Elite Playmaker':    1,   # must have at least one franchise cornerstone
    'Versatile Scorer':   2,   # guards/wings who defend and create
    'Defensive Wing':     1,   # defensive wing for perimeter coverage
    'Perimeter Scorer':   2,   # outside scoring and spacing
    'Two-Way Big':        2,   # versatile bigs (covers rim protectors + stretch bigs)
    'Bench / Role Player':1,   # bench depth
}

BIG_MAN_ARCHETYPES = ['Two-Way Big']

# ============================================================
# SCENARIO DEFINITIONS
#
# Each scenario is defined by:
#   cap       - salary ceiling (hard constraint)
#   objective - what we maximize:
#               'composite' = total COMPOSITE_SCORE_NORM
#               'defense'   = total (-DEF_RATING_ADJUSTED)
#               'offense'   = total OFF_RATING_ADJUSTED
#               'vorpd'     = total VORPD
#   variant   - extra constraint block to apply on top of base
#               None, 'rebuild', 'win_now', 'three_point', 'small_ball'
# ============================================================

SCENARIOS = {
    'A': {
        'name':      'A - Hard Cap ($136M)',
        'cap':        136_021_000,
        'objective': 'composite',
        'variant':    None,
        'note':       'Standard hard cap. Baseline roster.'
    },
    'B': {
        'name':      'B - Luxury Tax ($165M)',
        'cap':        165_294_000,
        'objective': 'composite',
        'variant':    None,
        'note':       'Deep-pocketed owner paying luxury tax. Best composite score money can buy.'
    },
    'C': {
        'name':      'C - Budget Team ($90M)',
        'cap':         90_000_000,
        'objective': 'composite',
        'variant':    None,
        'note':       'Small-market budget team. Maximize score under severe constraint.'
    },
    'D': {
        'name':      'D - Rebuild Mode ($136M)',
        'cap':        136_021_000,
        'objective': 'composite',
        'variant':   'rebuild',
        'note':       'Tanking / rebuild team. Hard cap + must include >=9 players age <= 24.'
    },
    'E': {
        'name':      'E - Win-Now ($165M)',
        'cap':        165_294_000,
        'objective': 'composite',
        'variant':   'win_now',
        'note':       'Championship window. Luxury cap + must include >=9 veterans age >= 28.'
    },
    'F': {
        'name':      'F - Defensive Identity ($136M)',
        'cap':        136_021_000,
        'objective': 'defense',
        'variant':    None,
        'note':       'Build around defense. Maximize sum of -DEF_RATING_ADJUSTED (lower = better defender).'
    },
    'G': {
        'name':      'G - Offensive Identity ($136M)',
        'cap':        136_021_000,
        'objective': 'offense',
        'variant':    None,
        'note':       'Build around offense. Maximize sum of OFF_RATING_ADJUSTED.'
    },
    'H': {
        'name':      'H - Three-Point Era ($136M)',
        'cap':        136_021_000,
        'objective': 'composite',
        'variant':   'three_point',
        'note':       'Modern spacing team. Hard cap + >=10 players shoot above league-avg FG3%.'
    },
    'I': {
        'name':      'I - Small Ball ($136M)',
        'cap':        136_021_000,
        'objective': 'composite',
        'variant':   'small_ball',
        'note':       'No traditional bigs. Hard cap + max 1 Two-Way Big on roster.'
    },
    'J': {
        'name':      'J - Value / Efficiency ($136M)',
        'cap':        136_021_000,
        'objective': 'vorpd',
        'variant':    None,
        'note':       'Moneyball approach. Hard cap but maximize VORPD (value per salary dollar).'
    },
}

all_results = {}

# ============================================================
# RUN ALL SCENARIOS
# ============================================================

for key, cfg in SCENARIOS.items():

    scenario_name = cfg['name']
    salary_cap    = cfg['cap']
    objective     = cfg['objective']
    variant       = cfg['variant']

    print(f"\n{'=' * 60}")
    print(f"SCENARIO {scenario_name}")
    print(f"Cap: ${salary_cap:,}  |  Objective: {objective}  |  Variant: {variant or 'standard'}")
    print(f"Note: {cfg['note']}")
    print("=" * 60)

    prob = LpProblem(f"NBA_Roster_{key}", LpMaximize)
    x = [LpVariable(f"x_{key}_{i}", cat='Binary') for i in range(N)]

    # ----------------------------------------------------------
    # OBJECTIVE FUNCTION
    # ----------------------------------------------------------

    if objective == 'composite':
        # Standard: maximize total composite score
        prob += lpSum(df_2324.loc[i, 'COMPOSITE_SCORE_NORM'] * x[i] for i in range(N))

    elif objective == 'defense':
        # DEF_RATING_ADJUSTED: LOWER = better defender
        # Maximizing the negative is equivalent to minimizing it
        prob += lpSum(-df_2324.loc[i, 'DEF_RATING_ADJUSTED'] * x[i] for i in range(N))

    elif objective == 'offense':
        # OFF_RATING_ADJUSTED: HIGHER = better offensive player
        prob += lpSum(df_2324.loc[i, 'OFF_RATING_ADJUSTED'] * x[i] for i in range(N))

    elif objective == 'vorpd':
        # VORPD: Value Over Replacement Per Dollar
        # Higher = more value per dollar of salary
        prob += lpSum(df_2324.loc[i, 'VORPD'] * x[i] for i in range(N))

    # ----------------------------------------------------------
    # CONSTRAINT 1 - Salary Cap
    # ----------------------------------------------------------

    prob += (
        lpSum(df_2324.loc[i, 'SALARY'] * x[i] for i in range(N)) <= salary_cap,
        "SalaryCap"
    )

    # ----------------------------------------------------------
    # CONSTRAINT 2 - Roster Size
    # ----------------------------------------------------------

    prob += (lpSum(x[i] for i in range(N)) == 15, "RosterSize")

    # ----------------------------------------------------------
    # CONSTRAINT 3 - Archetype Coverage
    # Small ball removes big man minimums (they're not required)
    # ----------------------------------------------------------

    archetype_mins = BASE_ARCHETYPE_MINIMUMS.copy()

    if variant == 'small_ball':
        archetype_mins.pop('Two-Way Big', None)

    for archetype, min_count in archetype_mins.items():
        indices = df_2324[df_2324['ARCHETYPE'] == archetype].index.tolist()
        if indices:
            prob += (
                lpSum(x[i] for i in indices) >= min_count,
                f"Min_{archetype.replace(' ', '_').replace('/', '_')}"
            )

    # ----------------------------------------------------------
    # CONSTRAINT 4 - Big Man Cap
    # Small ball: max 3 total | All others: max 7 total
    # ----------------------------------------------------------

    big_indices = df_2324[df_2324['ARCHETYPE'].isin(BIG_MAN_ARCHETYPES)].index.tolist()
    max_bigs = 1 if variant == 'small_ball' else 5
    prob += (lpSum(x[i] for i in big_indices) <= max_bigs, "MaxBigMen")

    # ----------------------------------------------------------
    # CONSTRAINT 5 - Team Diversity (max 2 from same team)
    # ----------------------------------------------------------

    for team in TEAMS:
        indices = df_2324[df_2324['TEAM_ABBREVIATION'] == team].index.tolist()
        if len(indices) > 2:
            prob += (lpSum(x[i] for i in indices) <= 2, f"MaxTwo_{team}")

    # ----------------------------------------------------------
    # VARIANT-SPECIFIC CONSTRAINTS
    # ----------------------------------------------------------

    if variant == 'rebuild':
        # Must have at least 9 players age 24 or younger — forces true youth movement
        young_indices = df_2324[df_2324['AGE'] <= 24].index.tolist()
        prob += (lpSum(x[i] for i in young_indices) >= 9, "MinYoungPlayers")
        print(f"  Rebuild constraint: >=9 players age <= 24  ({len(young_indices)} eligible)")

    elif variant == 'win_now':
        # Must have at least 9 veterans age 28 or older — forces proven-vet majority
        vet_indices = df_2324[df_2324['AGE'] >= 28].index.tolist()
        prob += (lpSum(x[i] for i in vet_indices) >= 9, "MinVeterans")
        print(f"  Win-now constraint: >=9 players age >= 28  ({len(vet_indices)} eligible)")

    elif variant == 'three_point':
        # Use IS_SHOOTER flag (FG3A >= 0.5 per game, set before neutralization)
        # NOT FG3_PCT, which was neutralized to league avg for non-shooters.
        if 'IS_SHOOTER' in df_2324.columns:
            shooter_indices = df_2324[df_2324['IS_SHOOTER'] == 1].index.tolist()
            print(f"  Three-point constraint: >=10 real shooters (FG3A>=0.5/gm, {len(shooter_indices)} eligible)")
        else:
            shooter_indices = df_2324[df_2324['FG3_PCT'] >= league_avg_fg3].index.tolist()
            print(f"  Three-point constraint: >=10 players FG3% >= {league_avg_fg3:.3f}  ({len(shooter_indices)} eligible)")
        prob += (lpSum(x[i] for i in shooter_indices) >= 10, "MinThreePointShooters")

    # ----------------------------------------------------------
    # SOLVE
    # ----------------------------------------------------------

    prob.solve(PULP_CBC_CMD(msg=0))
    status = LpStatus[prob.status]
    print(f"\nSolver status: {status}")

    if status != 'Optimal':
        print("WARNING: Solver did not find an optimal solution.")
        print("Try relaxing constraints or increasing cap.")
        continue

    # ----------------------------------------------------------
    # EXTRACT RESULTS
    # ----------------------------------------------------------

    selected_idx = [i for i in range(N) if value(x[i]) and value(x[i]) > 0.5]
    roster = df_2324.loc[selected_idx, [
        'PLAYER_NAME', 'TEAM_ABBREVIATION', 'ARCHETYPE',
        'COMPOSITE_SCORE_NORM', 'SALARY', 'VORPD', 'AGE',
        'DEF_RATING_ADJUSTED', 'OFF_RATING_ADJUSTED', 'FG3_PCT'
    ]].copy()

    roster = roster.sort_values('COMPOSITE_SCORE_NORM', ascending=False)

    total_salary  = roster['SALARY'].sum()
    total_score   = roster['COMPOSITE_SCORE_NORM'].sum()
    avg_score     = roster['COMPOSITE_SCORE_NORM'].mean()
    cap_used_pct  = total_salary / salary_cap * 100
    avg_age       = roster['AGE'].mean()
    total_vorpd   = roster['VORPD'].sum()
    pct_shooters  = (roster['FG3_PCT'] >= league_avg_fg3).mean() * 100

    print(f"\nOptimized 15-man roster:")
    display_cols = ['PLAYER_NAME', 'ARCHETYPE', 'AGE', 'COMPOSITE_SCORE_NORM', 'SALARY']
    print(roster[display_cols].to_string(index=False))

    print(f"\n--- SUMMARY ---")
    print(f"Total salary:      ${total_salary:>15,.0f}")
    print(f"Cap:               ${salary_cap:>15,.0f}")
    print(f"Cap used:          {cap_used_pct:>14.1f}%")
    print(f"Cap remaining:     ${salary_cap - total_salary:>15,.0f}")
    print(f"Total score:       {total_score:>15.2f}")
    print(f"Average score:     {avg_score:>15.2f}")
    print(f"Total VORPD:       {total_vorpd:>15.2f}")
    print(f"Average age:       {avg_age:>15.1f}")
    print(f"3PT shooters:      {pct_shooters:>14.0f}%")

    print(f"\nArchetype breakdown:")
    print(roster['ARCHETYPE'].value_counts().to_string())

    all_results[key] = {
        'scenario':     scenario_name,
        'roster':       roster,
        'total_salary': total_salary,
        'total_score':  total_score,
        'avg_score':    avg_score,
        'cap':          salary_cap,
        'cap_used_pct': cap_used_pct,
        'avg_age':      avg_age,
        'total_vorpd':  total_vorpd,
        'pct_shooters': pct_shooters,
        'objective':    objective,
        'note':         cfg['note'],
    }

# ============================================================
# SCENARIO COMPARISON TABLE
# ============================================================

print(f"\n{'=' * 70}")
print("SCENARIO COMPARISON")
print("=" * 70)
print(f"\n{'Key':<4} {'Scenario':<30} {'Cap $M':<9} {'Used%':<8} {'Score':<10} {'AvgAge':<8} {'VORPD'}")
print("-" * 80)
for key, res in all_results.items():
    print(f"{key:<4} {res['scenario']:<30} ${res['cap']/1e6:<7.0f}M "
          f"{res['cap_used_pct']:<8.1f} "
          f"{res['total_score']:<10.2f} "
          f"{res['avg_age']:<8.1f} "
          f"{res['total_vorpd']:.2f}")

# ============================================================
# SAVE ALL ROSTERS
# ============================================================

print(f"\n{'=' * 60}")
print("SAVING ROSTERS...")
for key, res in all_results.items():
    filename = f"optimized_roster_{key}.csv"
    res['roster'].to_csv(filename, index=False)
    print(f"  Saved: {filename}")

print(f"\n{'=' * 60}")
print("EXPANDED OPTIMIZATION COMPLETE")
print(f"  {len(all_results)} scenarios solved successfully")
print("  All rosters saved as optimized_roster_[A-J].csv")
print("=" * 60)
