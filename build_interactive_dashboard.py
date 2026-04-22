"""
Build interactive HTML dashboard using Plotly.
Opens in any browser — no Tableau or Power BI needed.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

print("=" * 60)
print("BUILDING INTERACTIVE DASHBOARD")
print("=" * 60)

# ── Load data ────────────────────────────────────────────────────────────────
df_all = pd.read_csv('nba_clustered.csv')
df_2324 = df_all[df_all['SEASON'] == '2023-24'].copy().sort_values('COMPOSITE_SCORE_NORM', ascending=False)
df_synergy = pd.read_csv('nba_synergy_2324.csv')
df_profile = pd.read_csv('nba_def_synergy_profile.csv')

rosters = {}
for key in 'ABCDEFGHIJ':
    try:
        rosters[key] = pd.read_csv(f'optimized_roster_syn_{key}.csv')
    except FileNotFoundError:
        pass

scenario_names = {
    'A': 'Hard Cap ($136M)', 'B': 'Luxury Tax ($165M)', 'C': 'Budget ($90M)',
    'D': 'Rebuild ($136M)', 'E': 'Win-Now ($165M)', 'F': 'Defensive Identity',
    'G': 'Offensive Identity', 'H': 'Three-Point Era', 'I': 'Small Ball',
    'J': 'Value/Efficiency'
}

# Colors per archetype
arch_colors = {
    'Elite Playmaker': '#FFD700',
    'Two-Way Big': '#2ECC71',
    'Versatile Scorer': '#E67E22',
    'Defensive Wing': '#E74C3C',
    'Perimeter Scorer': '#3498DB',
    'Bench / Role Player': '#95A5A6',
}

print(f"Loaded {len(df_2324)} players (2023-24)")
print(f"Loaded {len(rosters)} rosters")

# ============================================================
# CHART 1 — SCORE vs SALARY SCATTER (THE VORPD VIEW)
# ============================================================

print("Building Chart 1: Score vs Salary scatter...")

fig1 = go.Figure()

for arch, color in arch_colors.items():
    mask = df_2324['ARCHETYPE'] == arch
    subset = df_2324[mask]
    fig1.add_trace(go.Scatter(
        x=subset['SALARY'] / 1_000_000,
        y=subset['COMPOSITE_SCORE_NORM'],
        mode='markers',
        name=arch,
        marker=dict(color=color, size=8, opacity=0.7,
                    line=dict(width=0.5, color='#333')),
        text=subset['PLAYER_NAME'] + ' (' + subset['TEAM_ABBREVIATION'] + ')',
        hovertemplate=(
            '<b>%{text}</b><br>'
            'Score: %{y:.1f}<br>'
            'Salary: $%{x:.1f}M<br>'
            '<extra></extra>'
        ),
    ))

# Annotate top 5
top5 = df_2324.head(5)
for _, row in top5.iterrows():
    fig1.add_annotation(
        x=row['SALARY'] / 1_000_000, y=row['COMPOSITE_SCORE_NORM'],
        text=row['PLAYER_NAME'].split()[-1],
        showarrow=True, arrowhead=2, arrowsize=0.8,
        font=dict(size=10, color='white'),
        bgcolor='#1B2A4A', bordercolor='#C9A84C',
    )

fig1.update_layout(
    title=dict(text='Player Value Map — Score vs Salary (2023-24)', font=dict(size=20)),
    xaxis_title='Salary ($M)',
    yaxis_title='Composite Score (0-100)',
    template='plotly_dark',
    legend=dict(title='Archetype', font=dict(size=11)),
    height=600,
)

# ============================================================
# CHART 2 — TOP 30 PLAYER RANKINGS (horizontal bar)
# ============================================================

print("Building Chart 2: Top 30 rankings...")

top30 = df_2324.head(30).iloc[::-1]  # reverse for horizontal bar

fig2 = go.Figure()
fig2.add_trace(go.Bar(
    y=top30['PLAYER_NAME'] + ' (' + top30['TEAM_ABBREVIATION'] + ')',
    x=top30['COMPOSITE_SCORE_NORM'],
    orientation='h',
    base=0,
    marker=dict(
        color=[arch_colors.get(a, '#95A5A6') for a in top30['ARCHETYPE']],
        line=dict(width=0.5, color='#333')
    ),
    text=[f"{s:.1f}" for s in top30['COMPOSITE_SCORE_NORM']],
    textposition='inside',
    insidetextanchor='end',
    textfont=dict(color='white', size=11),
    hovertemplate=(
        '<b>%{y}</b><br>'
        'Score: %{x:.1f} / 100<br>'
        'Archetype: %{customdata}<br>'
        '<extra></extra>'
    ),
    customdata=top30['ARCHETYPE'],
))

fig2.update_layout(
    title=dict(text='Top 30 NBA Players by Composite Score — 2023-24', font=dict(size=20)),
    xaxis_title='Composite Score',
    xaxis=dict(
        range=[0, 100],
        dtick=10,
        tickvals=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        ticktext=['0', '10', '20', '30', '40', '50', '60', '70', '80', '90', '100'],
    ),
    template='plotly_dark',
    height=900,
    margin=dict(l=220),
)

# ============================================================
# CHART 3 — ARCHETYPE DISTRIBUTION (sunburst)
# ============================================================

print("Building Chart 3: Archetype distribution...")

arch_counts = df_2324['ARCHETYPE'].value_counts().reset_index()
arch_counts.columns = ['Archetype', 'Count']
arch_counts['Avg Score'] = arch_counts['Archetype'].apply(
    lambda a: df_2324[df_2324['ARCHETYPE'] == a]['COMPOSITE_SCORE_NORM'].mean()
)

fig3 = go.Figure(go.Pie(
    labels=arch_counts['Archetype'],
    values=arch_counts['Count'],
    marker=dict(colors=[arch_colors.get(a, '#95A5A6') for a in arch_counts['Archetype']]),
    textinfo='label+percent+value',
    textfont=dict(size=12),
    hovertemplate=(
        '<b>%{label}</b><br>'
        'Players: %{value}<br>'
        'Share: %{percent}<br>'
        '<extra></extra>'
    ),
    hole=0.35,
))

fig3.update_layout(
    title=dict(text='Player Archetype Distribution — 2023-24 (399 Players)', font=dict(size=20)),
    template='plotly_dark',
    height=500,
)

# ============================================================
# CHART 4 — ARCHETYPE RADAR (average stat profiles)
# ============================================================

print("Building Chart 4: Archetype radar...")

radar_stats = ['OFF_RATING_ADJUSTED', 'DEF_RATING_ADJUSTED', 'ON_OFF_DIFF',
               'INFLUENCE_SCORE', 'TS_PCT', 'BLK', 'STL', 'AST_PCT_ADJUSTED', 'FG3_PCT']
radar_labels = ['OFF Rating', 'DEF Rating', 'ON/OFF Diff', 'Influence',
                'TS%', 'BLK', 'STL', 'AST%', 'FG3%']

# Normalize each stat to 0-1 range for radar
df_radar = df_2324[radar_stats].copy()
for col in radar_stats:
    col_min = df_radar[col].min()
    col_max = df_radar[col].max()
    if col_max > col_min:
        df_radar[col] = (df_radar[col] - col_min) / (col_max - col_min)

df_radar['ARCHETYPE'] = df_2324['ARCHETYPE'].values

fig4 = go.Figure()
for arch in ['Elite Playmaker', 'Two-Way Big', 'Versatile Scorer',
             'Defensive Wing', 'Perimeter Scorer', 'Bench / Role Player']:
    means = df_radar[df_radar['ARCHETYPE'] == arch][radar_stats].mean()
    fig4.add_trace(go.Scatterpolar(
        r=list(means.values) + [means.values[0]],  # close the polygon
        theta=radar_labels + [radar_labels[0]],
        name=arch,
        line=dict(color=arch_colors.get(arch, '#95A5A6'), width=2),
        fill='toself',
        opacity=0.3,
    ))

fig4.update_layout(
    title=dict(text='Archetype Stat Fingerprints — Average Normalized Profiles', font=dict(size=18)),
    template='plotly_dark',
    polar=dict(
        radialaxis=dict(visible=True, range=[0, 1], showticklabels=False),
        bgcolor='rgba(0,0,0,0)',
    ),
    height=600,
    legend=dict(font=dict(size=11)),
)

# ============================================================
# CHART 5 — SCENARIO COMPARISON (grouped bar)
# ============================================================

print("Building Chart 5: Scenario comparison...")

scenario_data = []
for key, roster in rosters.items():
    score_col = 'COMPOSITE_SYNERGY' if 'COMPOSITE_SYNERGY' in roster.columns else 'COMPOSITE_SCORE_NORM'
    roster['SALARY'] = pd.to_numeric(roster['SALARY'], errors='coerce').fillna(0)
    roster[score_col] = pd.to_numeric(roster[score_col], errors='coerce').fillna(0)
    scenario_data.append({
        'Scenario': f"{key} - {scenario_names.get(key, key)}",
        'Total Score': roster[score_col].sum(),
        'Total Salary ($M)': roster['SALARY'].sum() / 1_000_000,
        'Avg Score': roster[score_col].mean(),
    })
df_scenarios = pd.DataFrame(scenario_data)

fig5 = make_subplots(rows=1, cols=2,
                      subplot_titles=['Total Synergy Score', 'Total Salary Used ($M)'])

fig5.add_trace(go.Bar(
    x=df_scenarios['Scenario'], y=df_scenarios['Total Score'],
    marker_color='#C9A84C', name='Total Score',
    text=df_scenarios['Total Score'].round(1), textposition='outside',
), row=1, col=1)

fig5.add_trace(go.Bar(
    x=df_scenarios['Scenario'], y=df_scenarios['Total Salary ($M)'],
    marker_color='#2C80D1', name='Salary ($M)',
    text=df_scenarios['Total Salary ($M)'].round(1), textposition='outside',
), row=1, col=2)

fig5.update_layout(
    title=dict(text='10 Scenario Comparison — Score vs Salary', font=dict(size=20)),
    template='plotly_dark',
    height=500,
    showlegend=False,
)
fig5.update_xaxes(tickangle=45, tickfont=dict(size=9))

# ============================================================
# CHART 6 — ROSTER A BREAKDOWN
# ============================================================

print("Building Chart 6: Roster A breakdown...")

if 'A' in rosters:
    roster_a = rosters['A'].copy()
    score_col = 'COMPOSITE_SYNERGY' if 'COMPOSITE_SYNERGY' in roster_a.columns else 'COMPOSITE_SCORE_NORM'
    roster_a = roster_a.sort_values(score_col, ascending=True)

    fig6 = go.Figure()
    fig6.add_trace(go.Bar(
        y=roster_a['PLAYER_NAME'],
        x=roster_a[score_col],
        orientation='h',
        marker=dict(
            color=[arch_colors.get(a, '#95A5A6') for a in roster_a['ARCHETYPE']],
        ),
        text=[f"${s/1e6:.1f}M" for s in roster_a['SALARY']],
        textposition='outside',
        hovertemplate=(
            '<b>%{y}</b><br>'
            'Score: %{x:.1f}<br>'
            'Salary: %{text}<br>'
            'Archetype: %{customdata}<br>'
            '<extra></extra>'
        ),
        customdata=roster_a['ARCHETYPE'],
    ))

    total_sal = roster_a['SALARY'].sum()
    fig6.update_layout(
        title=dict(text=f'Scenario A — Hard Cap Roster ($136M) | Total Salary: ${total_sal/1e6:.1f}M',
                   font=dict(size=18)),
        xaxis_title='Synergy-Adjusted Score',
        template='plotly_dark',
        height=550,
        margin=dict(l=200),
    )

# ============================================================
# CHART 7 — SYNERGY HEATMAP (top pairs)
# ============================================================

print("Building Chart 7: Synergy matrix...")

# Get top synergy players from rosters
if 'A' in rosters:
    roster_names = rosters['A']['PLAYER_NAME'].tolist()

    # Filter synergy pairs to roster A players
    syn_roster = df_synergy[
        df_synergy['GROUP_NAME'].apply(
            lambda g: any(n in g for n in [name.split()[-1] for name in roster_names])
        )
    ].copy()

    # Build matrix from top positive pairs
    top_pairs = df_synergy.sort_values('NET_SYNERGY', ascending=False).head(25)

    fig7 = go.Figure(go.Bar(
        x=top_pairs['GROUP_NAME'],
        y=top_pairs['NET_SYNERGY'],
        marker=dict(
            color=top_pairs['NET_SYNERGY'],
            colorscale='RdYlGn',
            showscale=True,
            colorbar=dict(title='NET SYN'),
        ),
        hovertemplate=(
            '<b>%{x}</b><br>'
            'NET Synergy: %{y:.2f}<br>'
            '<extra></extra>'
        ),
    ))

    fig7.update_layout(
        title=dict(text='Top 25 Positive Synergy Pairs — 2023-24', font=dict(size=18)),
        xaxis_title='Player Pair',
        yaxis_title='NET Synergy (pts/100 poss)',
        template='plotly_dark',
        height=500,
        xaxis=dict(tickangle=45, tickfont=dict(size=8)),
    )

# ============================================================
# CHART 8 — PLAYER FREQUENCY ACROSS SCENARIOS
# ============================================================

print("Building Chart 8: Player frequency across scenarios...")

all_roster_players = pd.concat(rosters.values())
player_freq = (all_roster_players.groupby('PLAYER_NAME')
               .agg(times_selected=('SCENARIO', 'nunique'),
                    scenarios=('SCENARIO', lambda x: ', '.join(sorted(x.unique()))))
               .reset_index()
               .sort_values('times_selected', ascending=False)
               .head(25))

fig8 = go.Figure()
fig8.add_trace(go.Bar(
    x=player_freq['PLAYER_NAME'],
    y=player_freq['times_selected'],
    marker_color='#C9A84C',
    text=player_freq['scenarios'],
    hovertemplate=(
        '<b>%{x}</b><br>'
        'Selected in: %{y}/10 scenarios<br>'
        'Scenarios: %{text}<br>'
        '<extra></extra>'
    ),
))

fig8.update_layout(
    title=dict(text='Most Selected Players Across All 10 Scenarios', font=dict(size=18)),
    xaxis_title='Player',
    yaxis_title='Times Selected (out of 10)',
    template='plotly_dark',
    height=500,
    xaxis=dict(tickangle=45, tickfont=dict(size=9)),
)

# ============================================================
# ASSEMBLE FULL HTML DASHBOARD
# ============================================================

print("\nAssembling full HTML dashboard...")

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NBA Roster Optimization Engine — Interactive Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ background: #0a0a1a; color: #fff; font-family: 'Segoe UI', Calibri, sans-serif; }}
        .header {{
            background: linear-gradient(135deg, #1B2A4A 0%, #0d1b2e 100%);
            padding: 40px 60px;
            border-bottom: 3px solid #C9A84C;
        }}
        .header h1 {{ color: #C9A84C; font-size: 32px; margin-bottom: 8px; }}
        .header p {{ color: #aaa; font-size: 15px; }}
        .stats-bar {{
            display: flex; gap: 40px; margin-top: 16px;
        }}
        .stat-box {{
            background: rgba(201, 168, 76, 0.1);
            border: 1px solid #C9A84C;
            border-radius: 8px;
            padding: 12px 24px;
            text-align: center;
        }}
        .stat-box .number {{ color: #C9A84C; font-size: 28px; font-weight: bold; }}
        .stat-box .label {{ color: #aaa; font-size: 12px; margin-top: 4px; }}
        .nav {{
            background: #111;
            padding: 12px 60px;
            border-bottom: 1px solid #333;
            position: sticky; top: 0; z-index: 100;
        }}
        .nav a {{
            color: #C9A84C; text-decoration: none; margin-right: 24px;
            font-size: 14px; font-weight: 600;
        }}
        .nav a:hover {{ color: #fff; }}
        .section {{
            padding: 40px 60px;
            border-bottom: 1px solid #1a1a2e;
        }}
        .section h2 {{
            color: #C9A84C; font-size: 22px; margin-bottom: 8px;
        }}
        .section p {{
            color: #888; font-size: 14px; margin-bottom: 20px;
        }}
        .chart-container {{
            background: #111;
            border-radius: 12px;
            padding: 10px;
            margin-bottom: 20px;
        }}
        .footer {{
            background: #1B2A4A;
            padding: 30px 60px;
            text-align: center;
            color: #888;
            font-size: 13px;
        }}
    </style>
</head>
<body>

<div class="header">
    <h1>NBA ROSTER OPTIMIZATION ENGINE</h1>
    <p>Interactive Dashboard — PCA Scoring | K-Means Archetypes | MILP Optimization | Synergy Model</p>
    <div class="stats-bar">
        <div class="stat-box">
            <div class="number">1,185</div>
            <div class="label">Player-Seasons</div>
        </div>
        <div class="stat-box">
            <div class="number">9</div>
            <div class="label">Validated Stats</div>
        </div>
        <div class="stat-box">
            <div class="number">6</div>
            <div class="label">Archetypes</div>
        </div>
        <div class="stat-box">
            <div class="number">10</div>
            <div class="label">Optimized Rosters</div>
        </div>
        <div class="stat-box">
            <div class="number">175</div>
            <div class="label">Quality Checks Passed</div>
        </div>
    </div>
</div>

<div class="nav">
    <a href="#value-map">Value Map</a>
    <a href="#rankings">Rankings</a>
    <a href="#archetypes">Archetypes</a>
    <a href="#radar">Stat Profiles</a>
    <a href="#scenarios">Scenarios</a>
    <a href="#roster">Roster A</a>
    <a href="#synergy">Synergy</a>
    <a href="#frequency">Player Frequency</a>
</div>

<div class="section" id="value-map">
    <h2>Player Value Map — Score vs Salary</h2>
    <p>Each dot is a player. Top-left = high value (great score, low salary). Bottom-right = overpaid. Hover for details.</p>
    <div class="chart-container">
        <div id="chart1"></div>
    </div>
</div>

<div class="section" id="rankings">
    <h2>Top 30 Player Rankings</h2>
    <p>PCA-derived composite scores. Colors = archetype. Scores are 0-100, data-driven with zero human bias.</p>
    <div class="chart-container">
        <div id="chart2"></div>
    </div>
</div>

<div class="section" id="archetypes">
    <h2>Archetype Distribution</h2>
    <p>K-Means clustering (K=7) grouped 399 players into 6 archetype categories based on their 9-stat profiles.</p>
    <div class="chart-container">
        <div id="chart3"></div>
    </div>
</div>

<div class="section" id="radar">
    <h2>Archetype Stat Fingerprints</h2>
    <p>Average normalized stat profile per archetype. Each archetype has a distinct shape — proving the clusters are real, not random.</p>
    <div class="chart-container">
        <div id="chart4"></div>
    </div>
</div>

<div class="section" id="scenarios">
    <h2>10-Scenario Comparison</h2>
    <p>Total synergy-adjusted score and salary used across all 10 optimization scenarios.</p>
    <div class="chart-container">
        <div id="chart5"></div>
    </div>
</div>

<div class="section" id="roster">
    <h2>Scenario A — Hard Cap Roster</h2>
    <p>The mathematically optimal 15-man roster under a $136M salary cap. Salary shown on each bar.</p>
    <div class="chart-container">
        <div id="chart6"></div>
    </div>
</div>

<div class="section" id="synergy">
    <h2>Top Synergy Pairs</h2>
    <p>Player pairs with the strongest observed two-way chemistry from 2-man lineup data. Green = positive synergy.</p>
    <div class="chart-container">
        <div id="chart7"></div>
    </div>
</div>

<div class="section" id="frequency">
    <h2>Most Selected Players Across All Scenarios</h2>
    <p>Players who appear in the most optimized rosters — the truly indispensable players regardless of strategy.</p>
    <div class="chart-container">
        <div id="chart8"></div>
    </div>
</div>

<div class="footer">
    NBA Roster Optimization Engine | Python + PCA + K-Means + MILP + Synergy Model | Public Data, Zero Bias
</div>

"""

# Build chart scripts — decode binary bdata to plain number arrays
import json as _json
import base64 as _b64
import struct as _struct

def _to_plain(obj):
    """Recursively convert Plotly binary data + numpy types to plain Python."""
    if isinstance(obj, dict):
        # Decode Plotly binary-encoded arrays (bdata format)
        if 'bdata' in obj and 'dtype' in obj:
            raw = _b64.b64decode(obj['bdata'])
            fmt_map = {'f8': 'd', 'f4': 'f', 'i4': 'i', 'i2': 'h', 'i1': 'b',
                       'u4': 'I', 'u2': 'H', 'u1': 'B'}
            fmt = fmt_map.get(obj['dtype'], 'd')
            n = len(raw) // _struct.calcsize(fmt)
            return list(_struct.unpack(f'<{n}{fmt}', raw))
        return {k: _to_plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_plain(v) for v in obj]
    if hasattr(obj, 'tolist'):
        return obj.tolist()
    if type(obj).__module__ == 'numpy':
        return obj.item()
    return obj

chart_figures = [
    ('chart1', fig1), ('chart2', fig2), ('chart3', fig3), ('chart4', fig4),
    ('chart5', fig5), ('chart6', fig6), ('chart7', fig7), ('chart8', fig8),
]

script_blocks = ""
for div_id, fig in chart_figures:
    fig_dict = _to_plain(fig.to_dict())
    json_str = _json.dumps(fig_dict)
    script_blocks += f'<script>(function(){{var s={json_str};Plotly.newPlot("{div_id}",s.data,s.layout,{{responsive:true}});}})();</script>\n'

html_final = html_content + "\n" + script_blocks + "\n</body>\n</html>"

output_file = 'NBA_Interactive_Dashboard.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_final)

print(f"\n{'=' * 60}")
print(f"INTERACTIVE DASHBOARD SAVED: {output_file}")
print(f"{'=' * 60}")
print(f"\nCharts included:")
print(f"  1. Player Value Map (Score vs Salary scatter)")
print(f"  2. Top 30 Rankings (horizontal bar)")
print(f"  3. Archetype Distribution (donut chart)")
print(f"  4. Archetype Radar Profiles (spider chart)")
print(f"  5. 10-Scenario Comparison (grouped bar)")
print(f"  6. Roster A Breakdown (bar + salary labels)")
print(f"  7. Top Synergy Pairs (color-coded bar)")
print(f"  8. Player Frequency Across Scenarios (bar)")
print(f"\nOpen {output_file} in any browser to interact with the dashboard.")
print(f"All charts are clickable, hoverable, and zoomable.")
