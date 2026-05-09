---
type: project-story
tags: [story, origin, vision]
date: 2026-05-08
---

# The Origin Story

## Why This Project Exists

This project started as a resume builder — a way to demonstrate real data science skills
to employers using a domain (basketball) that's both interesting and analytically rich.

The core question: *"Given an NBA salary cap and a pool of players, which 15-player roster
maximizes team quality?"* It's a deceptively hard problem that touches machine learning,
optimization, and sports analytics simultaneously.

## The Journey: Zero to Data Scientist

The project was built from absolute scratch:

- **No prior programming experience** when this started
- Learned Python installation, VS Code setup, library management, and debugging all from scratch
- Every error message was a new learning moment — PATH variables, virtual environments, admin mode
- The Python 3.14 installation alone took a full debugging session

That journey is part of what makes this project compelling on a resume — it wasn't handed over,
it was built line by line.

## The Pivot to Statistical Rigor

An early version used **arbitrary weights** for the composite score:
- 25% NET_RATING, 20% PIE, etc.

The decision was made to reject this and insist on **data-driven weights** instead:
1. Correlation analysis to find which stats actually predict winning
2. PCA to let the data determine the weights mathematically
3. Validation against real 2023-24 MVP and standings outcomes
4. Sensitivity analysis to prove robustness

This pivot is one of the most important decisions in the project. It's the difference between
a project that "looks analytical" and one that **is** analytical.

## The Scope Creep (Good Kind)

What started as "optimize a roster" expanded into:
- 3 seasons of data instead of 1 (2021-22, 2022-23, 2023-24)
- Synergy modeling from 2-man lineup data
- 10 optimization scenarios instead of 3
- SQLite database with views
- Interactive HTML dashboard
- PowerPoint presentation
- Tableau export
- Obsidian knowledge base (this vault)

Each addition made the project more complete and more defensible in a job interview.

## Related Notes
- [[Project_Story/Technical Evolution]]
- [[Project_Story/Key Decisions Ledger]]
- [[Project_Story/Resume Framing]]
- [[Methodology/Full Pipeline Overview]]
