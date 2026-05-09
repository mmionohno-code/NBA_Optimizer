---
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
