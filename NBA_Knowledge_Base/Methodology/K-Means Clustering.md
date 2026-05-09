---
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
