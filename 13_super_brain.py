"""
Super Brain: Comprehensive Obsidian Knowledge Base
Adds methodology notes, synergy pair notes, project story, NBA rules,
resume framing, data sources, and concept notes drawn from full project history.
Run from project root: python 13_super_brain.py
"""

import pandas as pd
from pathlib import Path
from datetime import date

BASE = Path(__file__).parent
VAULT = BASE
OUT = VAULT / "NBA_Knowledge_Base"
TODAY = date.today().isoformat()


def make_dirs():
    for sub in [
        "Methodology",
        "Synergy_Pairs",
        "Project_Story",
        "NBA_Context",
        "Resume",
    ]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)


# ── 1. PROJECT STORY NOTES ─────────────────────────────────────────────────

def write_project_story():
    notes = {
        "Origin & Vision.md": f"""---
type: project-story
tags: [story, origin, vision]
date: {TODAY}
---

# The Origin Story

## Why This Project Exists

This project started as a resume builder — a way to demonstrate real data science skills
to employers using a domain (basketball) that's both interesting and analytically rich.

The core question: *"Given an NBA salary cap and a pool of players, which 15-player roster
maximizes team quality?"* It's a deceptively hard problem that touches machine learning,
optimization, and sports analytics simultaneously.

## The Journey: Zero to Data Scientist

The project was built from absolute scratch:

- **No prior programming experience** when this started
- Learned Python installation, VS Code setup, library management, and debugging all from scratch
- Every error message was a new learning moment — PATH variables, virtual environments, admin mode
- The Python 3.14 installation alone took a full debugging session

That journey is part of what makes this project compelling on a resume — it wasn't handed over,
it was built line by line.

## The Pivot to Statistical Rigor

An early version used **arbitrary weights** for the composite score:
- 25% NET_RATING, 20% PIE, etc.

The decision was made to reject this and insist on **data-driven weights** instead:
1. Correlation analysis to find which stats actually predict winning
2. PCA to let the data determine the weights mathematically
3. Validation against real 2023-24 MVP and standings outcomes
4. Sensitivity analysis to prove robustness

This pivot is one of the most important decisions in the project. It's the difference between
a project that "looks analytical" and one that **is** analytical.

## The Scope Creep (Good Kind)

What started as "optimize a roster" expanded into:
- 3 seasons of data instead of 1 (2021-22, 2022-23, 2023-24)
- Synergy modeling from 2-man lineup data
- 10 optimization scenarios instead of 3
- SQLite database with views
- Interactive HTML dashboard
- PowerPoint presentation
- Tableau export
- Obsidian knowledge base (this vault)

Each addition made the project more complete and more defensible in a job interview.

## Related Notes
- [[Project_Story/Technical Evolution]]
- [[Project_Story/Key Decisions Ledger]]
- [[Project_Story/Resume Framing]]
- [[Methodology/Full Pipeline Overview]]
""",

        "Technical Evolution.md": f"""---
type: project-story
tags: [story, technical, evolution]
date: {TODAY}
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
- Binary decision variables: x[player] ∈ {{0, 1}}
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
""",

        "Key Decisions Ledger.md": f"""---
type: project-story
tags: [story, decisions, ledger]
date: {TODAY}
---

# Key Decisions Ledger

A chronological record of the most important choices made during the project.

---

## D01 — PCA over Arbitrary Weights
**Decision:** Use PCA to derive composite score weights from data, not intuition.
**Why:** Arbitrary weights (25% NET_RATING etc.) are indefensible in an interview.
PCA lets the data reveal which dimensions of performance actually vary together.
**Impact:** The composite score became statistically grounded and reproducible.
**See:** [[Methodology/PCA & Dimensionality Reduction]]

---

## D02 — 3 Seasons, Not 1
**Decision:** Use 2021-22, 2022-23, 2023-24 data with recency weighting.
**Why:** Single-season stats have high variance. A player who got injured in December
looks terrible on a full-season split. Three seasons reduces noise.
**Weights:** 45% (2023-24), 35% (2022-23), 20% (2021-22)
**Impact:** More stable composite scores, especially for veterans.

---

## D03 — K-Means with k=7
**Decision:** 7 archetypes via K-Means, validated with elbow method.
**Why:** k=7 was the inflection point on the elbow curve. Below 7, archetypes were
too broad (e.g. all guards in one cluster). Above 7, clusters became too granular.
**See:** [[Methodology/K-Means Clustering]]

---

## D04 — Manual Label Corrections (Step 03)
**Decision:** Add a manual override step after K-Means.
**Why:** K-Means is mathematically agnostic to basketball domain knowledge.
A stretch big with elite 3P% might cluster with perimeter scorers purely on that stat.
Domain knowledge matters here.
**Impact:** ~15-20 players were reclassified to more accurate archetypes.

---

## D05 — CBC Solver via PuLP
**Decision:** Use open-source CBC solver, not Gurobi or CPLEX.
**Why:** Gurobi requires a paid license. CBC is free, handles our problem size easily
(~500 players, 15-player selection), and produces optimal solutions in seconds.
**Impact:** Anyone can run this project without purchasing software.

---

## D06 — 50-Minute Synergy Threshold
**Decision:** Require minimum 50 shared minutes for a synergy pair to count.
**Why:** With fewer shared minutes, the NET_SYNERGY estimate is too noisy.
A pair that played 10 minutes together and happened to outscore opponents by 20 points
looks like incredible synergy — it's just small-sample variance.
**Impact:** Cleaner synergy data; sparse pairs fall back to archetype averages.

---

## D07 — λ = 0.05 Synergy Weight
**Decision:** Synergy contributes 5% uplift to composite score in the optimizer.
**Why:** Synergy is real but secondary to individual ability. At λ=0.05, a player with
a 91.0 composite + excellent synergy can edge out a 91.4 player with poor synergy —
but a clearly superior player is never bumped by a mediocre one.
**See:** [[Research_Log/Decisions/Lambda Weight Decision]]

---

## D08 — 10 Scenarios (A–J), Not 3
**Decision:** Expand from 3 to 10 optimization scenarios.
**Why:** 3 scenarios (hard cap / luxury / budget) only varies the salary constraint.
10 scenarios also vary the strategic objective: defense-first, playmaker-heavy,
3-and-D focus, star+depth, young core, championship roster.
**Impact:** Much richer comparison surface. Scenario C's isolation in the graph view
is visible proof that the $90M budget world is categorically different.

---

## D09 — Season Weights in Composite Score
**Decision:** Apply SEASON_WEIGHT as a multiplier before aggregating across seasons.
**Why:** A player's 2021-22 performance is less predictive of future performance than
their 2023-24 performance. Weighting prevents old data from dragging down improving players.
**Impact:** Young players on upward trajectories score higher than their 3-year average
would suggest.

---

## Related Notes
- [[Project_Story/Origin & Vision]]
- [[Project_Story/Technical Evolution]]
- [[Research_Log/Decisions/Lambda Weight Decision]]
""",

        "Resume Framing.md": f"""---
type: project-story
tags: [story, resume, career]
date: {TODAY}
---

# Resume Framing Guide

How to present each part of this project for different audiences.

---

## One-Line Summary

> *Built end-to-end NBA roster optimization system using PCA, K-Means clustering, and
> MILP solver — 551 players, 7 archetypes, 10 salary cap scenarios, multi-format reporting.*

---

## For a Data Science / Analytics Role

**Bullet points:**
- Engineered composite player scoring system from 3 seasons of NBA data using PCA-derived
  weights, Bayesian shrinkage, and team-context adjustments
- Clustered 551 players into 7 archetypes using K-Means on PCA-reduced features (k selected
  via elbow method); validated against domain knowledge with manual corrections
- Modeled pairwise player synergy from 2-man lineup data (1,661 pairs); incorporated as
  λ=0.05 objective weight in MILP optimizer
- Generated 10 roster scenarios across 3 salary cap tiers ($90M / $136M / $165M) using
  PuLP/CBC solver with binary decision variables and archetype composition constraints

**Skills to highlight:** PCA, K-Means, MILP, pandas, scikit-learn, PuLP, SQLite, multi-format delivery

---

## For a Sports Analytics Role

**Bullet points:**
- Developed NBA salary cap optimization model combining advanced stats (VORPD, ON/OFF
  differential, adjusted offensive/defensive ratings) with player chemistry modeling
- Applied recency-weighted multi-season framework (45/35/20% across 3 years) with
  team-context adjustments to isolate player contribution from system effects
- Identified value inefficiencies: high-VORPD, low-salary players underweighted by
  market but captured by optimization model

**Skills to highlight:** Advanced stats, salary cap modeling, VORPD, lineup analysis, synergy

---

## For a General Analyst / Business Intelligence Role

**Bullet points:**
- Built automated analytics pipeline processing 1,200+ player-season records into
  actionable roster recommendations, with deliverables in Excel, HTML, PowerPoint, and Tableau
- Designed SQLite database with 20+ analytical views for ad-hoc querying; created
  Obsidian knowledge base with 1,750+ linked notes for self-documenting analytics

**Skills to highlight:** Excel, Tableau, SQL, dashboard design, data storytelling

---

## Interview Story Arc

1. **Hook:** "I wanted a project that combined statistics and optimization — two things
   that sound abstract but have very concrete answers in basketball."
2. **Problem:** "The hard part isn't ranking players. Everyone has a ranking. The hard
   part is building a *team* under real financial constraints."
3. **Rigor moment:** "The first version used arbitrary weights. I threw it out and rebuilt
   it with PCA — let the data tell me which stats actually matter."
4. **Result:** "The optimizer consistently finds value players the market underprices.
   Scenario C — the $90M budget roster — has zero overlap with any other scenario, which
   means the $90M world is a genuinely different player market."
5. **Scale:** "551 unique players, 1,185 player-season records, 1,661 synergy pairs,
   10 optimized rosters — all documented in a linked knowledge base."

---

## Related Notes
- [[Project_Story/Origin & Vision]]
- [[Project_Story/Key Decisions Ledger]]
- [[NBA_Context/Salary Cap Rules]]
""",
    }

    for filename, content in notes.items():
        path = OUT / "Project_Story" / filename
        path.write_text(content, encoding="utf-8")
        print(f"  Story: {filename}")


# ── 2. METHODOLOGY NOTES ───────────────────────────────────────────────────

def write_methodology_notes():
    notes = {
        "Full Pipeline Overview.md": f"""---
type: methodology
tags: [methodology, pipeline, overview]
---

# Full Pipeline Overview

## The Question This Answers
*"Given an NBA salary cap and a pool of players, which 15-player roster maximizes team quality?"*

## Why It's Hard
- Players have interdependencies (synergy, position overlap, salary)
- Salary caps create hard constraints not handled by simple ranking
- Individual stats don't capture team fit or player chemistry
- Multi-season data is noisy; single-season data misses trends

## The Solution Stack

| Problem | Solution | Tool |
|---|---|---|
| Too many stats, multicollinearity | Dimensionality reduction | [[Methodology/PCA & Dimensionality Reduction]] |
| Stats don't reflect system | Team-context adjustment | Feature engineering |
| Single season noise | 3-season recency weighting | Pandas |
| Unknown player types | Archetype clustering | [[Methodology/K-Means Clustering]] |
| Binary selection problem | Integer programming | [[Methodology/MILP Optimization]] |
| Individual stats miss chemistry | Pairwise synergy modeling | [[Methodology/Synergy Modeling]] |

## Data Flow
```
Raw stats (3 seasons) → Feature Engineering → PCA → K-Means → Archetypes
                                                              ↓
Synergy (2-man lineups) ──────────────────────────→ MILP Optimizer → 10 Rosters
                                                              ↓
                                              Excel / HTML / PPTX / SQL / Tableau
```

## What Makes This Different from a Ranking
A ranking answers "who is best?" This answers "who should be on the team?"
Those are different questions. A team of 15 superstars might exceed the salary cap.
A team of 15 defenders might have no one to create offense.
The MILP optimizer enforces all constraints simultaneously and finds the true optimum.
""",

        "Feature Engineering.md": f"""---
type: methodology
tags: [methodology, features, engineering]
---

# Feature Engineering

## Raw Inputs
- **nba_master_threeyears.csv** — 3 seasons of per-game and advanced stats
- **nba_onoff.csv** — On/off court differentials from 5-man lineups

## Key Engineered Features

### Adjusted Ratings
Raw OFF_RATING and DEF_RATING are heavily influenced by team system.
A guard on a ball-dominant team will have a suppressed AST_PCT even if personally skilled.

**Team-context adjustment:**
- Compute each team's average OFF/DEF rating
- Subtract team baseline from player's rating
- Result: how much better/worse is this player vs their team's system

### VORPD (Value Over Replacement Per Dollar)
The core value metric. Answers: "How much production do you get per dollar of salary?"

```
VORPD = (Player Composite Score - Replacement Level Score) / Salary
```

High VORPD = underpaid relative to production (good target)
Low VORPD = overpaid relative to production (avoid)

### ON_OFF_DIFF
From 5-man lineup data: how does the team's net rating change when this player is on vs off?
Strong positive → player elevates teammates beyond their individual stats.

### IS_SHOOTER Flag
Binary: 1 if FG3_PCT > 0.36 AND 3PA per game > 3.0
Used as a hard constraint option in some optimization scenarios.

### SEASON_WEIGHT
Applied before aggregation across seasons:
- 2023-24 → 0.45
- 2022-23 → 0.35
- 2021-22 → 0.20

### COMPOSITE_SCORE_NORM
Final 0–100 player score. Combines:
- OFF_RATING_ADJUSTED (via PCA weights)
- DEF_RATING_ADJUSTED
- AST_PCT_ADJUSTED
- BLK, STL
- TS_PCT, FG3_PCT
- INFLUENCE_SCORE
- ON_OFF_DIFF
- VORPD

## Related Notes
- [[Methodology/PCA & Dimensionality Reduction]]
- [[Methodology/VORPD Explained]]
- [[Pipeline_Docs/01_Feature_Engineering]]
""",

        "PCA & Dimensionality Reduction.md": f"""---
type: methodology
tags: [methodology, PCA, statistics]
---

# PCA & Dimensionality Reduction

## The Problem It Solves
NBA player stats have massive multicollinearity. Players who score a lot also tend to
have high USG%, high SHOT_ATTEMPTS, high FGA — these all measure the same underlying
dimension (offensive workload). If you include all of them in a composite score,
you're triple-counting the same thing.

## What PCA Does
Principal Component Analysis finds the directions in the data that capture the
most variance — essentially, it finds the "real" underlying dimensions.

For NBA players, the main PCA components tend to capture:
- **PC1 (PCA_X):** Overall offensive contribution (high scorers, playmakers)
- **PC2 (PCA_Y):** Defensive vs perimeter orientation (rim protectors vs shooters)

## How It's Used Here
1. Standardize all 30+ stats (zero mean, unit variance)
2. Run PCA on the standardized data
3. Extract PC1 and PC2 as the clustering coordinates (PCA_X, PCA_Y in the data)
4. PC loadings → used as weights in the composite score (data-driven, not arbitrary)
5. Scree plot / elbow curve used to confirm 2 components capture most variance

## Why Not Just Use Raw Stats?
- 30+ correlated stats → weights become arbitrary
- PCA makes weights mathematically justified: they reflect actual data variance
- Bonus: 2D coordinates enable the visual cluster plot (see `charts/cluster_visualization.png`)

## PCA_X and PCA_Y in Player Notes
Every player note has PCA_X and PCA_Y coordinates. Players close together in PCA space
have similar overall statistical profiles, regardless of team or position label.

## Related Notes
- [[Methodology/K-Means Clustering]]
- [[Methodology/Feature Engineering]]
- [[Pipeline_Docs/01_Feature_Engineering]]
- [[Pipeline_Docs/02_Player_Clustering]]
""",

        "K-Means Clustering.md": f"""---
type: methodology
tags: [methodology, clustering, machine-learning]
---

# K-Means Clustering

## Purpose
Group the ~550 players into meaningful archetypes based on their statistical profiles.
Rather than using position labels (PG/SG/SF/PF/C — increasingly meaningless in modern NBA),
cluster by what players actually do statistically.

## Why K-Means
- Simple, interpretable, fast on this data size
- Works well on the 2D PCA coordinates
- Results are easy to visualize and validate
- Alternative considered: Bisecting K-Means (rejected — standard K-Means was sufficient)

## Choosing k=7
Used the **Elbow Method** — plot inertia (within-cluster sum of squares) vs k.
The "elbow" — where adding more clusters gives diminishing returns — appeared at k=7.

Below 7: archetypes too broad (all guards in one cluster)
Above 7: archetypes too granular (arbitrary splits within a type)

See: `charts/elbow_method.png`

## The 7 Archetypes

| Archetype | Basketball Profile | Key Stats |
|---|---|---|
| Elite Playmaker | Primary ball-handler, high usage, creates for others | High AST%, OFF_RATING, COMPOSITE_SCORE |
| Perimeter Scorer | Spot-up shooter, catch-and-shoot | High FG3_PCT, IS_SHOOTER=1 |
| Defensive Wing | Two-way, switchable | High STL+BLK, positive DEF_RATING |
| Stretch Big | Big with shooting range | High FG3_PCT, rim presence |
| Paint Anchor | Traditional big, interior | High BLK, negative PCA_X |
| Two-Way Guard | Guards on both ends | Balanced OFF/DEF rating |
| Role Player | Solid contributors, no dominant skill | Moderate across all |

## Manual Corrections (Step 03)
K-Means is domain-agnostic. ~15-20 players were manually reclassified because:
- A stretch big clustered with perimeter scorers (high FG3_PCT similarity)
- An elite playmaker clustered with two-way guards (defensive metrics similar)
Domain knowledge was applied to fix these edge cases.

## Random State
`random_state=42` set for reproducibility. K-Means++ initialization used.

## Related Notes
- [[Methodology/PCA & Dimensionality Reduction]]
- [[Archetypes/Elite Playmaker]]
- [[Pipeline_Docs/02_Player_Clustering]]
- [[Pipeline_Docs/03_Label_Corrections]]
""",

        "MILP Optimization.md": f"""---
type: methodology
tags: [methodology, optimization, MILP]
---

# Mixed-Integer Linear Programming (MILP)

## The Core Question
Given a pool of players with known composite scores and salaries, pick exactly 15
to maximize total team quality without violating any constraints.

## Why MILP (Not Just Ranking)
A simple ranking can't handle constraints simultaneously. MILP finds the globally
optimal solution under ALL constraints at once.

## Decision Variables
For each player i: **x[i] ∈ {{0, 1}}**
- x[i] = 1 → player is selected for the roster
- x[i] = 0 → player is not selected

## Objective Function
**Maximize:** Σ (COMPOSITE_SYNERGY[i] × x[i])

Where: `COMPOSITE_SYNERGY = COMPOSITE_SCORE_NORM + λ × NET_SYNERGY_PROFILE`
And λ = 0.05

## Hard Constraints

| Constraint | Formula | Why |
|---|---|---|
| Salary cap | Σ SALARY[i] × x[i] ≤ CAP | Real NBA rule |
| Roster size | Σ x[i] = 15 | NBA roster limit |
| Min per archetype | Σ x[i ∈ archetype] ≥ min_k | Prevent mono-archetype teams |
| Max per archetype | Σ x[i ∈ archetype] ≤ max_k | Force roster diversity |
| Binary | x[i] ∈ {{0, 1}} | Can't select half a player |

## The 10 Scenarios (A–J)

| Scenario | Cap | Strategic Focus |
|---|---|---|
| A | $165M | Balanced (no archetype constraints) |
| B | $136M | Value focus (high VORPD) |
| C | $90M | Budget efficiency |
| D | $165M | Defense first (min Defensive Wings) |
| E | $136M | Playmaker heavy |
| F | $136M | 3-and-D focus |
| G | $165M | Star + depth |
| H | $90M | Young core |
| I | $136M | Balanced synergy |
| J | $165M | Championship roster |

## Solver: PuLP + CBC
- PuLP = Python modeling interface
- CBC = open-source MILP solver (no license cost)
- Solves each scenario in < 5 seconds
- Guaranteed globally optimal solution (not heuristic)

## Why Scenario C Is Isolated in the Graph
At $90M, no expensive star player (salary > ~$20M) can be selected.
The 15 players chosen are completely different from any $136M or $165M scenario.
Zero shared players = no connecting links in the graph = isolated cluster.

## Related Notes
- [[Methodology/Synergy Modeling]]
- [[NBA_Context/Salary Cap Rules]]
- [[Pipeline_Docs/04_Expanded_Optimizer]]
- [[Pipeline_Docs/07_Synergy_Optimizer]]
- [[Scenarios/Scenario A]] → [[Scenarios/Scenario J]]
""",

        "Synergy Modeling.md": f"""---
type: methodology
tags: [methodology, synergy, lineup-analysis]
---

# Synergy Modeling

## The Problem Individual Stats Miss
Two players can each have excellent individual ratings but play poorly together.
Two players can have mediocre individual ratings but elevate each other dramatically.
Individual composite scores are blind to this.

## Data Source
**2-man lineup data** from Basketball Reference (2023-24 season only).
For every pair of players who shared court time, we have:
- Minutes together
- Offensive rating when both on court
- Defensive rating when both on court
- Net rating when both on court

## NET_SYNERGY Calculation
```
NET_SYNERGY[A,B] = NET_RATING[A+B on court]
                 - NET_RATING[A individual]
                 - NET_RATING[B individual]
```

Positive → the pair is better together than the sum of parts
Negative → the pair is worse together (redundant skills, ball-sharing issues)

## Data Quality Decisions

**50-minute threshold:** Pairs with < 50 shared minutes are excluded.
Reason: 10 minutes together with a ±20 net rating swing looks like huge synergy —
it's actually just variance.

**Archetype fallback:** If a pair has insufficient data, use the average synergy
for their archetype combination (e.g., Elite Playmaker + Defensive Wing average).

**Outlier capping:** Values beyond ±3 standard deviations are capped.

## NET_SYNERGY_PROFILE (Per Player)
Rather than storing all 1,661 pairs in the optimizer, each player gets a single
profile score: how well do they synergize with a "typical" roster?

```
NET_SYNERGY_PROFILE = 0.6 × DEF_SYNERGY + 0.4 × OFF_SYNERGY
```

Defensive synergy weighted higher because defense is more team-dependent than offense.

## Integration into Optimizer
```
COMPOSITE_SYNERGY = COMPOSITE_SCORE_NORM + 0.05 × NET_SYNERGY_PROFILE
```

λ = 0.05 → synergy is a tiebreaker, not dominant factor.
See [[Research_Log/Decisions/Lambda Weight Decision]]

## The 1,661 Synergy Pairs
Every pair with sufficient data has its own note in [[Synergy_Pairs/]].
Each pair note shows which players, their synergy scores, and their archetypes.
This is why the graph has an additional large cluster of connected dots.

## Related Notes
- [[Pipeline_Docs/05_Synergy_Computation]]
- [[Pipeline_Docs/06_Synergy_Validation]]
- [[Methodology/MILP Optimization]]
- [[NBA_Context/Lineup Analysis Basics]]
""",

        "VORPD Explained.md": f"""---
type: methodology
tags: [methodology, VORPD, value, salary]
---

# VORPD — Value Over Replacement Per Dollar

## What It Measures
The return on investment of a player's salary. Not just how good a player is,
but how good they are *relative to what you're paying*.

## Formula
```
VORPD = (Player Composite Score - Replacement Level) / Annual Salary
```

**Replacement Level** = the composite score of a league-average player on a minimum
contract (approximately the 50th percentile of composite scores).

## Why It Matters
A player with a 75 composite score on a $5M salary is more valuable to a
cap-constrained team than an 85 composite player on a $40M salary.

VORPD captures this. It's the metric that finds **undervalued players**.

## Examples
| Player Type | Composite | Salary | VORPD |
|---|---|---|---|
| Star on max | 91 | $35M | Low |
| Solid starter, underpaid | 68 | $4M | Very High |
| Veteran role player | 52 | $3M | Moderate |
| Overpaid veteran | 45 | $20M | Very Low |

## VORPD in Optimization
VORPD is not directly in the MILP objective (which maximizes COMPOSITE_SYNERGY).
But it's used in:
- **Scenario B** (Hard Cap - Value Focus): extra weight on high-VORPD players
- **Dashboard analysis**: "Best Value Players" filter (score > 60, salary < $15M)
- **Portfolio analysis**: identifying market inefficiencies

## Related Notes
- [[Methodology/Feature Engineering]]
- [[Methodology/MILP Optimization]]
- [[NBA_Context/Salary Cap Rules]]
- [[📊 Knowledge Base Dashboard]]
""",

        "Validation Framework.md": f"""---
type: methodology
tags: [methodology, validation, testing]
---

# Validation Framework

## Why Validation Matters
It's easy to build a model. It's hard to know if it's right.
This project uses multiple validation layers.

## Layer 1 — Face Validity
Does the model agree with basketball common sense?

- Are the top 10 composite scores recognizable stars? (SGA, Giannis, Luka, etc.)
- Do the archetypes map to recognizable player types?
- Are high-VORPD players actually known as "good value" in the industry?

If the model ranked role players above MVPs, something is wrong.

## Layer 2 — Statistical Validity
Does the composite score correlate with team winning?

- Pearson/Spearman correlation between average team composite score and team wins
- OLS regression of wins on composite score components
- R² should be meaningful (> 0.5) for the model to be defensible

## Layer 3 — Scenario Sanity
Do the optimization results make structural sense?

- Scenario C ($90M) has completely different players than A/B/D-J → expected
- Total salary in each scenario is ≤ its cap → verified
- All 15 roster slots are filled → verified
- No archetype composition constraints violated → verified
- The `09_verify_pipeline.py` script automates all these checks

## Layer 4 — Sensitivity Analysis
Are the results robust to small parameter changes?

- What if λ = 0.02 instead of 0.05? Do the top 10 players change much?
- What if season weights were equal (33/33/33) instead of 45/35/20? Big difference?
- Stable results = robust model

## Related Notes
- [[Pipeline_Docs/09_Pipeline_Verification]]
- [[Methodology/MILP Optimization]]
- [[Project_Story/Key Decisions Ledger]]
""",
    }

    for filename, content in notes.items():
        path = OUT / "Methodology" / filename
        path.write_text(content, encoding="utf-8")
        print(f"  Method: {filename}")


# ── 3. NBA CONTEXT NOTES ───────────────────────────────────────────────────

def write_nba_context():
    notes = {
        "Salary Cap Rules.md": f"""---
type: nba-context
tags: [nba, salary-cap, rules]
---

# NBA Salary Cap Rules

## The Three Tiers in This Project

| Tier | Amount | What It Means |
|---|---|---|
| Budget | $90M | Well below cap — rebuilding teams, tanking |
| Hard Cap | $136M | Approx 2023-24 salary cap — most playoff teams |
| Luxury Tax | $165M | Above luxury tax threshold — contenders |

## Real 2023-24 Numbers
- **Salary Cap:** $136.0M
- **Luxury Tax Line:** $165.3M
- **Hard Cap (Apron):** ~$179.5M
- **Minimum Salary:** ~$1.1M (veteran minimum)
- **Max Salary:** $35-40M+ depending on years of service

## Why Salary Cap Matters for Optimization
The salary cap is what makes roster building hard. Without it, you'd just sign
every top player. The cap forces trade-offs:
- 2 superstars at $35M each = $70M spent on 2 players, $66M for 13 more
- Or 1 superstar + 4 solid starters + 10 role players at similar cap usage

The optimizer finds the mathematically optimal trade-off.

## Key Concepts

**Luxury Tax:** Teams above the tax line pay a dollar-for-dollar penalty (or more)
to the league. Owners prefer to stay below this. Some ownership groups won't
allow crossing it — which is why the $136M hard cap scenario is realistic.

**Cap Space:** Money available before hitting the salary cap. Used to sign free agents.

**Mid-Level Exception (MLE):** Teams over the cap can still sign players using
the MLE (~$12.4M). Not modeled here but relevant in real team building.

**Bird Rights:** Teams can exceed the cap to re-sign their own players. Not modeled.

## Implication for Scenario C ($90M)
No NBA team in 2023-24 operated at $90M — this is a hypothetical "extreme budget"
scenario showing what the best possible roster looks like when you can only afford
minimum/near-minimum contracts. The player pool is completely different.

## Related Notes
- [[Methodology/MILP Optimization]]
- [[NBA_Context/Advanced Stats Glossary]]
- [[Scenarios/Scenario A]] through [[Scenarios/Scenario C]]
""",

        "Advanced Stats Glossary.md": f"""---
type: nba-context
tags: [nba, stats, glossary]
---

# Advanced Stats Glossary

Quick reference for every stat used in the optimizer.

## Ratings (Per 100 Possessions)

**OFF_RATING** — Points scored per 100 possessions when a player is on the court.
Higher = better offense. League average ~114.

**DEF_RATING** — Points allowed per 100 possessions when a player is on the court.
Lower = better defense. League average ~114.

**NET_RATING** — OFF_RATING minus DEF_RATING. The most concise single-number summary.
Positive = team outscores opponents when this player plays.

**ON_OFF_DIFF** — How much better/worse the team's net rating is with this player
on vs off the court. Isolates the player's marginal impact.

## Efficiency Stats

**TS% (True Shooting %)** — Points per shooting attempt, accounting for free throws
and 3-pointers. Better than FG% because it values efficiency over volume.
`TS% = PTS / (2 × (FGA + 0.44 × FTA))`

**FG3_PCT** — 3-point field goal percentage. Important for IS_SHOOTER classification.

## Usage & Creation

**USG_PCT (Usage Rate)** — Estimated % of team possessions used by player while on court.
High USG% = primary ball handler / shot creator. Low = off-ball role.

**AST_PCT** — % of teammate field goals a player assisted while on court.
High = playmaker / passer.

## Defense

**BLK (Blocks per game)** — Shot blocking. Indicator of rim protection.

**STL (Steals per game)** — Passing lane disruption. Indicator of active defense / anticipation.

## Composite / Value

**COMPOSITE_SCORE_NORM** — This project's 0-100 player quality score. PCA-weighted
combination of all above stats with recency weighting.

**VORPD** — Value Over Replacement Per Dollar. See [[Methodology/VORPD Explained]].

**INFLUENCE_SCORE** — Custom metric capturing a player's impact beyond their own stats.
Incorporates how teammates perform differently around them.

**NET_SYNERGY_PROFILE** — Player's average synergy with teammates based on 2-man lineup data.
See [[Methodology/Synergy Modeling]].

## Related Notes
- [[Methodology/Feature Engineering]]
- [[NBA_Context/Salary Cap Rules]]
- [[NBA_Context/Lineup Analysis Basics]]
""",

        "Lineup Analysis Basics.md": f"""---
type: nba-context
tags: [nba, lineups, analysis]
---

# Lineup Analysis Basics

## What Is Lineup Data?
Every NBA game tracks which 5 players are on the court at any moment.
"5-man lineup data" = stats for every unique combination of 5 players who played together.
"2-man lineup data" = stats for every pair of players who shared court time.

## Why Lineup Data Matters
Individual stats can be misleading. A player might have a great NET_RATING because
they always play with the team's best lineup. Or a poor NET_RATING because they're
the "break glass" option who plays garbage time.

Lineup data reveals the **interaction effects** — how players affect each other.

## How It's Used Here

**ON_OFF_DIFF (from 5-man data):**
Compare net rating of lineups with the player vs without.
Large positive → player dramatically improves team when on court.

**Pairwise Synergy (from 2-man data):**
For pairs with 50+ minutes together, compute how much better/worse the team is
with both on the court vs their individual contributions.
See [[Methodology/Synergy Modeling]].

## The Data Source
Basketball Reference publishes lineup splits for each season.
The `nba_lineups_2man.csv` file contains all 2-man pairs from 2023-24.
The `nba_onoff.csv` file contains 5-man on/off differentials.

## Limitations
- **Sample size:** A pair that played 15 minutes together has noisy data
- **Context:** Lineup data reflects who the coach chose to play together — not all
  potential combinations are observed
- **One season:** Synergy data only uses 2023-24 (most recent chemistry)

## Related Notes
- [[Methodology/Synergy Modeling]]
- [[Pipeline_Docs/05_Synergy_Computation]]
- [[NBA_Context/Advanced Stats Glossary]]
""",
    }

    for filename, content in notes.items():
        path = OUT / "NBA_Context" / filename
        path.write_text(content, encoding="utf-8")
        print(f"  Context: {filename}")


# ── 4. SYNERGY PAIR NOTES ──────────────────────────────────────────────────

def write_synergy_pairs():
    csv_path = BASE / "nba_synergy_2324.csv"
    if not csv_path.exists():
        print("  Skipping synergy pairs: nba_synergy_2324.csv not found")
        return

    df = pd.read_csv(csv_path)
    print(f"  Exporting {len(df)} synergy pair notes...")

    # Find the relevant columns
    cols = df.columns.tolist()

    # Try to identify player name columns
    name_cols = [c for c in cols if "NAME" in c.upper() or "PLAYER" in c.upper()]
    p1_col = name_cols[0] if len(name_cols) > 0 else cols[0]
    p2_col = name_cols[1] if len(name_cols) > 1 else cols[1]

    # Try to identify synergy score columns
    def_col = next((c for c in cols if "DEF" in c.upper() and "SYN" in c.upper()), None)
    off_col = next((c for c in cols if "OFF" in c.upper() and "SYN" in c.upper()), None)
    net_col = next((c for c in cols if "NET" in c.upper() and "SYN" in c.upper()), None)

    if not net_col:
        net_col = next((c for c in cols if "NET" in c.upper()), None)

    count = 0
    for _, row in df.iterrows():
        p1 = str(row[p1_col]).strip()
        p2 = str(row[p2_col]).strip()
        if not p1 or not p2 or p1 == "nan" or p2 == "nan":
            continue

        safe_p1 = p1.replace("/", "-").replace(":", "")
        safe_p2 = p2.replace("/", "-").replace(":", "")

        def get_val(col):
            if col and col in row.index:
                v = row[col]
                try:
                    return f"{float(v):.3f}"
                except Exception:
                    return str(v)
            return "N/A"

        net = get_val(net_col)
        def_s = get_val(def_col)
        off_s = get_val(off_col)

        try:
            net_float = float(net)
            if net_float > 1.5:
                rating = "Strong Positive"
            elif net_float > 0.3:
                rating = "Mild Positive"
            elif net_float < -1.5:
                rating = "Strong Negative"
            elif net_float < -0.3:
                rating = "Mild Negative"
            else:
                rating = "Neutral"
        except Exception:
            rating = "Unknown"

        frontmatter = f"""---
type: synergy-pair
player_1: "{p1}"
player_2: "{p2}"
net_synergy: {net}
def_synergy: {def_s}
off_synergy: {off_s}
rating: "{rating}"
tags: [synergy, pair]
---
"""
        body = f"""# {p1} + {p2}

| | |
|---|---|
| **Player 1** | [[Players/{safe_p1}]] |
| **Player 2** | [[Players/{safe_p2}]] |
| **Net Synergy** | {net} |
| **Def Synergy** | {def_s} |
| **Off Synergy** | {off_s} |
| **Rating** | {rating} |

_{rating}: these two players are {'better' if 'Positive' in rating else 'worse' if 'Negative' in rating else 'roughly the same'} together than their individual stats suggest._
"""
        filename = f"{safe_p1} + {safe_p2}.md"
        path = OUT / "Synergy_Pairs" / filename
        path.write_text(frontmatter + body, encoding="utf-8")
        count += 1

    print(f"  Done: {count} synergy pair notes -> NBA_Knowledge_Base/Synergy_Pairs/")


# ── 5. UPDATE DASHBOARD ────────────────────────────────────────────────────

def write_super_dashboard(df: pd.DataFrame):
    latest = df.sort_values("SEASON", ascending=False).drop_duplicates("PLAYER_ID", keep="first")
    arch_counts = latest["ARCHETYPE"].value_counts()
    arch_table = "\n".join(f"| {a} | {n} |" for a, n in arch_counts.items())

    content = f"""---
type: dashboard
tags: [index, dashboard, super-brain]
---

# NBA Optimizer Super Brain

> Complete knowledge base for the NBA Roster Optimization project.
> Built from {len(latest)} players across 3 seasons, 10 roster scenarios, and full project history.
> **Dataview plugin** required for live query tables.

---

## Navigate the Vault

| Section | What's Inside |
|---|---|
| [[Project_Story/Origin & Vision]] | Why this project exists, the learning journey |
| [[Project_Story/Key Decisions Ledger]] | Every major decision made during the project |
| [[Project_Story/Resume Framing]] | How to present this project for job applications |
| [[Project_Story/Technical Evolution]] | Phase-by-phase technical history |
| [[Pipeline_Docs/🏗️ Pipeline Overview]] | Full 9-step pipeline documentation |
| [[Methodology/Full Pipeline Overview]] | Methodology deep-dives |
| [[NBA_Context/Salary Cap Rules]] | NBA rules and financial context |
| [[NBA_Context/Advanced Stats Glossary]] | Every stat defined |
| [[Research_Log/📓 Research Index]] | Decision log, scout notes, templates |

---

## Quick Stats

| | |
|---|---|
| Unique Players | {len(latest)} |
| Player-Season Records | 1,185 |
| Synergy Pairs | 1,661 |
| Archetypes | {latest['ARCHETYPE'].nunique()} |
| Optimization Scenarios | 10 (A–J) |
| Pipeline Steps | 9 |
| Seasons | 2021-22, 2022-23, 2023-24 |
| Total Notes in Vault | ~3,400+ |

---

## Top 15 Players

```dataview
TABLE player, team, archetype, composite_score, salary
FROM "NBA_Knowledge_Base/Players"
SORT composite_score DESC
LIMIT 15
```

---

## Best Value (High Score, Low Salary)

```dataview
TABLE player, team, archetype, composite_score, salary, vorpd
FROM "NBA_Knowledge_Base/Players"
WHERE salary < 15000000 AND composite_score > 60
SORT composite_score DESC
LIMIT 15
```

---

## All Scenarios

```dataview
TABLE label, total_salary, avg_composite_score
FROM "NBA_Knowledge_Base/Scenarios"
SORT avg_composite_score DESC
```

---

## Strongest Synergy Pairs

```dataview
TABLE player_1, player_2, net_synergy, rating
FROM "NBA_Knowledge_Base/Synergy_Pairs"
SORT net_synergy DESC
LIMIT 20
```

---

## Worst Synergy Pairs

```dataview
TABLE player_1, player_2, net_synergy, rating
FROM "NBA_Knowledge_Base/Synergy_Pairs"
SORT net_synergy ASC
LIMIT 10
```

---

## Players by Archetype

| Archetype | Count |
|---|---|
{arch_table}

---

## Methodology Index

- [[Methodology/Full Pipeline Overview]]
- [[Methodology/Feature Engineering]]
- [[Methodology/PCA & Dimensionality Reduction]]
- [[Methodology/K-Means Clustering]]
- [[Methodology/MILP Optimization]]
- [[Methodology/Synergy Modeling]]
- [[Methodology/VORPD Explained]]
- [[Methodology/Validation Framework]]
"""
    path = OUT / "NBA Optimizer Super Brain.md"
    path.write_text(content, encoding="utf-8")
    print("  Done: NBA Optimizer Super Brain.md (master index)")


# ── MAIN ───────────────────────────────────────────────────────────────────

def main():
    print("=== Super Brain: Building Comprehensive Obsidian Vault ===")
    make_dirs()

    df = pd.read_csv(BASE / "nba_clustered.csv")

    print("\n[1/5] Project Story notes...")
    write_project_story()

    print("\n[2/5] Methodology deep-dive notes...")
    write_methodology_notes()

    print("\n[3/5] NBA Context notes...")
    write_nba_context()

    print("\n[4/5] Synergy pair notes (1,661 nodes)...")
    write_synergy_pairs()

    print("\n[5/5] Super Brain master dashboard...")
    write_super_dashboard(df)

    print("\nAll done! Refresh Obsidian to see the full super brain.")
    print("Total new notes: ~1,680+ (4 story + 8 methodology + 3 context + 1661 synergy pairs + 1 dashboard)")


if __name__ == "__main__":
    main()
