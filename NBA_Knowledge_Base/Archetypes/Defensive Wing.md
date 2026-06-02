---
archetype: "Defensive Wing"
player_count: 97
avg_composite_score: 35.16
avg_salary: 3753043
avg_off_rating_adj: -0.01
avg_def_rating_adj: 2.15
avg_vorpd: 9.14
tags: [archetype]
---
# Defensive Wing

> Two-way players with elite DEF_RATING. BLK + STL leaders.

## Archetype Summary

| Metric | Value |
|---|---|
| Total Players | 97 |
| Avg Composite Score | 35.2 |
| Avg Salary | $3,753,043 |
| Avg Off Rating Adj | -0.01 |
| Avg Def Rating Adj | 2.15 |
| Avg VORPD | 9.14 |

## Top 10 Players by Composite Score

| Player | Score | Salary | Team |
|---|---|---|---|
| [[Players/Tre Jones|Tre Jones]] | 62.5 | $7,039,195 | SAS |
| [[Players/Dennis Smith Jr.|Dennis Smith Jr.]] | 57.6 | $3,000,000 | BKN |
| [[Players/Eric Bledsoe|Eric Bledsoe]] | 56.8 | $925,258 | POR |
| [[Players/Ausar Thompson|Ausar Thompson]] | 52.5 | $7,721,117 | DET |
| [[Players/Tari Eason|Tari Eason]] | 52.2 | $4,994,103 | HOU |
| [[Players/Jose Alvarado|Jose Alvarado]] | 51.2 | $3,959,547 | NOP |
| [[Players/Hamidou Diallo|Hamidou Diallo]] | 51.0 | $1,017,781 | DET |
| [[Players/Jared Butler|Jared Butler]] | 50.4 | $2,019,706 | WAS |
| [[Players/Josh Hart|Josh Hart]] | 50.2 | $17,133,611 | NYK |
| [[Players/Max Strus|Max Strus]] | 47.8 | $14,022,474 | CLE |

## All Players (Dataview)

```dataview
TABLE composite_score, salary, team, season
FROM "NBA_Knowledge_Base/Players"
WHERE archetype = "Defensive Wing"
SORT composite_score DESC
```

## Synergy Notes

_How this archetype pairs with others — see [[📊 Knowledge Base Dashboard]] for cross-archetype synergy data._
