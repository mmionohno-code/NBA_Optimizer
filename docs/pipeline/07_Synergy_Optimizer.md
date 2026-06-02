---
step: 07
name: "Synergy Optimizer"
script: "07_optimizer_synergy.py"
status: "completed"
tags: [pipeline, step-07]
---

# Step 07: Synergy Optimizer

← [[06_Synergy_Validation]] | → [[08_Dashboard_Builder]]

**Script:** `07_optimizer_synergy.py`

---

## What This Step Does

Re-runs optimization incorporating synergy scores into the objective function. COMPOSITE_SYNERGY = COMPOSITE_SCORE_NORM + λ × NET_SYNERGY_PROFILE, where λ controls how much chemistry matters vs individual ability. This produces the final roster files used in all downstream reporting.

---

## Inputs

  - `nba_clustered.csv`
  - `nba_def_synergy_profile.csv`

## Outputs

  - `optimized_roster_syn_A.csv (updated)`
  - `… through syn_J.csv`

---

## Key Decisions & Parameters

  - λ = 0.05 (synergy adds up to ~5% uplift to composite score)
  - Synergy is additive to composite score, not multiplicative
  - Same MILP structure as step 04 but with updated objective coefficients

---

## Feeds Into

  - [[08_build_dashboard]]

---

## Change Log

| Date | Change | Why |
|---|---|---|
| 2026-05-08 | Initial pipeline run | — |

## Notes

_Add notes about any modifications, experiments, or issues here._
