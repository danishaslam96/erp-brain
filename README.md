# ERP Brain

Repo: https://github.com/danishaslam96/erp-brain

## Overview
ERP Brain interfaces with the Shahzad Textile Mills Oracle ERP to extract data, analyze schema, and generate/parse reports.

## Management Protocol (Development.md Hybrid)
- Source of truth: GitHub Issues + Project Board
- State file: `projects/erp-brain/mission-control/state.json`
- Worker: autonomous micro-batches (5–7m) when `in_progress=true`
- Monitor: toggles worker based on actionable issues (unblocked)

## Status
- Paused (Waiting) — reports-frontend server must be fixed to enable parsing. See Issue #1.
- Backfill prior assets: blocked on the location of previous ERP Brain artifacts. See Issue #2.

## Getting Started
1. Install gh CLI and authenticate (`gh auth login`).
2. Labels: blocked, needs-info, on-hold, waiting (created).
3. Open issues on GitHub; add `waiting` if blocked.

## Paths
- Manifest: `projects/erp-brain/docs/PROJECT_MANIFEST.md`
- State: `projects/erp-brain/mission-control/state.json`
- Decisions: `projects/erp-brain/mission-control/decisions.md`
- Progress: `projects/erp-brain/mission-control/progress-log.md`
