---
type: project-story
tags: [story, technical, evolution]
date: 2026-05-08
---

# Technical Evolution

## Phase 1 — Basic Stats Pipeline
**Goal:** Pull real NBA data and compute a meaningful player score.

- Source: `nba_api` library (official NBA.com data)
- Salary data: HoopsHype scraping
- Stats used: OFF_RATING, DEF_RATING, NET_RATING, TS_PCT, USG_PCT, AST_PCT, REB_PCT, PIE
- Initial composite: simple weighted average (later replaced by PCA-driven weights)

## Phase 2 — Statistical Rigor
**Goal:** Make the scoring system defensible.

- Added Pearson/Spearman correlation analysis to justify which stats matter
- Replaced arbitrary weights with PCA-derived importance scores
- Added Bayesian Shrinkage to handle small-sample players
- Added VORPD (Value Over Replacement per Dollar) as the core value metric

## Phase 3 — Multi-Season Expansion
**Goal:** Reduce noise from single-season outliers.

- Expanded from 2023-24 only to 3 seasons (2021-22, 2022-23, 2023-24)
- Applied season weights: **45% / 35% / 20%** (most to least recent)
- Added team-context adjustments (system effects on individual stats)
- ON_OFF differential from 5-man lineup data merged in

## Phase 4 — Clustering
**Goal:** Group players into meaningful archetypes.

- K-Means on PCA-reduced features (k=7, elbow method)
- 7 archetypes: Elite Playmaker, Perimeter Scorer, Defensive Wing,
  Stretch Big, Paint Anchor, Two-Way Guard, Role Player
- Manual label corrections for ~15-20 borderline players
- IS_SHOOTER flag engineered (FG3_PCT > 36% AND 3PA > 3.0)

## Phase 5 — MILP Optimization
**Goal:** Find the mathematically optimal roster under real constraints.

- Solver: PuLP + CBC (open-source, no license required)
- Binary decision variables: x[player] ∈ {0, 1}
- 3 salary tiers: $90M (budget), $136M (hard cap), $165M (luxury tax)
- Expanded to 10 scenarios (A–J) with different strategic constraints

## Phase 6 — Synergy Modeling
**Goal:** Account for player chemistry, not just individual stats.

- 2-man lineup data from Basketball Reference
- Minimum 50 shared minutes threshold
- NET_SYNERGY = shared_net_rating - individual_A_net - individual_B_net
- Archetype-level fallback for sparse pairs
- λ = 0.05 synergy weight in optimizer objective

## Phase 7 — Multi-Format Reporting
**Goal:** Make results accessible to any audience.

- `NBA_Optimizer_Dashboard.xlsx` — Excel with conditional formatting and charts
- `NBA_Interactive_Dashboard.html` — standalone HTML dashboard
- `NBA_Optimizer_Presentation.pptx` — PowerPoint deck
- `nba_optimizer.db` — SQLite with 20+ analytical views
- `tableau_data/` — 4 Tableau-ready CSV exports
- This Obsidian vault — knowledge base and documentation

## Related Notes
- [[Project_Story/Origin & Vision]]
- [[Methodology/MILP Optimization]]
- [[Methodology/Synergy Modeling]]
- [[Methodology/Feature Engineering]]
