---
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
