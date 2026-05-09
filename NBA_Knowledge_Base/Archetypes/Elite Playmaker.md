---
archetype: "Elite Playmaker"
player_count: 45
avg_composite_score: 70.69
avg_salary: 31803636
avg_off_rating_adj: 3.45
avg_def_rating_adj: -0.33
avg_vorpd: 2.50
tags: [archetype]
---
# Elite Playmaker

> High-usage primary ball-handlers who create offense. Top AST%, high COMPOSITE_SCORE.

## Archetype Summary

| Metric | Value |
|---|---|
| Total Players | 45 |
| Avg Composite Score | 70.7 |
| Avg Salary | $31,803,636 |
| Avg Off Rating Adj | 3.45 |
| Avg Def Rating Adj | -0.33 |
| Avg VORPD | 2.50 |

## Top 10 Players by Composite Score

| Player | Score | Salary | Team |
|---|---|---|---|
| [[Players/Nikola Jokić|Nikola Jokić]] | 95.9 | $48,592,024 | DEN |
| [[Players/Shai Gilgeous-Alexander|Shai Gilgeous-Alexander]] | 91.4 | $33,729,226 | OKC |
| [[Players/Luka Dončić|Luka Dončić]] | 90.4 | $40,475,071 | DAL |
| [[Players/Joel Embiid|Joel Embiid]] | 86.6 | $48,592,024 | PHI |
| [[Players/LaMelo Ball|LaMelo Ball]] | 84.0 | $33,399,888 | CHA |
| [[Players/Ja Morant|Ja Morant]] | 83.1 | $31,553,147 | MEM |
| [[Players/Giannis Antetokounmpo|Giannis Antetokounmpo]] | 83.1 | $47,625,828 | MIL |
| [[Players/Donovan Mitchell|Donovan Mitchell]] | 82.0 | $40,822,138 | CLE |
| [[Players/De'Aaron Fox|De'Aaron Fox]] | 81.7 | $32,641,292 | SAC |
| [[Players/Tyrese Haliburton|Tyrese Haliburton]] | 81.0 | $40,079,866 | IND |

## All Players (Dataview)

```dataview
TABLE composite_score, salary, team, season
FROM "NBA_Knowledge_Base/Players"
WHERE archetype = "Elite Playmaker"
SORT composite_score DESC
```

## Synergy Notes

_How this archetype pairs with others — see [[📊 Knowledge Base Dashboard]] for cross-archetype synergy data._
