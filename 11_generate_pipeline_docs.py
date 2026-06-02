"""
Option 2: Living Pipeline Documentation
Auto-generates linked Obsidian notes for each of the 9 pipeline steps,
with inputs, outputs, key decisions, and a master overview note.
Run from the project root: python 11_generate_pipeline_docs.py
"""

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import os
from pathlib import Path

BASE = Path(__file__).parent
VAULT = BASE
OUT = VAULT / "Pipeline_Docs"

STEPS = [
    {
        "num": "01",
        "name": "Feature Engineering",
        "file": "01_feature_engineering.py",
        "inputs": ["nba_master_threeyears.csv", "nba_onoff.csv"],
        "outputs": ["nba_complete_master.csv", "nba_scored_complete.csv"],
        "description": (
            "Loads 3 seasons of raw NBA player data (2021-24) and engineers the core features "
            "used throughout the pipeline. Applies team-context adjustments to account for "
            "system effects (e.g., a guard's AST% on a ball-dominant team), computes a weighted "
            "COMPOSITE_SCORE_NORM that blends offensive rating, defensive rating, shooting efficiency, "
            "and on/off differential. Also runs PCA to reduce the 30+ stat columns to 2D coordinates "
            "(PCA_X, PCA_Y) used for cluster visualization."
        ),
        "key_decisions": [
            "Season weights: 2023-24 = 0.45, 2022-23 = 0.35, 2021-22 = 0.20 (recency bias)",
            "VORPD (Value Over Replacement per Dollar) computed here as the core value metric",
            "ON_OFF_DIFF from 5-man lineup data merged via `nba_onoff.csv`",
            "IS_SHOOTER flag: 1 if FG3_PCT > 0.36 AND 3PA > 3.0",
        ],
        "downstream": ["02_clustering.py"],
    },
    {
        "num": "02",
        "name": "Player Clustering",
        "file": "02_clustering.py",
        "inputs": ["nba_scored_complete.csv"],
        "outputs": ["nba_clustered.csv"],
        "description": (
            "Clusters all players into 7 archetypes using K-means on the PCA-reduced feature space. "
            "The elbow method (see charts/elbow_method.png) guided the choice of k=7. "
            "Each player is assigned a CLUSTER integer (0-6) and an ARCHETYPE label string. "
            "Clustering runs on standardized features to prevent salary-scale dominance."
        ),
        "key_decisions": [
            "k=7 chosen via elbow method — balances granularity with interpretability",
            "Clustering on PCA components, not raw stats (avoids multicollinearity)",
            "Random state fixed (seed=42) for reproducibility",
            "K-means initialized with k-means++ for better convergence",
        ],
        "downstream": ["03_fix_labels.py"],
    },
    {
        "num": "03",
        "name": "Label Corrections",
        "file": "03_fix_labels.py",
        "inputs": ["nba_clustered.csv"],
        "outputs": ["nba_clustered.csv (updated)"],
        "description": (
            "Manual post-processing step that corrects obvious mis-classifications from K-means. "
            "K-means is agnostic to basketball domain knowledge — for example, it may cluster a "
            "stretch big with perimeter scorers due to 3P% similarity. This step applies "
            "rule-based overrides and renames clusters to human-readable archetype labels."
        ),
        "key_decisions": [
            "Manual overrides for ~15-20 players who span archetype boundaries",
            "Final archetype names assigned here: Elite Playmaker, Perimeter Scorer, Defensive Wing, etc.",
            "Players with < 500 minutes excluded from optimization (small sample size)",
        ],
        "downstream": ["04_optimizer_expanded.py", "05_compute_synergy.py"],
    },
    {
        "num": "04",
        "name": "Expanded Optimizer",
        "file": "04_optimizer_expanded.py",
        "inputs": ["nba_clustered.csv"],
        "outputs": [
            "optimized_roster_syn_A.csv", "optimized_roster_syn_B.csv",
            "optimized_roster_syn_C.csv", "optimized_roster_syn_D.csv",
            "optimized_roster_syn_E.csv", "optimized_roster_syn_F.csv",
            "optimized_roster_syn_G.csv", "optimized_roster_syn_H.csv",
            "optimized_roster_syn_I.csv", "optimized_roster_syn_J.csv",
        ],
        "description": (
            "Runs 10 Mixed-Integer Linear Programming (MILP) optimization scenarios using PuLP/CBC. "
            "Each scenario maximizes COMPOSITE_SCORE_NORM subject to salary cap, roster size (15 players), "
            "and archetype composition constraints. The 10 scenarios vary salary caps ($90M, $136M, $165M) "
            "and strategic priorities (defense-first, value-focus, star-heavy, etc.)."
        ),
        "key_decisions": [
            "Solver: CBC (open-source MILP solver via PuLP)",
            "Constraints: hard salary cap, min/max per archetype, exactly 15 roster spots",
            "Binary decision variables: x[player] ∈ {0, 1}",
            "Objective: maximize Σ(COMPOSITE_SCORE_NORM × x[player])",
            "Each scenario A-J tweaks archetype minimums or cap level",
        ],
        "downstream": ["07_optimizer_synergy.py"],
    },
    {
        "num": "05",
        "name": "Synergy Computation",
        "file": "05_compute_synergy.py",
        "inputs": ["nba_lineups_2man.csv", "nba_clustered.csv"],
        "outputs": ["nba_synergy_2324.csv", "nba_archetype_synergy.csv"],
        "description": (
            "Computes pairwise defensive synergy scores from 2-man lineup data. "
            "For each player pair with sufficient shared minutes, calculates the "
            "NET_SYNERGY = (shared_net_rating) - (player_A_individual_net) - (player_B_individual_net). "
            "Aggregates pair-level synergy up to the archetype level to fill in sparse data "
            "(most pairs have limited shared minutes)."
        ),
        "key_decisions": [
            "Minimum 50 shared minutes threshold to include a pair",
            "DEF_SYNERGY weighted 2x vs OFF_SYNERGY (defense is more team-driven)",
            "Archetype-level averages used as fallback for pairs with no shared data",
            "Only 2023-24 season used for synergy (most recent lineup chemistry)",
        ],
        "downstream": ["06_validate_synergy.py"],
    },
    {
        "num": "06",
        "name": "Synergy Validation",
        "file": "06_validate_synergy.py",
        "inputs": ["nba_synergy_2324.csv", "nba_archetype_synergy.csv", "nba_clustered.csv"],
        "outputs": ["nba_def_synergy_profile.csv"],
        "description": (
            "Validates synergy calculations for data quality issues: missing values, "
            "extreme outliers, and players appearing in synergy data but not in the clustered set. "
            "Produces the final DEF_SYNERGY_PROFILE per player — a single number summarizing "
            "how well each player's defensive tendencies complement a typical roster."
        ),
        "key_decisions": [
            "Outliers capped at ±3 standard deviations",
            "Players with <3 valid synergy pairs fallback to archetype average",
            "NET_SYNERGY_PROFILE = 0.6×DEF + 0.4×OFF aggregation",
        ],
        "downstream": ["07_optimizer_synergy.py"],
    },
    {
        "num": "07",
        "name": "Synergy Optimizer",
        "file": "07_optimizer_synergy.py",
        "inputs": ["nba_clustered.csv", "nba_def_synergy_profile.csv"],
        "outputs": ["optimized_roster_syn_A.csv (updated)", "… through syn_J.csv"],
        "description": (
            "Re-runs optimization incorporating synergy scores into the objective function. "
            "COMPOSITE_SYNERGY = COMPOSITE_SCORE_NORM + λ × NET_SYNERGY_PROFILE, where λ "
            "controls how much chemistry matters vs individual ability. "
            "This produces the final roster files used in all downstream reporting."
        ),
        "key_decisions": [
            "λ = 0.05 (synergy adds up to ~5% uplift to composite score)",
            "Synergy is additive to composite score, not multiplicative",
            "Same MILP structure as step 04 but with updated objective coefficients",
        ],
        "downstream": ["08_build_dashboard.py"],
    },
    {
        "num": "08",
        "name": "Dashboard Builder",
        "file": "08_build_dashboard.py",
        "inputs": [
            "nba_clustered.csv", "nba_archetype_synergy.csv",
            "optimized_roster_syn_A.csv … syn_J.csv",
        ],
        "outputs": ["NBA_Optimizer_Dashboard.xlsx"],
        "description": (
            "Generates the multi-tab Excel dashboard using openpyxl. Tabs include: "
            "Player Rankings, Archetype Summary, 10 Scenario Rosters, Salary Analysis, "
            "Synergy Matrix, and Top Value Players. Applies conditional formatting and "
            "embedded charts for presentation."
        ),
        "key_decisions": [
            "Conditional formatting: green gradient on composite scores, red on salary overpay",
            "Salary cap reference lines drawn at $90M, $136M, $165M",
            "Charts embedded directly vs linked (portability)",
        ],
        "downstream": [],
    },
    {
        "num": "09",
        "name": "Pipeline Verification",
        "file": "09_verify_pipeline.py",
        "inputs": ["All intermediate and final CSVs"],
        "outputs": ["Console validation report"],
        "description": (
            "End-to-end validation script that checks: all expected output files exist, "
            "row counts are within expected ranges, no null values in critical columns, "
            "salary cap constraints were respected in all scenarios, and composite scores "
            "are within [0, 100]. Acts as a smoke test after any pipeline change."
        ),
        "key_decisions": [
            "Expected row count ranges are soft bounds (±10%) not hard failures",
            "Reports warnings rather than exceptions for partial data issues",
        ],
        "downstream": [],
    },
]


def make_step_note(step: dict) -> str:
    inputs_md = "\n".join(f"  - `{f}`" for f in step["inputs"])
    outputs_md = "\n".join(f"  - `{f}`" for f in step["outputs"])
    decisions_md = "\n".join(f"  - {d}" for d in step["key_decisions"])
    downstream_md = (
        "\n".join(f"  - [[{s.replace('.py', '')}]]" for s in step["downstream"])
        if step["downstream"]
        else "  - _(final step)_"
    )
    prev_num = int(step["num"]) - 1
    next_num = int(step["num"]) + 1
    prev_link = f"[[{prev_num:02d}_{STEPS[prev_num-1]['name'].replace(' ', '_')}]]" if prev_num >= 1 else "_Start of pipeline_"
    next_link = f"[[{next_num:02d}_{STEPS[next_num-1]['name'].replace(' ', '_')}]]" if next_num <= 9 else "_End of pipeline_"

    return f"""---
step: {step['num']}
name: "{step['name']}"
script: "{step['file']}"
status: "completed"
tags: [pipeline, step-{step['num']}]
---

# Step {step['num']}: {step['name']}

← {prev_link} | → {next_link}

**Script:** `{step['file']}`

---

## What This Step Does

{step['description']}

---

## Inputs

{inputs_md}

## Outputs

{outputs_md}

---

## Key Decisions & Parameters

{decisions_md}

---

## Feeds Into

{downstream_md}

---

## Change Log

| Date | Change | Why |
|---|---|---|
| 2026-05-08 | Initial pipeline run | — |

## Notes

_Add notes about any modifications, experiments, or issues here._
"""


def make_overview_note() -> str:
    step_links = "\n".join(
        f"| [[{s['num']}_{s['name'].replace(' ', '_')}|Step {s['num']}: {s['name']}]] "
        f"| `{s['file']}` "
        f"| {', '.join(s['outputs'][:1])} |"
        for s in STEPS
    )

    return f"""---
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
{step_links}

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
"""


def main():
    print("=== Option 2: Generating Pipeline Documentation ===")
    OUT.mkdir(parents=True, exist_ok=True)

    for step in STEPS:
        safe_name = f"{step['num']}_{step['name'].replace(' ', '_')}"
        path = OUT / f"{safe_name}.md"
        path.write_text(make_step_note(step), encoding="utf-8")
        print(f"  Written: {path.name}")

    overview_path = OUT / "🏗️ Pipeline Overview.md"
    overview_path.write_text(make_overview_note(), encoding="utf-8")
    print(f"  Written: 🏗️ Pipeline Overview.md")

    print(f"\nAll done! Open Obsidian and browse Pipeline_Docs/")
    print("Tip: The overview note has a full pipeline flow diagram in text form.")


if __name__ == "__main__":
    main()
