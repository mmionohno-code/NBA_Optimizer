---
type: dashboard
tags: [index, dashboard, super-brain]
---

# NBA Optimizer Super Brain

> Complete knowledge base for the NBA Roster Optimization project.
> Built from 551 players across 3 seasons, 10 roster scenarios, and full project history.
> **Dataview plugin** required for live query tables.

---

## Navigate the Vault

| Section | What's Inside |
|---|---|
| [[Project_Story/Origin & Vision]] | Why this project exists, the learning journey |
| [[Project_Story/Key Decisions Ledger]] | Every major decision made during the project |
| [[Project_Story/Resume Framing]] | How to present this project for job applications |
| [[Project_Story/Technical Evolution]] | Phase-by-phase technical history |
| [[Pipeline_Docs/🏗️ Pipeline Overview]] | Full 9-step pipeline documentation |
| [[Methodology/Full Pipeline Overview]] | Methodology deep-dives |
| [[NBA_Context/Salary Cap Rules]] | NBA rules and financial context |
| [[NBA_Context/Advanced Stats Glossary]] | Every stat defined |
| [[Research_Log/📓 Research Index]] | Decision log, scout notes, templates |

---

## Quick Stats

| | |
|---|---|
| Unique Players | 551 |
| Player-Season Records | 1,185 |
| Synergy Pairs | 1,661 |
| Archetypes | 6 |
| Optimization Scenarios | 10 (A–J) |
| Pipeline Steps | 9 |
| Seasons | 2021-22, 2022-23, 2023-24 |
| Total Notes in Vault | ~3,400+ |

---

## Top 15 Players

```dataview
TABLE player, team, archetype, composite_score, salary
FROM "NBA_Knowledge_Base/Players"
SORT composite_score DESC
LIMIT 15
```

---

## Best Value (High Score, Low Salary)

```dataview
TABLE player, team, archetype, composite_score, salary, vorpd
FROM "NBA_Knowledge_Base/Players"
WHERE salary < 15000000 AND composite_score > 60
SORT composite_score DESC
LIMIT 15
```

---

## All Scenarios

```dataview
TABLE label, total_salary, avg_composite_score
FROM "NBA_Knowledge_Base/Scenarios"
SORT avg_composite_score DESC
```

---

## Strongest Synergy Pairs

```dataview
TABLE player_1, player_2, net_synergy, rating
FROM "NBA_Knowledge_Base/Synergy_Pairs"
SORT net_synergy DESC
LIMIT 20
```

---

## Worst Synergy Pairs

```dataview
TABLE player_1, player_2, net_synergy, rating
FROM "NBA_Knowledge_Base/Synergy_Pairs"
SORT net_synergy ASC
LIMIT 10
```

---

## Players by Archetype

| Archetype | Count |
|---|---|
| Bench / Role Player | 237 |
| Perimeter Scorer | 87 |
| Defensive Wing | 86 |
| Versatile Scorer | 68 |
| Elite Playmaker | 45 |
| Two-Way Big | 28 |

---

## Methodology Index

- [[Methodology/Full Pipeline Overview]]
- [[Methodology/Feature Engineering]]
- [[Methodology/PCA & Dimensionality Reduction]]
- [[Methodology/K-Means Clustering]]
- [[Methodology/MILP Optimization]]
- [[Methodology/Synergy Modeling]]
- [[Methodology/VORPD Explained]]
- [[Methodology/Validation Framework]]
