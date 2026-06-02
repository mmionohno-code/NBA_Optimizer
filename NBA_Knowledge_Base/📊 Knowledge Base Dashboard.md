---
type: dashboard
tags: [index, dashboard]
---

# 📊 NBA Knowledge Base Dashboard

> Auto-generated from project data. Navigate via the graph view or the Dataview tables below.
> **Dataview plugin required** for live queries — install it in Settings → Community Plugins.

---

## Quick Stats

| | |
|---|---|
| Total Players | 555 |
| Seasons Covered | 2021-22, 2022-23, 2023-24 |
| Optimization Scenarios | 10 (A–J) |
| Player Archetypes | 6 |

---

## Top 15 Players by Composite Score

```dataview
TABLE player, team, archetype, composite_score, salary
FROM "NBA_Knowledge_Base/Players"
SORT composite_score DESC
LIMIT 15
```

---

## Best Value Players (High Score, Low Salary)

```dataview
TABLE player, team, archetype, composite_score, salary
FROM "NBA_Knowledge_Base/Players"
WHERE salary < 15000000 AND composite_score > 60
SORT composite_score DESC
LIMIT 15
```

---

## Players by Archetype

| Archetype | Count |
|---|---|
| Bench / Role Player | 248 |
| Defensive Wing | 97 |
| Perimeter Scorer | 81 |
| Versatile Scorer | 55 |
| Elite Playmaker | 46 |
| Two-Way Big | 28 |

```dataview
TABLE player, composite_score, salary
FROM "NBA_Knowledge_Base/Players"
GROUP BY archetype
```

---

## All Scenarios

```dataview
TABLE label, total_salary, avg_composite_score, roster_size
FROM "NBA_Knowledge_Base/Scenarios"
SORT avg_composite_score DESC
```

---

## Archetypes Index

```dataview
TABLE avg_composite_score, avg_salary, player_count
FROM "NBA_Knowledge_Base/Archetypes"
SORT avg_composite_score DESC
```

---

## Navigation

- [[Archetypes/Elite Playmaker]] · [[Archetypes/Perimeter Scorer]] · [[Archetypes/Defensive Wing]]
- [[Archetypes/Stretch Big]] · [[Archetypes/Paint Anchor]] · [[Archetypes/Two-Way Guard]]
- [[Scenarios/Scenario A]] → [[Scenarios/Scenario J]]
