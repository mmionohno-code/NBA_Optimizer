 import pandas as pd
import numpy as np
from pulp import LpProblem, LpMaximize, LpVariable, LpStatus, lpSum, value, PULP_CBC_CMD

print("=" * 60)
print("NBA ROSTER OPTIMIZER — MILP MODEL")
print("=" * 60)

# ============================================================
# LOAD 2023-24 DATA
# We optimize on the most recent season only
# ============================================================

df = pd.read_csv('nba_clustered.csv')
df_2324 = df[df['SEASON'] == '2023-24'].copy().reset_index(drop=True)

print(f"\nPlayers available for selection: {len(df_2324)}")
print(f"Archetypes: {sorted(df_2324['ARCHETYPE'].unique())}")
print(f"Salary range: ${df_2324['SALARY'].min():,.0f} — ${df_2324['SALARY'].max():,.0f}")

# ============================================================
# REAL NBA SALARY CAP FIGURES (2023-24 SEASON)
# Source: NBA Collective Bargaining Agreement
# ============================================================

SCENARIOS = {
    'A — Hard Cap ($136M)':     136_021_000,
    'B — Luxury Tax ($165M)':   165_294_000,
    'C — Budget Team ($90M)':    90_000_000,
}

ARCHETYPES = df_2324['ARCHETYPE'].unique()
TEAMS = df_2324['TEAM_ABBREVIATION'].unique()
N = len(df_2324)

all_results = {}

# ============================================================
# RUN ALL THREE SCENARIOS
# ============================================================

for scenario_name, salary_cap in SCENARIOS.items():

    print(f"\n{'=' * 60}")
    print(f"SCENARIO {scenario_name}")
    print(f"Salary cap: ${salary_cap:,}")
    print("=" * 60)

    # ----------------------------------------------------------
    # DECISION VARIABLES
    # x[i] = 1 if player i is selected, 0 if not
    # Binary — a player is either on the roster or not
    # ----------------------------------------------------------

    prob = LpProblem(f"NBA_Roster_{scenario_name[:1]}", LpMaximize)
    x = [LpVariable(f"x_{i}", cat='Binary') for i in range(N)]

    # ----------------------------------------------------------
    # OBJECTIVE FUNCTION
    # Maximize total composite score of selected players
    # ----------------------------------------------------------

    prob += lpSum(df_2324.loc[i, 'COMPOSITE_SCORE_NORM'] * x[i] for i in range(N))

    # ----------------------------------------------------------
    # CONSTRAINT 1 — Salary Cap (HARD)
    # Total salary of all selected players must not exceed cap
    # ----------------------------------------------------------

    prob += (
        lpSum(df_2324.loc[i, 'SALARY'] * x[i] for i in range(N)) <= salary_cap,
        "SalaryCap"
    )

    # ----------------------------------------------------------
    # CONSTRAINT 2 — Roster Size (HARD)
    # NBA rosters have exactly 15 players
    # ----------------------------------------------------------

    prob += (lpSum(x[i] for i in range(N)) == 15, "RosterSize")

    # ----------------------------------------------------------
    # CONSTRAINT 3 — Archetype Coverage (HARD)
    # Minimum players required per archetype.
    # Derived from basketball reality:
    #   - A real NBA rotation needs at least 2 guards/wings
    #     who can handle the ball and initiate offense
    #   - At least 2 wings for switching defense
    #   - Big men capped at 6 total to prevent unrealistic
    #     rosters (our composite score heavily rewards bigs)
    # ----------------------------------------------------------

    archetype_minimums = {
        'Perimeter Playmaker':    2,   # need real ball handlers
        '3-and-D Wing':           2,   # need perimeter depth
        'Defensive Specialist':   1,
        'Elite Two-Way Big':      1,
        'Rim Protector':          1,
        'Stretch Big':            1,
        'Bench / Fringe Player':  1,
    }

    for archetype, min_count in archetype_minimums.items():
        indices = df_2324[df_2324['ARCHETYPE'] == archetype].index.tolist()
        prob += (
            lpSum(x[i] for i in indices) >= min_count,
            f"Min_{archetype.replace(' ', '_').replace('/', '_')}"
        )

    # ----------------------------------------------------------
    # CONSTRAINT 5 — Big Man Cap (HARD)
    # Total big men (Rim Protectors + Elite Two-Way Bigs +
    # Stretch Bigs) cannot exceed 7 of the 15 roster spots.
    # This reflects real NBA roster construction — you need
    # perimeter players to actually run an offense.
    # Without this, the optimizer loads up on cheap bigs.
    # ----------------------------------------------------------

    big_man_archetypes = ['Rim Protector', 'Elite Two-Way Big', 'Stretch Big']
    big_indices = df_2324[df_2324['ARCHETYPE'].isin(big_man_archetypes)].index.tolist()
    prob += (
        lpSum(x[i] for i in big_indices) <= 7,
        "MaxBigMen"
    )

    # ----------------------------------------------------------
    # CONSTRAINT 4 — Team Diversity (HARD)
    # Max 2 players from the same real NBA team.
    # Prevents unrealistic team-stacking and models real
    # front office behavior of diversifying the roster.
    # ----------------------------------------------------------

    for team in TEAMS:
        indices = df_2324[df_2324['TEAM_ABBREVIATION'] == team].index.tolist()
        if len(indices) > 2:
            prob += (
                lpSum(x[i] for i in indices) <= 2,
                f"MaxTwo_{team}"
            )

    # ----------------------------------------------------------
    # SOLVE
    # CBC solver (bundled with PuLP) — free and reliable
    # for problems of this size
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
        'COMPOSITE_SCORE_NORM', 'SALARY', 'VORPD'
    ]].copy()

    roster = roster.sort_values('COMPOSITE_SCORE_NORM', ascending=False)

    total_salary = roster['SALARY'].sum()
    total_score = roster['COMPOSITE_SCORE_NORM'].sum()
    avg_score = roster['COMPOSITE_SCORE_NORM'].mean()
    cap_used_pct = total_salary / salary_cap * 100

    print(f"\nOptimized 15-man roster:")
    print(roster.to_string(index=False))

    print(f"\n--- SUMMARY ---")
    print(f"Total salary:       ${total_salary:>15,.0f}")
    print(f"Cap:                ${salary_cap:>15,.0f}")
    print(f"Cap used:           {cap_used_pct:>14.1f}%")
    print(f"Cap remaining:      ${salary_cap - total_salary:>15,.0f}")
    print(f"Total score:        {total_score:>15.2f}")
    print(f"Average score:      {avg_score:>15.2f}")

    print(f"\nArchetype breakdown:")
    print(roster['ARCHETYPE'].value_counts().to_string())

    all_results[scenario_name] = {
        'roster': roster,
        'total_salary': total_salary,
        'total_score': total_score,
        'avg_score': avg_score,
        'cap': salary_cap,
        'cap_used_pct': cap_used_pct
    }

# ============================================================
# SCENARIO COMPARISON
# ============================================================

print(f"\n{'=' * 60}")
print("SCENARIO COMPARISON")
print("=" * 60)

print(f"\n{'Scenario':<30} {'Cap':<15} {'Used %':<10} {'Total Score':<15} {'Avg Score'}")
print("-" * 80)
for name, res in all_results.items():
    print(f"{name:<30} ${res['cap']/1e6:<13.0f}M "
          f"{res['cap_used_pct']:<10.1f} "
          f"{res['total_score']:<15.2f} "
          f"{res['avg_score']:.2f}")

# ============================================================
# SAVE RESULTS
# ============================================================

for scenario_name, res in all_results.items():
    safe_name = scenario_name[:1]
    filename = f"optimized_roster_{safe_name}.csv"
    res['roster'].to_csv(filename, index=False)
    print(f"\nSaved: {filename}")

print(f"\n{'=' * 60}")
print("OPTIMIZATION COMPLETE")
print("Three optimized rosters saved.")
print("Next step: Week 5 — Excel Dashboard")
print("=" * 60)
