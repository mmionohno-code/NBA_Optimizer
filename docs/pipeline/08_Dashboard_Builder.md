---
step: 08
name: "Dashboard Builder"
script: "08_build_dashboard.py"
status: "completed"
tags: [pipeline, step-08]
---

# Step 08: Dashboard Builder

← [[07_Synergy_Optimizer]] | → [[09_Pipeline_Verification]]

**Script:** `08_build_dashboard.py`

---

## What This Step Does

Generates the multi-tab Excel dashboard using openpyxl. Tabs include: Player Rankings, Archetype Summary, 10 Scenario Rosters, Salary Analysis, Synergy Matrix, and Top Value Players. Applies conditional formatting and embedded charts for presentation.

---

## Inputs

  - `nba_clustered.csv`
  - `nba_archetype_synergy.csv`
  - `optimized_roster_syn_A.csv … syn_J.csv`

## Outputs

  - `NBA_Optimizer_Dashboard.xlsx`

---

## Key Decisions & Parameters

  - Conditional formatting: green gradient on composite scores, red on salary overpay
  - Salary cap reference lines drawn at $90M, $136M, $165M
  - Charts embedded directly vs linked (portability)

---

## Feeds Into

  - _(final step)_

---

## Change Log

| Date | Change | Why |
|---|---|---|
| 2026-05-08 | Initial pipeline run | — |

## Notes

_Add notes about any modifications, experiments, or issues here._
