#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_FORMS = ROOT / 'raw' / 'schema' / 'forms'
ANALYSIS_FORMS = ROOT / 'raw' / 'analysis' / 'forms'
KNOWLEDGE_FORMS = ROOT / 'knowledge' / 'forms'

# Create knowledge/forms directory
KNOWLEDGE_FORMS.mkdir(parents=True, exist_ok=True)

# Copy JSON files from schema/forms to knowledge/forms
if SCHEMA_FORMS.exists():
    json_files = list(SCHEMA_FORMS.glob('*.json'))
    print(f"Found {len(json_files)} JSON files in {SCHEMA_FORMS}")
    for json_file in json_files:
        dest = KNOWLEDGE_FORMS / json_file.name
        shutil.copy2(json_file, dest)
        print(f"Copied {json_file.name} to knowledge/forms/")

# Copy MD files from analysis/forms to knowledge/forms
if ANALYSIS_FORMS.exists():
    md_files = list(ANALYSIS_FORMS.glob('*.md'))
    print(f"Found {len(md_files)} MD files in {ANALYSIS_FORMS}")
    for md_file in md_files:
        dest = KNOWLEDGE_FORMS / md_file.name
        shutil.copy2(md_file, dest)
        print(f"Copied {md_file.name} to knowledge/forms/")

knowledge_files = list(KNOWLEDGE_FORMS.glob('*'))
print(f"Total files in knowledge/forms/: {len(knowledge_files)}")
for f in knowledge_files[:5]:  # Show first 5
    print(f"  - {f.name}")