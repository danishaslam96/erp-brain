# Project Manifest: ERP Brain

Repo: https://github.com/danishaslam96/erp-brain

## Project Description
ERP Brain is an autonomous agent system designed to interface with the Shahzad Textile Mills Oracle ERP database. It performs data extraction, schema analysis, and report generation.

## Current Status
- **Paused (Waiting)**: Reports frontend server must be fixed to enable report parsing (tracked in GitHub Issue #1).

## Architecture
- **Database**: Oracle ERP (Shahzad Textile Mills).
- **Worker**: Autonomous background worker (OpenClaw/DeepSeek) for execution.
- **Monitor**: CLI-based monitor for state management.

## Goals
1.  **Wait for Dependency**: Monitor the status of the reports frontend server (currently blocking).
2.  **Autonomous Analysis**: Once unblocked, parse reports and analyze the ERP schema.

## Blockers
- **Reports Frontend Server**: The system cannot parse reports until the server issues are resolved. (Status: Blocked/Waiting — see Issue #1)
