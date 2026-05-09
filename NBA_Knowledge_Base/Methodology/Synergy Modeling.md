---
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
