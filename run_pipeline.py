"""
run_pipeline.py - One-command orchestrator for the full NBA Roster Optimizer.

Runs every stage in order and rebuilds all deliverables:
  feature engineering -> clustering -> labels -> baseline optimizer ->
  synergy -> synergy optimizer -> dashboard -> verification,
  then database, dashboards, Tableau data, and slide deck.

Usage:
    python run_pipeline.py            # run everything
    python run_pipeline.py --core     # pipeline only (skip deliverable builds)

This processes whatever INPUT CSVs are present in the repo
(nba_complete_master.csv, nba_onoff.csv, nba_lineups_2man.csv,
 nba_master_threeyears.csv). It does NOT fetch new data from the NBA API.
To add a new season, see UPDATING.md for the data steps that come first.
"""
import os
import sys
import time
import subprocess


def ensure_charts_dir():
    """Guarantee charts/ exists before any stage writes to it.

    On Windows under OneDrive, a plain charts/ folder gets dehydrated
    mid-run, so we point charts/ at the git-tracked deliverables/charts/
    via a directory junction (which persists). Falls back to a normal
    folder on other systems / clean clones.
    """
    if os.path.isdir("charts"):
        return
    deliverables_charts = os.path.join("deliverables", "charts")
    os.makedirs(deliverables_charts, exist_ok=True)
    if os.name == "nt":
        subprocess.run(
            ["cmd", "/c", "mklink", "/J", "charts",
             deliverables_charts.replace("/", "\\")],
            capture_output=True, text=True,
        )
    if not os.path.isdir("charts"):
        os.makedirs("charts", exist_ok=True)
    print("charts/ ready")

CORE = [
    "01_feature_engineering.py",
    "02_clustering.py",
    "03_fix_labels.py",
    "04_optimizer_expanded.py",
    "05_compute_synergy.py",
    "06_validate_synergy.py",
    "07_optimizer_synergy.py",
    "08_build_dashboard.py",
    "09_verify_pipeline.py",
]

DELIVERABLES = [
    "build_database.py",
    "build_interactive_dashboard.py",
    "build_enhanced_dashboard.py",
    "build_tableau_data.py",
    "build_pptx.py",
]


def run(stage):
    print(f"\n{'=' * 64}\n>>> {stage}\n{'=' * 64}")
    t = time.time()
    result = subprocess.run([sys.executable, stage])
    if result.returncode != 0:
        print(f"\n!!! FAILED at {stage} (exit {result.returncode}). Stopping.")
        sys.exit(result.returncode)
    print(f"--- {stage} done in {time.time() - t:.1f}s")


def main():
    core_only = "--core" in sys.argv
    stages = CORE if core_only else CORE + DELIVERABLES

    ensure_charts_dir()

    start = time.time()
    print("=" * 64)
    print("NBA ROSTER OPTIMIZER - FULL PIPELINE RUN")
    print(f"Stages: {len(stages)}  |  mode: {'core only' if core_only else 'full (with deliverables)'}")
    print("=" * 64)

    for stage in stages:
        run(stage)

    mins = (time.time() - start) / 60
    print(f"\n{'=' * 64}")
    print(f"PIPELINE COMPLETE in {mins:.1f} min")
    print("Regenerated: scores, archetypes, 10x2 rosters, synergy,")
    print("dashboards, SQL database, Tableau exports, and slide deck.")
    print(f"{'=' * 64}")


if __name__ == "__main__":
    main()
