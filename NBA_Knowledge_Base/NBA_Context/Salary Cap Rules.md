---
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
