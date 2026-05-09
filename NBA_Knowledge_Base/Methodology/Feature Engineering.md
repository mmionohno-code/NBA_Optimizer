---
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
