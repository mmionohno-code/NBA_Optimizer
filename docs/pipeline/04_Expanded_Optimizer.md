---
step: 04
name: "Expanded Optimizer"
script: "04_optimizer_expanded.py"
status: "completed"
tags: [pipeline, step-04]
---

# Step 04: Expanded Optimizer

← [[03_Label_Corrections]] | → [[05_Synergy_Computation]]

**Script:** `04_optimizer_expanded.py`

---

## What This Step Does

Runs 10 Mixed-Integer Linear Programming (MILP) optimization scenarios using PuLP/CBC. Each scenario maximizes COMPOSITE_SCORE_NORM subject to salary cap, roster size (15 players), and archetype composition constraints. The 10 scenarios vary salary caps ($90M, $136M, $165M) and strategic priorities (defense-first, value-focus, star-heavy, etc.).

---

## Inputs

  - `nba_clustered.csv`

## Outputs

  - `optimized_roster_syn_A.csv`
  - `optimized_roster_syn_B.csv`
  - `optimized_roster_syn_C.csv`
  - `optimized_roster_syn_D.csv`
  - `optimized_roster_syn_E.csv`
  - `optimized_roster_syn_F.csv`
  - `optimized_roster_syn_G.csv`
  - `optimized_roster_syn_H.csv`
  - `optimized_roster_syn_I.csv`
  - `optimized_roster_syn_J.csv`

---

## Key Decisions & Parameters

  - Solver: CBC (open-source MILP solver via PuLP)
  - Constraints: hard salary cap, min/max per archetype, exactly 15 roster spots
  - Binary decision variables: x[player] ∈ {0, 1}
  - Objective: maximize Σ(COMPOSITE_SCORE_NORM × x[player])
  - Each scenario A-J tweaks archetype minimums or cap level

---

## Feeds Into

  - [[07_optimizer_synergy]]

---

## Change Log

| Date | Change | Why |
|---|---|---|
| 2026-05-08 | Initial pipeline run | — |

## Notes

_Add notes about any modifications, experiments, or issues here._
