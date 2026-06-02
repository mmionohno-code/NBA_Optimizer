---
step: 05
name: "Synergy Computation"
script: "05_compute_synergy.py"
status: "completed"
tags: [pipeline, step-05]
---

# Step 05: Synergy Computation

← [[04_Expanded_Optimizer]] | → [[06_Synergy_Validation]]

**Script:** `05_compute_synergy.py`

---

## What This Step Does

Computes pairwise defensive synergy scores from 2-man lineup data. For each player pair with sufficient shared minutes, calculates the NET_SYNERGY = (shared_net_rating) - (player_A_individual_net) - (player_B_individual_net). Aggregates pair-level synergy up to the archetype level to fill in sparse data (most pairs have limited shared minutes).

---

## Inputs

  - `nba_lineups_2man.csv`
  - `nba_clustered.csv`

## Outputs

  - `nba_synergy_2324.csv`
  - `nba_archetype_synergy.csv`

---

## Key Decisions & Parameters

  - Minimum 50 shared minutes threshold to include a pair
  - DEF_SYNERGY weighted 2x vs OFF_SYNERGY (defense is more team-driven)
  - Archetype-level averages used as fallback for pairs with no shared data
  - Only 2023-24 season used for synergy (most recent lineup chemistry)

---

## Feeds Into

  - [[06_validate_synergy]]

---

## Change Log

| Date | Change | Why |
|---|---|---|
| 2026-05-08 | Initial pipeline run | — |

## Notes

_Add notes about any modifications, experiments, or issues here._
