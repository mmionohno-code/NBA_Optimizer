---
archetype: "Elite Playmaker"
player_count: 46
avg_composite_score: 63.94
avg_salary: 32866111
avg_off_rating_adj: 2.76
avg_def_rating_adj: -0.58
avg_vorpd: 2.27
tags: [archetype]
---
# Elite Playmaker

> High-usage primary ball-handlers who create offense. Top AST%, high COMPOSITE_SCORE.

## Archetype Summary

| Metric | Value |
|---|---|
| Total Players | 46 |
| Avg Composite Score | 63.9 |
| Avg Salary | $32,866,111 |
| Avg Off Rating Adj | 2.76 |
| Avg Def Rating Adj | -0.58 |
| Avg VORPD | 2.27 |

## Top 10 Players by Composite Score

| Player | Score | Salary | Team |
|---|---|---|---|
| [[Players/Nikola Jokić|Nikola Jokić]] | 96.3 | $48,592,024 | DEN |
| [[Players/Shai Gilgeous-Alexander|Shai Gilgeous-Alexander]] | 89.0 | $33,729,226 | OKC |
| [[Players/Luka Dončić|Luka Dončić]] | 87.5 | $40,475,071 | DAL |
| [[Players/Ja Morant|Ja Morant]] | 82.1 | $31,553,147 | MEM |
| [[Players/Giannis Antetokounmpo|Giannis Antetokounmpo]] | 81.5 | $47,625,828 | MIL |
| [[Players/Joel Embiid|Joel Embiid]] | 79.8 | $48,592,024 | PHI |
| [[Players/Tyrese Haliburton|Tyrese Haliburton]] | 78.2 | $40,079,866 | IND |
| [[Players/De'Aaron Fox|De'Aaron Fox]] | 77.3 | $32,641,292 | SAC |
| [[Players/Donovan Mitchell|Donovan Mitchell]] | 76.7 | $40,822,138 | CLE |
| [[Players/Jalen Brunson|Jalen Brunson]] | 76.6 | $30,747,204 | NYK |

## All Players (Dataview)

```dataview
TABLE composite_score, salary, team, season
FROM "NBA_Knowledge_Base/Players"
WHERE archetype = "Elite Playmaker"
SORT composite_score DESC
```

## Synergy Notes

_How this archetype pairs with others — see [[📊 Knowledge Base Dashboard]] for cross-archetype synergy data._
