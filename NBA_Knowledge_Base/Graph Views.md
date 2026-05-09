---
type: graph-guide
tags: [guide, navigation]
---

# Graph Views Cheatsheet

Open the **Graph view** (left sidebar globe icon, or `Ctrl+G`), click the **Filters** dropdown at the top of the panel, and paste any of these strings into the search box. Each gives you a different "lens" on the same vault.

---

## Default View (already set)

```
-path:Synergy_Pairs -path:Players/Seasons
```

Hides the 1,661 synergy pair dots and the 1,185 season sub-notes. You see the **clean skeleton**: Players, Archetypes, Scenarios, Methodology, Pipeline, Story.

---

## Executive View — minimum noise

```
-path:Synergy_Pairs -path:Players/Seasons -path:Players
```

Drops players entirely. Just the **conceptual map**: Archetypes ↔ Scenarios ↔ Methodology ↔ Pipeline. Useful for showing the project shape to someone in 5 seconds.

---

## Roster View — who plays where

```
-path:Synergy_Pairs -path:Players/Seasons -path:Methodology -path:Pipeline_Docs -path:Research_Log -path:NBA_Context -path:Project_Story
```

Just **Players + Archetypes + Scenarios**. The "who's on what team" view.

---

## Synergy Web — chemistry only

```
path:Synergy_Pairs OR path:Players
```

Shows the synergy pairs and the players they connect. **Dense and beautiful** — best zoomed in on a single player to see their chemistry web.

---

## Player Career View

```
path:Players/Seasons OR path:Players
```

Shows each player connected to their year-by-year season notes. Good for tracking individual player **trajectories**.

---

## Methodology / Pipeline Deep Dive

```
path:Methodology OR path:Pipeline_Docs OR path:Project_Story
```

Just the **explanation layer** — how the system works. Useful when writing about the project.

---

## Scenario Comparison

```
path:Scenarios OR path:Players
```

All 10 scenarios and the players they pull in. Look for **hub players** appearing across multiple scenarios.

---

## Reset to See Everything

Clear the search box (delete all text). Warning: ~3,500 nodes will render. Slow but spectacular.

---

## Pro Tips

- **Local Graph** (`Ctrl+Shift+G` while inside any note) shows only nodes within a few hops of the current note — perfect for exploring one player's connections without the chaos.
- The **depth slider** in the local graph controls how many hops out to show (1 = direct neighbors only).
- Color groups are already set in graph settings — each note type has its own vibrant color.
