---
step: 01
name: "Feature Engineering"
script: "01_feature_engineering.py"
status: "completed"
tags: [pipeline, step-01]
---

# Step 01: Feature Engineering

← _Start of pipeline_ | → [[02_Player_Clustering]]

**Script:** `01_feature_engineering.py`

---

## What This Step Does

Loads 3 seasons of raw NBA player data (2021-24) and engineers the core features used throughout the pipeline. Applies team-context adjustments to account for system effects (e.g., a guard's AST% on a ball-dominant team), computes a weighted COMPOSITE_SCORE_NORM that blends offensive rating, defensive rating, shooting efficiency, and on/off differential. Also runs PCA to reduce the 30+ stat columns to 2D coordinates (PCA_X, PCA_Y) used for cluster visualization.

---

## Inputs

  - `nba_master_threeyears.csv`
  - `nba_onoff.csv`

## Outputs

  - `nba_complete_master.csv`
  - `nba_scored_complete.csv`

---

## Key Decisions & Parameters

  - Season weights: 2023-24 = 0.45, 2022-23 = 0.35, 2021-22 = 0.20 (recency bias)
  - VORPD (Value Over Replacement per Dollar) computed here as the core value metric
  - ON_OFF_DIFF from 5-man lineup data merged via `nba_onoff.csv`
  - IS_SHOOTER flag: 1 if FG3_PCT > 0.36 AND 3PA > 3.0

---

## Feeds Into

  - [[02_clustering]]

---

## Change Log

| Date | Change | Why |
|---|---|---|
| 2026-05-08 | Initial pipeline run | — |

## Notes

_Add notes about any modifications, experiments, or issues here._
