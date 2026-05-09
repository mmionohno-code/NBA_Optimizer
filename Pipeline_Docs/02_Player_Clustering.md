---
step: 02
name: "Player Clustering"
script: "02_clustering.py"
status: "completed"
tags: [pipeline, step-02]
---

# Step 02: Player Clustering

← [[01_Feature_Engineering]] | → [[03_Label_Corrections]]

**Script:** `02_clustering.py`

---

## What This Step Does

Clusters all players into 7 archetypes using K-means on the PCA-reduced feature space. The elbow method (see charts/elbow_method.png) guided the choice of k=7. Each player is assigned a CLUSTER integer (0-6) and an ARCHETYPE label string. Clustering runs on standardized features to prevent salary-scale dominance.

---

## Inputs

  - `nba_scored_complete.csv`

## Outputs

  - `nba_clustered.csv`

---

## Key Decisions & Parameters

  - k=7 chosen via elbow method — balances granularity with interpretability
  - Clustering on PCA components, not raw stats (avoids multicollinearity)
  - Random state fixed (seed=42) for reproducibility
  - K-means initialized with k-means++ for better convergence

---

## Feeds Into

  - [[03_fix_labels]]

---

## Change Log

| Date | Change | Why |
|---|---|---|
| 2026-05-08 | Initial pipeline run | — |

## Notes

_Add notes about any modifications, experiments, or issues here._
