---
type: project-story
tags: [story, resume, career]
date: 2026-06-01
---

# Resume Framing Guide

How to present each part of this project for different audiences.

---

## One-Line Summary

> *Built end-to-end NBA roster optimization system using PCA, K-Means clustering, and
> MILP solver — 551 players, 7 archetypes, 10 salary cap scenarios, multi-format reporting.*

---

## For a Data Science / Analytics Role

**Bullet points:**
- Engineered composite player scoring system from 3 seasons of NBA data using PCA-derived
  weights, Bayesian shrinkage, and team-context adjustments
- Clustered 551 players into 7 archetypes using K-Means on PCA-reduced features (k selected
  via elbow method); validated against domain knowledge with manual corrections
- Modeled pairwise player synergy from 2-man lineup data (1,661 pairs); incorporated as
  λ=0.05 objective weight in MILP optimizer
- Generated 10 roster scenarios across 3 salary cap tiers ($90M / $136M / $165M) using
  PuLP/CBC solver with binary decision variables and archetype composition constraints

**Skills to highlight:** PCA, K-Means, MILP, pandas, scikit-learn, PuLP, SQLite, multi-format delivery

---

## For a Sports Analytics Role

**Bullet points:**
- Developed NBA salary cap optimization model combining advanced stats (VORPD, ON/OFF
  differential, adjusted offensive/defensive ratings) with player chemistry modeling
- Applied recency-weighted multi-season framework (45/35/20% across 3 years) with
  team-context adjustments to isolate player contribution from system effects
- Identified value inefficiencies: high-VORPD, low-salary players underweighted by
  market but captured by optimization model

**Skills to highlight:** Advanced stats, salary cap modeling, VORPD, lineup analysis, synergy

---

## For a General Analyst / Business Intelligence Role

**Bullet points:**
- Built automated analytics pipeline processing 1,200+ player-season records into
  actionable roster recommendations, with deliverables in Excel, HTML, PowerPoint, and Tableau
- Designed SQLite database with 20+ analytical views for ad-hoc querying; created
  Obsidian knowledge base with 1,750+ linked notes for self-documenting analytics

**Skills to highlight:** Excel, Tableau, SQL, dashboard design, data storytelling

---

## Interview Story Arc

1. **Hook:** "I wanted a project that combined statistics and optimization — two things
   that sound abstract but have very concrete answers in basketball."
2. **Problem:** "The hard part isn't ranking players. Everyone has a ranking. The hard
   part is building a *team* under real financial constraints."
3. **Rigor moment:** "The first version used arbitrary weights. I threw it out and rebuilt
   it with PCA — let the data tell me which stats actually matter."
4. **Result:** "The optimizer consistently finds value players the market underprices.
   Scenario C — the $90M budget roster — has zero overlap with any other scenario, which
   means the $90M world is a genuinely different player market."
5. **Scale:** "551 unique players, 1,185 player-season records, 1,661 synergy pairs,
   10 optimized rosters — all documented in a linked knowledge base."

---

## Related Notes
- [[Project_Story/Origin & Vision]]
- [[Project_Story/Key Decisions Ledger]]
- [[NBA_Context/Salary Cap Rules]]
