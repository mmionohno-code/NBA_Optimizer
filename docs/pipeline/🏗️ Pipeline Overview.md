---
type: overview
tags: [pipeline, index]
---

# 🏗️ NBA Optimizer Pipeline

> This vault documents the full 9-step data pipeline from raw NBA stats to optimized rosters.

---

## Pipeline Flow

```
Raw Data (3 seasons)
    │
    ▼
01_feature_engineering.py  →  nba_complete_master.csv, nba_scored_complete.csv
    │
    ▼
02_clustering.py           →  nba_clustered.csv (7 archetypes)
    │
    ▼
03_fix_labels.py           →  nba_clustered.csv (corrected labels)
    │
    ├──────────────────────────┐
    ▼                          ▼
04_optimizer_expanded.py   05_compute_synergy.py
(10 roster scenarios)      (pairwise synergy scores)
    │                          │
    └──────────┬───────────────┘
               ▼
          06_validate_synergy.py
               │
               ▼
          07_optimizer_synergy.py  →  Final optimized rosters (A–J)
               │
               ▼
          08_build_dashboard.py    →  NBA_Optimizer_Dashboard.xlsx
               │
               ▼
          09_verify_pipeline.py   →  Validation report
```

---

## Steps

| Step | Script | Primary Output |
|---|---|---|
| [[01_Feature_Engineering|Step 01: Feature Engineering]] | `01_feature_engineering.py` | nba_complete_master.csv |
| [[02_Player_Clustering|Step 02: Player Clustering]] | `02_clustering.py` | nba_clustered.csv |
| [[03_Label_Corrections|Step 03: Label Corrections]] | `03_fix_labels.py` | nba_clustered.csv (updated) |
| [[04_Expanded_Optimizer|Step 04: Expanded Optimizer]] | `04_optimizer_expanded.py` | optimized_roster_syn_A.csv |
| [[05_Synergy_Computation|Step 05: Synergy Computation]] | `05_compute_synergy.py` | nba_synergy_2324.csv |
| [[06_Synergy_Validation|Step 06: Synergy Validation]] | `06_validate_synergy.py` | nba_def_synergy_profile.csv |
| [[07_Synergy_Optimizer|Step 07: Synergy Optimizer]] | `07_optimizer_synergy.py` | optimized_roster_syn_A.csv (updated) |
| [[08_Dashboard_Builder|Step 08: Dashboard Builder]] | `08_build_dashboard.py` | NBA_Optimizer_Dashboard.xlsx |
| [[09_Pipeline_Verification|Step 09: Pipeline Verification]] | `09_verify_pipeline.py` | Console validation report |

---

## Supporting Scripts

| Script | Purpose |
|---|---|
| `optimizer.py` | Standalone MILP solver (3 cap scenarios) |
| `build_database.py` | Populates `nba_optimizer.db` SQLite |
| `build_interactive_dashboard.py` | Generates HTML dashboard |
| `build_pptx.py` | Generates PowerPoint presentation |
| `build_tableau_data.py` | Exports Tableau-ready CSVs |

---

## Key Design Choices

- **MILP Solver:** PuLP + CBC (open source, no license cost)
- **Synergy weight (λ):** 0.05 — synergy is a tiebreaker, not dominant
- **Season weights:** 45% / 35% / 20% most-to-least recent
- **Archetype count (k):** 7 — validated via elbow method
- **Salary caps modeled:** $90M (budget), $136M (hard cap), $165M (luxury tax)

---

## Data Sources

- Player stats: 2021-22, 2022-23, 2023-24 NBA seasons
- Lineup data: 2-man and 5-man lineup splits (Basketball Reference)
- Salary data: 2023-24 cap figures
