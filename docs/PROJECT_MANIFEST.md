# Project Manifest: ERP Brain

## Project Description
ERP Brain is an autonomous agent system designed to interface with the Shahzad Textile Mills Oracle ERP database. It performs data extraction, schema analysis, and report generation.

## Current Status
- **Stalled**: Waiting for fixes to the reports frontend server to enable report parsing.
- **Migration**: Currently migrating to the new hybrid PlanSuite/GitHub management protocol.

## Architecture
- **Database**: Oracle ERP (Shahzad Textile Mills).
- **Worker**: Autonomous background worker (OpenClaw/DeepSeek) for execution.
- **Monitor**: CLI-based monitor for state management.

## Goals
1.  **Resume Operations**: Reactivate the project under the new protocol.
2.  **Wait for Dependency**: Monitor the status of the reports frontend server (currently blocking).
3.  **Autonomous Analysis**: Once unblocked, parse reports and analyze the ERP schema.

## Blockers
- **Reports Frontend Server**: The system cannot parse reports until the server issues are resolved. (Status: Blocked/Waiting)
