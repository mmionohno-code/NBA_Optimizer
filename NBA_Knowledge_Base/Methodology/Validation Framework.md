---
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
