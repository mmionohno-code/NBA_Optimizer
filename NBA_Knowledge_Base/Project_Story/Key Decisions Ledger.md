---
type: project-story
tags: [story, decisions, ledger]
date: 2026-06-01
---

# Key Decisions Ledger

A chronological record of the most important choices made during the project.

---

## D01 — PCA over Arbitrary Weights
**Decision:** Use PCA to derive composite score weights from data, not intuition.
**Why:** Arbitrary weights (25% NET_RATING etc.) are indefensible in an interview.
PCA lets the data reveal which dimensions of performance actually vary together.
**Impact:** The composite score became statistically grounded and reproducible.
**See:** [[Methodology/PCA & Dimensionality Reduction]]

---

## D02 — 3 Seasons, Not 1
**Decision:** Use 2021-22, 2022-23, 2023-24 data with recency weighting.
**Why:** Single-season stats have high variance. A player who got injured in December
looks terrible on a full-season split. Three seasons reduces noise.
**Weights:** 45% (2023-24), 35% (2022-23), 20% (2021-22)
**Impact:** More stable composite scores, especially for veterans.

---

## D03 — K-Means with k=7
**Decision:** 7 archetypes via K-Means, validated with elbow method.
**Why:** k=7 was the inflection point on the elbow curve. Below 7, archetypes were
too broad (e.g. all guards in one cluster). Above 7, clusters became too granular.
**See:** [[Methodology/K-Means Clustering]]

---

## D04 — Manual Label Corrections (Step 03)
**Decision:** Add a manual override step after K-Means.
**Why:** K-Means is mathematically agnostic to basketball domain knowledge.
A stretch big with elite 3P% might cluster with perimeter scorers purely on that stat.
Domain knowledge matters here.
**Impact:** ~15-20 players were reclassified to more accurate archetypes.

---

## D05 — CBC Solver via PuLP
**Decision:** Use open-source CBC solver, not Gurobi or CPLEX.
**Why:** Gurobi requires a paid license. CBC is free, handles our problem size easily
(~500 players, 15-player selection), and produces optimal solutions in seconds.
**Impact:** Anyone can run this project without purchasing software.

---

## D06 — 50-Minute Synergy Threshold
**Decision:** Require minimum 50 shared minutes for a synergy pair to count.
**Why:** With fewer shared minutes, the NET_SYNERGY estimate is too noisy.
A pair that played 10 minutes together and happened to outscore opponents by 20 points
looks like incredible synergy — it's just small-sample variance.
**Impact:** Cleaner synergy data; sparse pairs fall back to archetype averages.

---

## D07 — λ = 0.05 Synergy Weight
**Decision:** Synergy contributes 5% uplift to composite score in the optimizer.
**Why:** Synergy is real but secondary to individual ability. At λ=0.05, a player with
a 91.0 composite + excellent synergy can edge out a 91.4 player with poor synergy —
but a clearly superior player is never bumped by a mediocre one.
**See:** [[Research_Log/Decisions/Lambda Weight Decision]]

---

## D08 — 10 Scenarios (A–J), Not 3
**Decision:** Expand from 3 to 10 optimization scenarios.
**Why:** 3 scenarios (hard cap / luxury / budget) only varies the salary constraint.
10 scenarios also vary the strategic objective: defense-first, playmaker-heavy,
3-and-D focus, star+depth, young core, championship roster.
**Impact:** Much richer comparison surface. Scenario C's isolation in the graph view
is visible proof that the $90M budget world is categorically different.

---

## D09 — Season Weights in Composite Score
**Decision:** Apply SEASON_WEIGHT as a multiplier before aggregating across seasons.
**Why:** A player's 2021-22 performance is less predictive of future performance than
their 2023-24 performance. Weighting prevents old data from dragging down improving players.
**Impact:** Young players on upward trajectories score higher than their 3-year average
would suggest.

---

## Related Notes
- [[Project_Story/Origin & Vision]]
- [[Project_Story/Technical Evolution]]
- [[Research_Log/Decisions/Lambda Weight Decision]]
