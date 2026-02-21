# Project Manifest: ERP Brain

Repo: https://github.com/danishaslam96/erp-brain
Portal: https://schema.shahzadtex.com
**Status: ✅ COMPLETE — Closed 2026-02-21**

---

## What's Live in knowledge/

| Asset | Count | Notes |
|---|---|---|
| `tables/sgdgroup_schema.json` | 1,968 tables | Live from Oracle DB (SGDGROUP) |
| `forms/` | 9 forms | JSON + MD. Only 9 FMBs existed — 1,200+ are compiled FMX (no source) |
| `menus/` | 3 menus | JSON + MD from Windows VM conversion |
| `libs/` | 3 OLBs | JSON + MD |
| `reports/` | 8 RDFs | Binary-scanned. Full XML requires rwconverter (not available) |
| `procedures/` | 263 objects | Packages, triggers, functions from Oracle DB |
| `KB_INDEX.md` | 288 total | Auto-generated master index |

## What the ERP Portal Consumes (erp_portal/backend/)
- `forms_catalog.json` — 800 forms (from Oracle menu registry, not FMB source)
- `reports_index.json` — 304 reports with live SQL from Oracle DB
- `relational-mapping.json` — AI-inferred cross-module relationships

## Known Gaps (Accepted — Will Not Fix)
- FMB source for 1,200+ forms: lost, only compiled FMX binaries remain
- Full RDF report XML: requires Oracle rwconverter (not installed on VM)
- PL/SQL source truncated at 50 lines per object

## Architecture
- **Database**: Oracle ERP, host=110.39.14.50, SID=wizerp, schema=SGDGROUP
- **Worker**: DeepSeek-chat cron (every 7min) — board is now clear, cron remains enabled for future use
- **Windows VM**: SMB mount at /home/danishaslam96/winvm/ — FMB→XML via frmf2xml watcher

## Closing Notes
All planned issues (#1–#17) closed. No open issues remain. Project declared complete.
