---
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
