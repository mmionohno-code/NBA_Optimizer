---
step: 03
name: "Label Corrections"
script: "03_fix_labels.py"
status: "completed"
tags: [pipeline, step-03]
---

# Step 03: Label Corrections

← [[02_Player_Clustering]] | → [[04_Expanded_Optimizer]]

**Script:** `03_fix_labels.py`

---

## What This Step Does

Manual post-processing step that corrects obvious mis-classifications from K-means. K-means is agnostic to basketball domain knowledge — for example, it may cluster a stretch big with perimeter scorers due to 3P% similarity. This step applies rule-based overrides and renames clusters to human-readable archetype labels.

---

## Inputs

  - `nba_clustered.csv`

## Outputs

  - `nba_clustered.csv (updated)`

---

## Key Decisions & Parameters

  - Manual overrides for ~15-20 players who span archetype boundaries
  - Final archetype names assigned here: Elite Playmaker, Perimeter Scorer, Defensive Wing, etc.
  - Players with < 500 minutes excluded from optimization (small sample size)

---

## Feeds Into

  - [[04_optimizer_expanded]]
  - [[05_compute_synergy]]

---

## Change Log

| Date | Change | Why |
|---|---|---|
| 2026-05-08 | Initial pipeline run | — |

## Notes

_Add notes about any modifications, experiments, or issues here._
