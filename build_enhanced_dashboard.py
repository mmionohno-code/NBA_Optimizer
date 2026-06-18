#!/usr/bin/env python3
"""
Build the elegant Minho Moon NBA Optimizer dashboard.

Front page = full-viewport 3D knowledge graph (Obsidian-style),
overlaid with the title, MM branding, stats, and graph controls.
Subsequent sections reveal with 3D scroll transitions.
"""

import pandas as pd
import json
import re
from pathlib import Path

BASE = Path(__file__).parent
INPUT_HTML  = BASE / "NBA_Interactive_Dashboard.html"
OUTPUT_HTML = BASE / "NBA_Enhanced_Dashboard.html"

# ── ARCHETYPE COLOR MAP ────────────────────────────────────────────────
ARCH_COLORS = {
    "Elite Playmaker":     "#C9A84C",
    "Defensive Wing":      "#06B6D4",
    "Perimeter Scorer":    "#3B82F6",
    "Versatile Scorer":    "#A855F7",
    "Two-Way Big":         "#10B981",
    "Bench / Role Player": "#F97316",
}

# ── LOAD DATA ──────────────────────────────────────────────────────────
print("Loading player data...")
players_df = pd.read_csv(BASE / "nba_clustered.csv")
players_24 = players_df[players_df["SEASON"] == "2023-24"].copy()

# Take ALL 2023-24 players who have an archetype assigned
top_players = (
    players_24
    [["PLAYER_NAME","PLAYER_ID","ARCHETYPE","COMPOSITE_SCORE_NORM","SALARY","TEAM_ABBREVIATION"]]
    .dropna(subset=["PLAYER_NAME","ARCHETYPE"])
    .drop_duplicates("PLAYER_NAME")
    .sort_values("COMPOSITE_SCORE_NORM", ascending=False)
    .reset_index(drop=True)
)
print(f"  {len(top_players)} unique players (full 2023-24 rotation)")

print("Loading synergy data...")
synergy_df = pd.read_csv(BASE / "nba_synergy_2324.csv")
# Keep edge count bounded: only meaningful synergies between players who logged real minutes
high_syn = synergy_df[
    (synergy_df["NET_SYNERGY"].abs() > 0.75) &
    (synergy_df["MIN"] > 400)
].copy()

# ── BUILD GRAPH JSON ───────────────────────────────────────────────────
nodes, links = [], []
pid_to_nid = {}

# Archetype hub nodes (larger, more visible)
for arch, color in ARCH_COLORS.items():
    nodes.append({
        "id": f"arch::{arch}", "name": arch,
        "type": "archetype", "color": color,
        "val": 60, "group": arch,
    })

# Player nodes
for _, row in top_players.iterrows():
    pid  = int(row["PLAYER_ID"])
    nid  = f"p::{pid}"
    pid_to_nid[pid] = nid
    arch  = row["ARCHETYPE"]
    score = float(row["COMPOSITE_SCORE_NORM"])
    nodes.append({
        "id": nid, "name": row["PLAYER_NAME"],
        "type": "player",
        "color": ARCH_COLORS.get(arch, "#888"),
        "val": max(5, min(20, score / 5)),
        "group": arch, "score": round(score, 1),
        "team": str(row["TEAM_ABBREVIATION"]),
        "salary": int(row["SALARY"]) if pd.notna(row["SALARY"]) else 0,
    })
    links.append({
        "source": nid, "target": f"arch::{arch}",
        "color": "rgba(255,255,255,0.04)", "synergy": 0,
    })

# Player-player synergy edges
seen = set()
for _, row in high_syn.iterrows():
    a, b = int(row["PLAYER_A_ID"]), int(row["PLAYER_B_ID"])
    if a not in pid_to_nid or b not in pid_to_nid:
        continue
    key = (min(a, b), max(a, b))
    if key in seen:
        continue
    seen.add(key)
    syn = float(row["NET_SYNERGY"])
    alpha = min(0.85, 0.15 + abs(syn) * 0.10)
    color = f"rgba(16,185,129,{alpha:.2f})" if syn > 0 else f"rgba(239,68,68,{alpha:.2f})"
    links.append({
        "source": pid_to_nid[a], "target": pid_to_nid[b],
        "color": color, "synergy": round(syn, 2),
    })

GRAPH_DATA_JS = json.dumps({"nodes": nodes, "links": links}, separators=(",", ":"))
print(f"  Graph: {len(nodes)} nodes, {len(links)} links")

# ══════════════════════════════════════════════════════════════════════
# CSS — Elegant design layer
# ══════════════════════════════════════════════════════════════════════
EXTRA_CSS = r"""
        /* ════════════════════════════════════════════════════
           MINHO MOON  ·  Elegant Design Layer (Black & Gold)
           ════════════════════════════════════════════════════ */

        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400&display=swap');

        /* Override base palette: deep black + gold (luxury aesthetic) */
        :root {
            --navy:        #050505;
            --navy-mid:    #0a0a0a;
            --navy-light:  #141414;
            --surface:     #080808;
            --surface-card: rgba(14,14,14,0.72);
            --border:      rgba(201,168,76,0.18);
            --gold-dim:    rgba(201,168,76,0.10);
        }
        body { background: #030303; }

        html { scroll-behavior: smooth; scrollbar-width: thin; scrollbar-color: var(--gold) #000; }
        ::-webkit-scrollbar        { width: 3px; }
        ::-webkit-scrollbar-track  { background: #000; }
        ::-webkit-scrollbar-thumb  { background: var(--gold); border-radius: 2px; }

        body {
            perspective: 1600px;
            perspective-origin: 50% 30%;
        }

        /* ════════════════════════════════════
           HERO  ·  Full-viewport 3D graph
           ════════════════════════════════════ */
        .hero {
            height: 100vh;
            min-height: 720px;
            padding: 0;
            position: relative;
            overflow: hidden;
            background: radial-gradient(ellipse 100% 80% at 50% 50%, #0d0d0d 0%, #050505 60%, #000 100%);
            border-bottom: 1px solid rgba(201,168,76,0.18);
        }
        .hero::before {
            content: '';
            position: absolute; inset: 0;
            background: url("data:image/svg+xml,%3Csvg width='80' height='80' xmlns='http://www.w3.org/2000/svg'%3E%3Ccircle cx='40' cy='40' r='0.6' fill='%23c9a84c' fill-opacity='0.05'/%3E%3C/svg%3E");
            pointer-events: none; z-index: 1;
        }
        .hero::after {
            /* vignette */
            content: '';
            position: absolute; inset: 0;
            background:
                radial-gradient(ellipse 60% 50% at 50% 50%, transparent 0%, rgba(0,0,0,0.55) 100%),
                linear-gradient(180deg, rgba(0,0,0,0.45) 0%, transparent 25%, transparent 70%, rgba(0,0,0,0.85) 100%);
            pointer-events: none; z-index: 2;
        }

        /* 3D graph fills the hero as background */
        #hero-graph-bg {
            position: absolute;
            inset: 0;
            z-index: 1;
            cursor: grab;
            opacity: 0;
            transition: opacity 1.4s ease;
        }
        #hero-graph-bg.ready { opacity: 1; }
        #hero-graph-bg:active { cursor: grabbing; }

        /* Hero overlay (text + UI on top of graph) */
        .hero-overlay {
            position: relative;
            z-index: 5;
            height: 100%;
            width: 100%;
            display: grid;
            grid-template-rows: auto 1fr auto;
            padding: 56px 80px 36px;
            pointer-events: none;
        }
        .hero-overlay > * { pointer-events: auto; }

        /* Top bar — badge + MM brand */
        .hero-top {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }
        .mm-brand {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 4px;
            user-select: none;
        }
        .mm-monogram {
            font-family: 'Cormorant Garamond', serif;
            font-size: 54px; font-weight: 300; line-height: 1;
            color: rgba(201,168,76,0.7);
            letter-spacing: 8px;
            text-shadow: 0 0 24px rgba(201,168,76,0.25);
        }
        .mm-name {
            font-size: 10px; font-weight: 600; letter-spacing: 5px;
            text-transform: uppercase; color: rgba(201,168,76,0.65);
        }

        /* Center — main title & stats */
        .hero-center {
            align-self: center;
            max-width: 640px;
        }
        .hero-badge {
            display: inline-flex; align-items: center; gap: 8px;
            background: rgba(10,10,10,0.55); backdrop-filter: blur(20px);
            border: 1px solid rgba(201,168,76,0.3); border-radius: 100px;
            padding: 7px 18px; font-size: 11px; font-weight: 600;
            color: var(--gold); letter-spacing: 2px; text-transform: uppercase;
            margin-bottom: 24px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.4);
            position: relative; overflow: hidden;
        }
        .hero-badge .dot {
            width: 6px; height: 6px; background: #10B981; border-radius: 50%;
            animation: pulse 2s infinite; box-shadow: 0 0 8px #10B981;
        }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
        .hero-badge::after {
            content: ''; position: absolute; top: 0; left: -100%;
            width: 50%; height: 100%;
            background: linear-gradient(90deg, transparent, rgba(201,168,76,0.18), transparent);
            animation: badge-shine 4s infinite;
        }
        @keyframes badge-shine { 0%{left:-100%} 100%{left:200%} }

        .hero h1 {
            font-family: 'Inter', sans-serif;
            font-size: 64px; font-weight: 800;
            letter-spacing: -2px; line-height: 1.02;
            color: #fff;
            margin-bottom: 18px;
            text-shadow: 0 4px 32px rgba(0,0,0,0.6);
        }
        .hero h1 span {
            color: var(--gold);
            font-family: 'Cormorant Garamond', serif;
            font-style: italic;
            font-weight: 500;
            letter-spacing: -1px;
        }
        .hero .subtitle {
            font-size: 17px; line-height: 1.65;
            color: rgba(232,234,240,0.78);
            max-width: 560px;
            margin-bottom: 36px;
            text-shadow: 0 2px 12px rgba(0,0,0,0.7);
        }

        /* Hero stat row — glassy compact */
        .stats-row {
            display: flex; gap: 10px; flex-wrap: wrap; margin-top: 0;
        }
        .hero .stat-card {
            background: rgba(10,10,10,0.62);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(201,168,76,0.18);
            border-radius: 12px;
            padding: 14px 22px;
            min-width: 110px;
            transition: transform 0.25s, border-color 0.25s, background 0.25s;
        }
        .hero .stat-card:hover {
            transform: translateY(-4px);
            border-color: var(--gold);
            background: rgba(18,18,18,0.78);
        }
        .hero .stat-card .val {
            font-family: 'JetBrains Mono', monospace;
            font-size: 26px; font-weight: 700; color: #fff;
        }
        .hero .stat-card .lbl {
            font-size: 10px; color: var(--text-dim);
            text-transform: uppercase; letter-spacing: 1.4px;
            margin-top: 4px;
        }

        /* Bottom bar — controls + legend + scroll cue */
        .hero-bottom {
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            align-items: end;
            gap: 32px;
        }

        .graph-legend {
            display: flex; gap: 16px; flex-wrap: wrap; align-items: center;
        }
        .legend-item {
            display: flex; align-items: center; gap: 7px;
            font-size: 10.5px; color: rgba(232,234,240,0.75);
            font-weight: 500; letter-spacing: 0.4px;
            background: rgba(0,0,0,0.45); backdrop-filter: blur(12px);
            padding: 6px 10px; border-radius: 50px;
            border: 1px solid rgba(255,255,255,0.05);
        }
        .legend-dot {
            width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
        }

        .graph-controls {
            display: flex; flex-direction: row-reverse; gap: 7px;
            flex-wrap: wrap; justify-content: flex-end;
        }
        .graph-control-btn {
            background: rgba(10,10,10,0.62);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(201,168,76,0.18); border-radius: 50px;
            padding: 7px 14px; font-size: 10.5px; font-weight: 600;
            color: rgba(232,234,240,0.8); cursor: pointer;
            letter-spacing: 0.8px; text-transform: uppercase;
            transition: all 0.2s;
        }
        .graph-control-btn:hover, .graph-control-btn.active {
            color: var(--gold); border-color: var(--gold);
            background: rgba(201,168,76,0.12);
        }

        /* Scroll cue (animated arrow) */
        .scroll-cue {
            grid-column: 2;
            display: flex; flex-direction: column;
            align-items: center; gap: 8px;
            font-size: 10px; color: rgba(232,234,240,0.55);
            letter-spacing: 3px; text-transform: uppercase;
            cursor: pointer;
            user-select: none;
        }
        .scroll-cue .arrow {
            width: 22px; height: 36px;
            border: 1.5px solid rgba(201,168,76,0.5);
            border-radius: 12px;
            position: relative;
        }
        .scroll-cue .arrow::after {
            content: '';
            position: absolute; top: 6px; left: 50%;
            width: 2px; height: 8px;
            background: var(--gold);
            border-radius: 1px;
            transform: translateX(-50%);
            animation: scroll-dot 2s infinite;
        }
        @keyframes scroll-dot {
            0%   { top: 6px;  opacity: 1; }
            70%  { top: 20px; opacity: 0; }
            100% { top: 6px;  opacity: 0; }
        }

        /* Tooltip */
        #graph-tooltip {
            position: fixed; padding: 14px 18px;
            background: rgba(8,8,8,0.95); backdrop-filter: blur(20px);
            border: 1px solid rgba(201,168,76,0.25); border-radius: 12px;
            pointer-events: none; z-index: 9999;
            opacity: 0; transition: opacity 0.15s;
            max-width: 240px; min-width: 170px;
            box-shadow: 0 16px 48px rgba(0,0,0,0.75), 0 0 0 1px rgba(201,168,76,0.05);
        }
        #graph-tooltip.visible { opacity: 1; }
        #graph-tooltip .tt-name {
            font-weight: 700; font-size: 14px; color: #fff;
            margin-bottom: 8px; padding-bottom: 8px;
            border-bottom: 1px solid rgba(201,168,76,0.15);
        }
        #graph-tooltip .tt-row {
            font-size: 11.5px; color: var(--text-dim);
            display: flex; justify-content: space-between; gap: 12px;
            margin-bottom: 3px;
        }
        #graph-tooltip .tt-val {
            color: var(--gold); font-family: 'JetBrains Mono', monospace;
            font-weight: 600; font-size: 11px;
        }

        /* ════════════════════════════════════
           NAV — sticky glass with gold underline glow
           ════════════════════════════════════ */
        .nav {
            background: rgba(3,3,3,0.92);
            backdrop-filter: blur(24px);
            border-bottom: 1px solid rgba(201,168,76,0.1);
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        }

        /* ════════════════════════════════════
           SECTIONS — 3D scroll-in transitions
           ════════════════════════════════════ */
        .section {
            position: relative;
            overflow: hidden;
            transform-origin: center top;
            transform: perspective(1600px) rotateX(-8deg) translateY(60px) scale(0.97);
            opacity: 0;
            transition:
                transform 1.05s cubic-bezier(0.22, 1, 0.36, 1),
                opacity   0.9s cubic-bezier(0.22, 1, 0.36, 1);
            will-change: transform, opacity;
        }
        .section.in-view {
            transform: perspective(1600px) rotateX(0) translateY(0) scale(1);
            opacity: 1;
        }

        /* Section background number */
        .section-num {
            position: absolute; right: 56px; top: 24px;
            font-family: 'Cormorant Garamond', serif;
            font-size: 120px; font-weight: 300; line-height: 1;
            color: rgba(201,168,76,0.035);
            pointer-events: none; user-select: none;
            transition: transform 1.2s ease;
        }
        .section.in-view .section-num {
            transform: translateY(-12px);
        }

        /* Stagger method cards */
        .method-card {
            opacity: 0;
            transform: translateY(28px) scale(0.97);
            transition: opacity 0.6s ease, transform 0.6s cubic-bezier(0.22, 1, 0.36, 1);
        }
        .section.in-view .method-card {
            opacity: 1;
            transform: none;
        }
        .section.in-view .method-card:nth-child(1) { transition-delay: 0.05s; }
        .section.in-view .method-card:nth-child(2) { transition-delay: 0.10s; }
        .section.in-view .method-card:nth-child(3) { transition-delay: 0.15s; }
        .section.in-view .method-card:nth-child(4) { transition-delay: 0.20s; }
        .section.in-view .method-card:nth-child(5) { transition-delay: 0.25s; }
        .section.in-view .method-card:nth-child(6) { transition-delay: 0.30s; }
        .section.in-view .method-card:nth-child(7) { transition-delay: 0.35s; }
        .section.in-view .method-card:nth-child(8) { transition-delay: 0.40s; }

        /* Chart card reveal */
        .chart-card {
            opacity: 0;
            transform: translateY(20px) scale(0.985);
            transition: opacity 0.7s ease, transform 0.7s cubic-bezier(0.22, 1, 0.36, 1);
            transition-delay: 0.15s;
        }
        .section.in-view .chart-card {
            opacity: 1;
            transform: none;
        }

        /* Section header reveal */
        .section-header {
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.6s ease 0.05s, transform 0.6s cubic-bezier(0.22, 1, 0.36, 1) 0.05s;
        }
        .section.in-view .section-header {
            opacity: 1;
            transform: none;
        }

        /* ════════════════════════════════════
           PLAYER SPOTLIGHT (transitions between sections)
           ════════════════════════════════════ */
        .spotlight {
            position: relative;
            padding: 110px 80px;
            min-height: 540px;
            overflow: hidden;
            background:
                radial-gradient(ellipse 60% 80% at 80% 50%, rgba(201,168,76,0.07) 0%, transparent 70%),
                linear-gradient(180deg, #050505 0%, #0a0a0a 50%, #050505 100%);
            border-top: 1px solid rgba(201,168,76,0.10);
            border-bottom: 1px solid rgba(201,168,76,0.10);
            transform-origin: center;
            transform: perspective(1600px) rotateX(-6deg) translateY(40px) scale(0.98);
            opacity: 0;
            transition:
                transform 1.05s cubic-bezier(0.22, 1, 0.36, 1),
                opacity   0.95s cubic-bezier(0.22, 1, 0.36, 1);
            will-change: transform, opacity;
        }
        .spotlight.in-view {
            transform: perspective(1600px) rotateX(0) translateY(0) scale(1);
            opacity: 1;
        }
        .spotlight::before {
            /* faint grid texture */
            content: '';
            position: absolute; inset: 0;
            background: url("data:image/svg+xml,%3Csvg width='40' height='40' xmlns='http://www.w3.org/2000/svg'%3E%3Ccircle cx='20' cy='20' r='0.5' fill='%23c9a84c' fill-opacity='0.06'/%3E%3C/svg%3E");
            pointer-events: none;
        }
        .spotlight-bg-stat {
            position: absolute;
            right: 6vw; top: 50%;
            transform: translateY(-50%);
            font-family: 'Cormorant Garamond', serif;
            font-size: clamp(180px, 32vw, 420px);
            font-weight: 300;
            color: rgba(201,168,76,0.04);
            line-height: 0.8;
            letter-spacing: -8px;
            pointer-events: none;
            user-select: none;
            white-space: nowrap;
        }
        .spotlight-content {
            display: grid;
            grid-template-columns: 1.1fr 1fr;
            gap: 60px;
            align-items: center;
            max-width: 1400px;
            margin: 0 auto;
            position: relative;
            z-index: 2;
        }
        .spotlight-eyebrow {
            font-size: 11px; font-weight: 600;
            letter-spacing: 4px; text-transform: uppercase;
            color: var(--gold); margin-bottom: 22px;
            display: flex; align-items: center; gap: 14px;
        }
        .spotlight-eyebrow::before {
            content: ''; width: 36px; height: 1px;
            background: linear-gradient(90deg, transparent, var(--gold));
        }
        .spotlight-text h3 {
            font-family: 'Cormorant Garamond', serif;
            font-size: clamp(40px, 5vw, 76px);
            font-weight: 300;
            color: #fff;
            line-height: 1; letter-spacing: -1.5px;
            margin-bottom: 28px;
        }
        .spotlight-text h3 em {
            color: var(--gold);
            font-style: italic;
            font-weight: 400;
        }
        .spotlight-quote {
            font-family: 'Cormorant Garamond', serif;
            font-size: clamp(17px, 1.5vw, 23px);
            font-style: italic;
            font-weight: 400;
            color: rgba(232,234,240,0.85);
            line-height: 1.5;
            margin-bottom: 32px;
            padding-left: 22px;
            border-left: 2px solid var(--gold);
            max-width: 540px;
        }
        .spotlight-meta {
            display: flex; align-items: center; gap: 28px;
            flex-wrap: wrap;
        }
        .spotlight-stat-block {
            border-right: 1px solid rgba(201,168,76,0.2);
            padding-right: 28px;
        }
        .spotlight-stat-val {
            font-family: 'JetBrains Mono', monospace;
            font-size: 44px; font-weight: 700;
            color: var(--gold);
            line-height: 1;
        }
        .spotlight-stat-lbl {
            font-size: 10px; color: var(--text-dim);
            letter-spacing: 2.5px; text-transform: uppercase;
            margin-top: 7px;
        }
        .spotlight-desc {
            font-size: 13.5px; color: var(--text-dim);
            line-height: 1.55;
            max-width: 280px;
        }
        /* Video frame replaces static photo — keeps cinematic NBA action looping */
        .spotlight-video-wrap {
            position: relative;
            aspect-ratio: 4 / 3;
            width: 100%;
            max-width: 540px;
            margin-left: auto;
            border-radius: 18px;
            overflow: hidden;
            transform: translateY(30px) scale(0.97);
            opacity: 0;
            transition:
                transform 1.3s cubic-bezier(0.22, 1, 0.36, 1) 0.15s,
                opacity   1.1s ease 0.15s;
            box-shadow:
                0 24px 60px rgba(0,0,0,0.7),
                0 0 0 1px rgba(201,168,76,0.15),
                0 0 80px rgba(201,168,76,0.12);
        }
        .spotlight.in-view .spotlight-video-wrap {
            transform: translateY(0) scale(1);
            opacity: 1;
        }
        .spotlight-video,
        .spotlight-img-fallback {
            position: absolute; inset: 0;
            width: 100%; height: 100%;
            object-fit: cover;
            display: block;
            background: #050505;
        }
        .spotlight-img-fallback { object-fit: contain; padding: 20px; }

        /* Subtle cinematic vignette over the video */
        .spotlight-video-overlay {
            position: absolute; inset: 0;
            background:
                linear-gradient(180deg, transparent 50%, rgba(0,0,0,0.65) 100%),
                radial-gradient(ellipse 100% 100% at 50% 50%, transparent 60%, rgba(0,0,0,0.45) 100%);
            pointer-events: none;
            z-index: 2;
        }
        /* Gold inner-frame on hover */
        .spotlight-video-frame {
            position: absolute; inset: 0;
            border-radius: 18px;
            border: 1px solid rgba(201,168,76,0.22);
            box-shadow: inset 0 0 0 4px rgba(0,0,0,0.7);
            pointer-events: none;
            z-index: 3;
            transition: border-color 0.4s;
        }
        .spotlight-video-wrap:hover .spotlight-video-frame {
            border-color: rgba(201,168,76,0.6);
        }
        /* Soft glow behind the frame */
        .spotlight-video-glow {
            position: absolute;
            inset: -30px;
            border-radius: 24px;
            background: radial-gradient(ellipse 60% 50% at 50% 70%, rgba(201,168,76,0.22) 0%, transparent 65%);
            pointer-events: none;
            z-index: -1;
        }

        @media (max-width: 900px) {
            .spotlight { padding: 60px 24px; min-height: auto; }
            .spotlight-content { grid-template-columns: 1fr; gap: 32px; }
            .spotlight-video-wrap { max-width: 100%; order: -1; aspect-ratio: 16 / 10; }
            .spotlight-bg-stat { font-size: 180px; opacity: 0.5; }
        }

        /* ════════════════════════════════════
           FOOTER
           ════════════════════════════════════ */
        .footer { position: relative; }
        .footer-mm {
            font-family: 'Cormorant Garamond', serif;
            font-size: 22px; font-weight: 300;
            color: rgba(201,168,76,0.4);
            letter-spacing: 6px; text-transform: uppercase;
        }

        /* ════════════════════════════════════
           RESPONSIVE
           ════════════════════════════════════ */
        @media (max-width: 900px) {
            .hero-overlay { padding: 32px 24px 24px; }
            .hero h1 { font-size: 38px; }
            .hero .subtitle { font-size: 14px; }
            .hero-bottom { grid-template-columns: 1fr; gap: 16px; }
            .scroll-cue { grid-column: 1; }
            .graph-controls { justify-content: flex-start; }
            .mm-monogram { font-size: 38px; }
        }
"""

# ══════════════════════════════════════════════════════════════════════
# NEW HERO  ·  Full-viewport 3D graph + overlay
# ══════════════════════════════════════════════════════════════════════
NEW_HERO = """
<!-- HERO  ·  3D Knowledge Graph -->
<div class="hero" id="hero">
    <div id="hero-graph-bg"></div>
    <div class="hero-overlay">

        <!-- Top: badge (left) + MM (right) -->
        <div class="hero-top">
            <div class="hero-badge"><span class="dot"></span> Live 3D Knowledge Graph</div>
            <div class="mm-brand">
                <div class="mm-monogram">MM</div>
                <div class="mm-name">Minho Moon</div>
            </div>
        </div>

        <!-- Center: title + stats -->
        <div class="hero-center">
            <h1>NBA Roster<br/><span>Optimization</span> Engine</h1>
            <p class="subtitle">
                A 3D map of the modern NBA &mdash; every 2023-24 rotation player across 6 archetypes,
                connected by real pairwise synergy from 2-man lineup data.
                Drag to rotate &middot; scroll inside the graph to zoom.
            </p>
            <div class="stats-row">
                <div class="stat-card"><div class="val" data-target="1208">0</div><div class="lbl">Player-Seasons</div></div>
                <div class="stat-card"><div class="val" data-target="9">0</div><div class="lbl">Validated Stats</div></div>
                <div class="stat-card"><div class="val" data-target="6">0</div><div class="lbl">Archetypes</div></div>
                <div class="stat-card"><div class="val" data-target="10">0</div><div class="lbl">Optimized Rosters</div></div>
                <div class="stat-card"><div class="val" data-target="175">0</div><div class="lbl">Checks Passed</div></div>
            </div>
        </div>

        <!-- Bottom: legend (left) + scroll cue (center) + controls (right) -->
        <div class="hero-bottom">
            <div class="graph-legend">
                <div class="legend-item"><div class="legend-dot" style="background:#C9A84C;box-shadow:0 0 7px #C9A84C99"></div>Elite Playmaker</div>
                <div class="legend-item"><div class="legend-dot" style="background:#06B6D4;box-shadow:0 0 7px #06B6D499"></div>Defensive Wing</div>
                <div class="legend-item"><div class="legend-dot" style="background:#3B82F6;box-shadow:0 0 7px #3B82F699"></div>Perimeter Scorer</div>
                <div class="legend-item"><div class="legend-dot" style="background:#A855F7;box-shadow:0 0 7px #A855F799"></div>Versatile Scorer</div>
                <div class="legend-item"><div class="legend-dot" style="background:#10B981;box-shadow:0 0 7px #10B98199"></div>Two-Way Big</div>
                <div class="legend-item"><div class="legend-dot" style="background:#F97316;box-shadow:0 0 7px #F9731699"></div>Bench / Role</div>
            </div>
            <div class="scroll-cue" onclick="document.getElementById('methodology').scrollIntoView({behavior:'smooth'})">
                <div class="arrow"></div>
                <span>Scroll</span>
            </div>
            <div class="graph-controls">
                <button class="graph-control-btn" onclick="filterGraph(this,'Versatile Scorer')">Versatile</button>
                <button class="graph-control-btn" onclick="filterGraph(this,'Two-Way Big')">Bigs</button>
                <button class="graph-control-btn" onclick="filterGraph(this,'Perimeter Scorer')">Scorers</button>
                <button class="graph-control-btn" onclick="filterGraph(this,'Defensive Wing')">Defenders</button>
                <button class="graph-control-btn" onclick="filterGraph(this,'Elite Playmaker')">Playmakers</button>
                <button class="graph-control-btn active" onclick="filterGraph(this,'all')">All</button>
            </div>
        </div>

    </div>
</div>
<div id="graph-tooltip">
    <div class="tt-name" id="tt-name">-</div>
    <div class="tt-row"><span>Score</span><span class="tt-val" id="tt-score">-</span></div>
    <div class="tt-row"><span>Team</span><span class="tt-val" id="tt-team">-</span></div>
    <div class="tt-row"><span>Archetype</span><span class="tt-val" id="tt-arch">-</span></div>
    <div class="tt-row"><span>Salary</span><span class="tt-val" id="tt-salary">-</span></div>
</div>
"""

# ══════════════════════════════════════════════════════════════════════
# JS  ·  3D graph + scroll engine + counters
# ══════════════════════════════════════════════════════════════════════
GRAPH_JS = f"""
<script src="https://unpkg.com/3d-force-graph@1.73.1/dist/3d-force-graph.min.js"></script>
<script>
/* ─────────────────────────────────────────────
   3D Knowledge Graph (hero background)
   ───────────────────────────────────────────── */
(function () {{
  const RAW = {GRAPH_DATA_JS};
  let Graph = null;
  let rotTimer = null;
  let rotPaused = false;
  const container = document.getElementById('hero-graph-bg');
  if (!container) return;

  function deepClone(d) {{
    return {{ nodes: d.nodes.map(n => ({{...n}})), links: d.links.map(l => ({{...l}})) }};
  }}

  function startRotation() {{
    if (rotTimer) clearInterval(rotTimer);
    rotPaused = false;
    let angle = 0;
    rotTimer = setInterval(() => {{
      if (!Graph || rotPaused) return;
      angle += 0.0014;
      const d = Graph.camera().position.length();
      Graph.cameraPosition({{ x: d * Math.sin(angle), z: d * Math.cos(angle) }});
    }}, 33);
  }}

  /* Build the Force-Graph instance ONCE; all subsequent filter changes
     reuse it via .graphData(). This avoids the WebGL-destroy glitch. */
  function initGraph() {{
    Graph = ForceGraph3D({{ antialias: true, alpha: true }})(container)
      .backgroundColor('rgba(0,0,0,0)')
      .graphData(deepClone(RAW))
      .nodeId('id')
      .nodeLabel(() => '')
      .nodeVal(n => n.val)
      .nodeColor(n => n.color)
      .nodeOpacity(0.94)
      .nodeResolution(16)
      .linkColor(l => l.color || 'rgba(255,255,255,0.06)')
      .linkWidth(l => {{
        const s = Math.abs(l.synergy || 0);
        return s > 0 ? Math.min(2.2, 0.35 + s * 0.28) : 0.18;
      }})
      .linkOpacity(0.78)
      .linkCurvature(0.08)
      .d3AlphaDecay(0.012)
      .d3VelocityDecay(0.32)
      .warmupTicks(80)
      .cooldownTicks(Infinity)
      .onNodeHover(node => {{
        const tt = document.getElementById('graph-tooltip');
        container.style.cursor = node ? 'pointer' : 'grab';
        if (node) {{
          document.getElementById('tt-name').textContent   = node.name;
          document.getElementById('tt-score').textContent  = node.type === 'archetype' ? 'HUB' : (node.score ?? '-');
          document.getElementById('tt-team').textContent   = node.team  ?? '-';
          document.getElementById('tt-arch').textContent   = node.group ?? '-';
          document.getElementById('tt-salary').textContent = (node.salary && node.salary > 0)
            ? '$' + (node.salary / 1e6).toFixed(1) + 'M' : '-';
          tt.classList.add('visible');
        }} else {{
          tt.classList.remove('visible');
        }}
      }})
      .onBackgroundClick(() => document.getElementById('graph-tooltip').classList.remove('visible'));

    function fit() {{ Graph.width(container.clientWidth).height(container.clientHeight); }}
    fit();
    window.addEventListener('resize', fit);

    /* Fade graph in once the simulation has warmed up */
    setTimeout(() => container.classList.add('ready'), 600);

    /* Auto-fit to viewport after layout settles (handles any node count) */
    setTimeout(() => {{ if (Graph) Graph.zoomToFit(1200, 60); }}, 1200);

    /* Begin auto-rotation after warmup so it doesn't fight initial layout */
    setTimeout(startRotation, 2600);

    container.addEventListener('mousedown', () => {{ rotPaused = true; }});
    container.addEventListener('wheel',     () => {{ rotPaused = true; }});
  }}

  /* In-place data swap — keeps the WebGL context alive, no flash */
  function setData(data) {{
    if (!Graph) return;
    Graph.graphData(data);
  }}

  window.filterGraph = function (btn, filter) {{
    document.querySelectorAll('.graph-control-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    if (filter === 'all') {{ setData(deepClone(RAW)); return; }}
    const keep = new Set(RAW.nodes.filter(n => n.group === filter).map(n => n.id));
    keep.add('arch::' + filter);
    const nodes = RAW.nodes.filter(n => keep.has(n.id)).map(n => ({{...n}}));
    const ids = new Set(nodes.map(n => n.id));
    const links = RAW.links
      .filter(l => ids.has(l.source?.id || l.source) && ids.has(l.target?.id || l.target))
      .map(l => ({{...l}}));
    setData({{ nodes, links }});
  }};

  // Tooltip follows mouse
  document.addEventListener('mousemove', e => {{
    const tt = document.getElementById('graph-tooltip');
    if (!tt.classList.contains('visible')) return;
    const x = e.clientX + 18, y = e.clientY - 10;
    const rw = tt.offsetWidth || 240, rh = tt.offsetHeight || 130;
    tt.style.left = (x + rw > window.innerWidth  ? x - rw - 28 : x) + 'px';
    tt.style.top  = (y + rh > window.innerHeight ? y - rh - 8  : y) + 'px';
  }});

  // Init when lib ready
  if (typeof ForceGraph3D !== 'undefined') initGraph();
  else {{
    const wait = setInterval(() => {{
      if (typeof ForceGraph3D !== 'undefined') {{ clearInterval(wait); initGraph(); }}
    }}, 80);
  }}
}})();

/* ─────────────────────────────────────────────
   Scroll-driven 3D section reveals
   ───────────────────────────────────────────── */
const sectionObs = new IntersectionObserver(entries => {{
  entries.forEach(e => {{
    if (e.isIntersecting) {{
      e.target.classList.add('in-view');
    }}
  }});
}}, {{ threshold: 0.12, rootMargin: '0px 0px -10% 0px' }});

document.querySelectorAll('.section, .spotlight').forEach(s => sectionObs.observe(s));

/* ─────────────────────────────────────────────
   Lazy-load spotlight videos (Giphy MP4s)
   Only fetch + autoplay when the user is near
   ───────────────────────────────────────────── */
const videoObs = new IntersectionObserver(entries => {{
  entries.forEach(e => {{
    const v = e.target;
    if (e.isIntersecting) {{
      if (!v.src && v.dataset.src) {{
        v.src = v.dataset.src;
        v.load();
      }}
      const p = v.play();
      if (p && p.catch) p.catch(() => {{}});
    }} else {{
      try {{ v.pause(); }} catch(_) {{}}
    }}
  }});
}}, {{ threshold: 0.25, rootMargin: '200px 0px' }});
document.querySelectorAll('.spotlight-video').forEach(v => videoObs.observe(v));

/* ─────────────────────────────────────────────
   Animated number counters (only inside hero)
   ───────────────────────────────────────────── */
function animCount(el) {{
  const raw = el.dataset.target;
  if (!raw) return;
  const target = parseFloat(raw);
  const dur = 1800, start = performance.now();
  (function tick(now) {{
    const p = Math.min((now - start) / dur, 1);
    const e = 1 - Math.pow(1 - p, 3);
    el.textContent = Math.round(target * e).toLocaleString();
    if (p < 1) requestAnimationFrame(tick);
  }})(start);
}}
// Trigger after a short delay so it overlaps with the graph intro
setTimeout(() => {{
  document.querySelectorAll('.val[data-target]').forEach(animCount);
}}, 800);

/* ─────────────────────────────────────────────
   Subtle parallax on hero text while scrolling
   ───────────────────────────────────────────── */
const heroCenter = document.querySelector('.hero-center');
const heroTop    = document.querySelector('.hero-top');
const heroBottom = document.querySelector('.hero-bottom');
const graphBg    = document.getElementById('hero-graph-bg');

window.addEventListener('scroll', () => {{
  const y = window.scrollY;
  if (y > window.innerHeight * 1.2) return;  // skip when far past hero
  const t = Math.min(y / window.innerHeight, 1);
  if (heroCenter) heroCenter.style.transform = `translateY(${{t * -80}}px)`;
  if (heroTop)    heroTop.style.transform    = `translateY(${{t * -40}}px)`;
  if (heroBottom) heroBottom.style.transform = `translateY(${{t *  60}}px)`;
  if (graphBg)    graphBg.style.transform    = `scale(${{1 + t * 0.15}})`;
  // Fade overlay as you scroll past hero
  const overlay = document.querySelector('.hero-overlay');
  if (overlay) overlay.style.opacity = String(1 - t * 1.2);
}}, {{ passive: true }});

</script>
"""

# ══════════════════════════════════════════════════════════════════════
# Read + patch existing dashboard
# ══════════════════════════════════════════════════════════════════════
print("Reading existing dashboard...")
with open(INPUT_HTML, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Inject extra CSS right before closing </style>
html = html.replace("</style>", EXTRA_CSS + "\n    </style>", 1)

# 2. Replace the entire <!-- HERO -->...<!-- NAV --> block
html = re.sub(
    r"<!-- HERO -->.*?(?=<!-- NAV -->)",
    NEW_HERO + "\n\n",
    html,
    count=1,
    flags=re.DOTALL,
)

# 3. Add section-num decorative numbers to every section
section_labels = iter(["01","02","03","04","05","06","07","08","09","10"])
html = re.sub(
    r'(<div class="section" id="[^"]+">)',
    lambda m: m.group(0) + f'\n    <div class="section-num">{next(section_labels, "")}</div>',
    html
)

# 3b. Inject player-spotlight transition cards between specific sections
SPOTLIGHTS = [
    {
        "before": "value-map",
        "player_id": "203999",
        "giphy_id": "OSeUQJQxEDki6GB3LV",  # Nikola Jokić basketball action (Denver Nuggets)
        "name_first": "Nikola", "name_last": "Jokić",
        "eyebrow": "Highest Composite Score",
        "stat": "96.3", "stat_lbl": "PCA Score",
        "desc": "Elite Playmaker  ·  DEN  ·  2023-24",
        "quote": "Every signal we trust agrees on him. The model's centerpiece.",
        "bg_stat": "96.3",
    },
    {
        "before": "rankings",
        "player_id": "1628983",
        "giphy_id": "W6JJlg4UmK5XqRfz3U",  # Shai Gilgeous-Alexander basketball (OKC Thunder)
        "name_first": "Shai", "name_last": "Gilgeous-Alexander",
        "eyebrow": "Mid-Range Mastery, Quantified",
        "stat": "89.0", "stat_lbl": "Composite",
        "desc": "Elite Playmaker  ·  OKC  ·  2023-24",
        "quote": "Old-school footwork meets new-school efficiency.",
        "bg_stat": "#2",
    },
    {
        "before": "archetypes",
        "player_id": "203507",
        "giphy_id": "Qg3HvhmT5ECSNwZQM7",  # Giannis Antetokounmpo dunk (NBA)
        "name_first": "Giannis", "name_last": "Antetokounmpo",
        "eyebrow": "The Versatile All-Star",
        "stat": "ALL 6", "stat_lbl": "Archetypes",
        "desc": "Good at everything, fitting no single cluster cleanly.",
        "quote": "A player so versatile he refutes the very idea of archetype.",
        "bg_stat": "v·",
    },
    {
        "before": "synergy",
        "player_id": "1627750",
        "giphy_id": "n2afntw2IxBfhkqhd3",  # Jamal Murray game winner (Denver Nuggets)
        "name_first": "Jokić ×", "name_last": "Murray",
        "eyebrow": "A Championship Duo, Quantified",
        "stat": "+5.2", "stat_lbl": "Net / 100",
        "desc": "Validated by real 2-man lineup performance.",
        "quote": "Where the model stops predicting and starts confirming.",
        "bg_stat": "+5",
    },
]

def spotlight_html(s):
    headshot = f"https://cdn.nba.com/headshots/nba/latest/1040x760/{s['player_id']}.png"
    video_mp4 = f"https://media.giphy.com/media/{s['giphy_id']}/giphy.mp4"
    return f"""
<!-- Spotlight: {s['name_first']} {s['name_last']} -->
<div class="spotlight" data-spotlight>
    <div class="spotlight-bg-stat">{s['bg_stat']}</div>
    <div class="spotlight-content">
        <div class="spotlight-text">
            <div class="spotlight-eyebrow">{s['eyebrow']}</div>
            <h3>{s['name_first']} <em>{s['name_last']}</em></h3>
            <div class="spotlight-quote">&ldquo;{s['quote']}&rdquo;</div>
            <div class="spotlight-meta">
                <div class="spotlight-stat-block">
                    <div class="spotlight-stat-val">{s['stat']}</div>
                    <div class="spotlight-stat-lbl">{s['stat_lbl']}</div>
                </div>
                <div class="spotlight-desc">{s['desc']}</div>
            </div>
        </div>
        <div class="spotlight-video-wrap">
            <video class="spotlight-video"
                   data-src="{video_mp4}"
                   poster="{headshot}"
                   muted loop playsinline preload="none"
                   onerror="this.replaceWith(Object.assign(document.createElement('img'),{{src:'{headshot}',className:'spotlight-img-fallback',alt:'{s['name_first']} {s['name_last']}'}}))"></video>
            <div class="spotlight-video-overlay"></div>
            <div class="spotlight-video-glow"></div>
            <div class="spotlight-video-frame"></div>
        </div>
    </div>
</div>
"""

for s in SPOTLIGHTS:
    target = f'<div class="section" id="{s["before"]}">'
    if target in html:
        html = html.replace(target, spotlight_html(s) + "\n" + target, 1)
        # ASCII-only console print (avoid cp1252 errors on Windows)
        safe_name = (s['name_first'] + ' ' + s['name_last']).encode('ascii', 'replace').decode('ascii')
        print(f"  Spotlight inserted before #{s['before']}: {safe_name}")
    else:
        print(f"  WARNING: target section #{s['before']} not found, skipping spotlight")

# 4. Inject graph + scroll JS before </body>
html = html.replace("</body>", GRAPH_JS + "\n</body>", 1)

# 5. Footer tweak — center the bottom
html = html.replace(
    'class="footer-bottom"',
    'class="footer-bottom" style="flex-direction:column;gap:14px;text-align:center;"',
    1
)

# ── Write ─────────────────────────────────────────────────────────────
print(f"Writing -> {OUTPUT_HTML}")
with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(html)

size_kb = OUTPUT_HTML.stat().st_size // 1024
print(f"Done! ({size_kb} KB) -- refresh NBA_Enhanced_Dashboard.html in the browser")
