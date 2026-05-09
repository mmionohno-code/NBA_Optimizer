---
type: decision
date: 2026-05-08
status: "accepted"
area: "modeling"
tags: [decision, modeling, synergy]
---

# Decision: Synergy Weight (λ = 0.05)

**Date:** 2026-05-08
**Area:** Modeling
**Status:** Accepted

---

## Context

After computing NET_SYNERGY_PROFILE scores in step 06, needed to decide how heavily
synergy should influence the optimizer's objective function vs raw COMPOSITE_SCORE_NORM.

## Options Considered

1. **λ = 0.0** — Pure composite score, ignore synergy entirely
2. **λ = 0.05** — Synergy adds up to ~5% uplift (chosen)
3. **λ = 0.20** — Heavy synergy weighting, risk of dropping high-composite players

## Decision

**λ = 0.05** — Synergy acts as a tiebreaker between similarly-scored players.
At this level, a player with a 91.0 composite + top synergy profile (~+0.9) can
edge out a 91.4 composite player with negative synergy (-0.8), but a clearly
superior player is never bumped by a mediocre one.

## Consequences

- **Positive:** Rosters feel more "coherent" archetypally. Fewer jarring pair conflicts.
- **Negative / Risk:** Synergy data is sparse (50-min threshold). Could amplify noise.

## Outcome Measurement

Compare scenario avg scores with λ=0.0 vs λ=0.05. If avg score drops >1.5 points
while archetype diversity improves, consider reducing λ.

## Related Notes

- [[05_compute_synergy]]
- [[07_optimizer_synergy]]
- [[Research Index]]
