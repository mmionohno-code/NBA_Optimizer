---
type: nba-context
tags: [nba, lineups, analysis]
---

# Lineup Analysis Basics

## What Is Lineup Data?
Every NBA game tracks which 5 players are on the court at any moment.
"5-man lineup data" = stats for every unique combination of 5 players who played together.
"2-man lineup data" = stats for every pair of players who shared court time.

## Why Lineup Data Matters
Individual stats can be misleading. A player might have a great NET_RATING because
they always play with the team's best lineup. Or a poor NET_RATING because they're
the "break glass" option who plays garbage time.

Lineup data reveals the **interaction effects** — how players affect each other.

## How It's Used Here

**ON_OFF_DIFF (from 5-man data):**
Compare net rating of lineups with the player vs without.
Large positive → player dramatically improves team when on court.

**Pairwise Synergy (from 2-man data):**
For pairs with 50+ minutes together, compute how much better/worse the team is
with both on the court vs their individual contributions.
See [[Methodology/Synergy Modeling]].

## The Data Source
Basketball Reference publishes lineup splits for each season.
The `nba_lineups_2man.csv` file contains all 2-man pairs from 2023-24.
The `nba_onoff.csv` file contains 5-man on/off differentials.

## Limitations
- **Sample size:** A pair that played 15 minutes together has noisy data
- **Context:** Lineup data reflects who the coach chose to play together — not all
  potential combinations are observed
- **One season:** Synergy data only uses 2023-24 (most recent chemistry)

## Related Notes
- [[Methodology/Synergy Modeling]]
- [[Pipeline_Docs/05_Synergy_Computation]]
- [[NBA_Context/Advanced Stats Glossary]]
