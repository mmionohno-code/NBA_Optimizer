---
step: 06
name: "Synergy Validation"
script: "06_validate_synergy.py"
status: "completed"
tags: [pipeline, step-06]
---

# Step 06: Synergy Validation

← [[05_Synergy_Computation]] | → [[07_Synergy_Optimizer]]

**Script:** `06_validate_synergy.py`

---

## What This Step Does

Validates synergy calculations for data quality issues: missing values, extreme outliers, and players appearing in synergy data but not in the clustered set. Produces the final DEF_SYNERGY_PROFILE per player — a single number summarizing how well each player's defensive tendencies complement a typical roster.

---

## Inputs

  - `nba_synergy_2324.csv`
  - `nba_archetype_synergy.csv`
  - `nba_clustered.csv`

## Outputs

  - `nba_def_synergy_profile.csv`

---

## Key Decisions & Parameters

  - Outliers capped at ±3 standard deviations
  - Players with <3 valid synergy pairs fallback to archetype average
  - NET_SYNERGY_PROFILE = 0.6×DEF + 0.4×OFF aggregation

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
