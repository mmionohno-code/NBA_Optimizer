---
type: methodology
tags: [methodology, optimization, MILP]
---

# Mixed-Integer Linear Programming (MILP)

## The Core Question
Given a pool of players with known composite scores and salaries, pick exactly 15
to maximize total team quality without violating any constraints.

## Why MILP (Not Just Ranking)
A simple ranking can't handle constraints simultaneously. MILP finds the globally
optimal solution under ALL constraints at once.

## Decision Variables
For each player i: **x[i] ∈ {0, 1}**
- x[i] = 1 → player is selected for the roster
- x[i] = 0 → player is not selected

## Objective Function
**Maximize:** Σ (COMPOSITE_SYNERGY[i] × x[i])

Where: `COMPOSITE_SYNERGY = COMPOSITE_SCORE_NORM + λ × NET_SYNERGY_PROFILE`
And λ = 0.05

## Hard Constraints

| Constraint | Formula | Why |
|---|---|---|
| Salary cap | Σ SALARY[i] × x[i] ≤ CAP | Real NBA rule |
| Roster size | Σ x[i] = 15 | NBA roster limit |
| Min per archetype | Σ x[i ∈ archetype] ≥ min_k | Prevent mono-archetype teams |
| Max per archetype | Σ x[i ∈ archetype] ≤ max_k | Force roster diversity |
| Binary | x[i] ∈ {0, 1} | Can't select half a player |

## The 10 Scenarios (A–J)

| Scenario | Cap | Strategic Focus |
|---|---|---|
| A | $165M | Balanced (no archetype constraints) |
| B | $136M | Value focus (high VORPD) |
| C | $90M | Budget efficiency |
| D | $165M | Defense first (min Defensive Wings) |
| E | $136M | Playmaker heavy |
| F | $136M | 3-and-D focus |
| G | $165M | Star + depth |
| H | $90M | Young core |
| I | $136M | Balanced synergy |
| J | $165M | Championship roster |

## Solver: PuLP + CBC
- PuLP = Python modeling interface
- CBC = open-source MILP solver (no license cost)
- Solves each scenario in < 5 seconds
- Guaranteed globally optimal solution (not heuristic)

## Why Scenario C Is Isolated in the Graph
At $90M, no expensive star player (salary > ~$20M) can be selected.
The 15 players chosen are completely different from any $136M or $165M scenario.
Zero shared players = no connecting links in the graph = isolated cluster.

## Related Notes
- [[Methodology/Synergy Modeling]]
- [[NBA_Context/Salary Cap Rules]]
- [[Pipeline_Docs/04_Expanded_Optimizer]]
- [[Pipeline_Docs/07_Synergy_Optimizer]]
- [[Scenarios/Scenario A]] → [[Scenarios/Scenario J]]
