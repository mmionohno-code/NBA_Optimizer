---
step: 09
name: "Pipeline Verification"
script: "09_verify_pipeline.py"
status: "completed"
tags: [pipeline, step-09]
---

# Step 09: Pipeline Verification

← [[08_Dashboard_Builder]] | → _End of pipeline_

**Script:** `09_verify_pipeline.py`

---

## What This Step Does

End-to-end validation script that checks: all expected output files exist, row counts are within expected ranges, no null values in critical columns, salary cap constraints were respected in all scenarios, and composite scores are within [0, 100]. Acts as a smoke test after any pipeline change.

---

## Inputs

  - `All intermediate and final CSVs`

## Outputs

  - `Console validation report`

---

## Key Decisions & Parameters

  - Expected row count ranges are soft bounds (±10%) not hard failures
  - Reports warnings rather than exceptions for partial data issues

---

## Feeds Into

  - _(final step)_

---

## Change Log

| Date | Change | Why |
|---|---|---|
| 2026-05-08 | Initial pipeline run | — |

## Notes

_Add notes about any modifications, experiments, or issues here._
