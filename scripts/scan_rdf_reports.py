#!/usr/bin/env python3
"""
Binary-scan RDF reports → knowledge/reports/ (JSON + MD)
Extract printable strings, SQL fragments, table references.
"""
import os
import re
import json
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent
RDF_SOURCE = Path('/home/danishaslam96/winvm/in/source')
KNOWLEDGE_REPORTS = WORKSPACE / 'knowledge' / 'reports'
KNOWLEDGE_REPORTS.mkdir(parents=True, exist_ok=True)

INDEX_PATH = KNOWLEDGE_REPORTS / 'INDEX.json'

def extract_strings(data):
    """Extract printable ASCII strings of length >= 4."""
    # Match printable ASCII characters (space to tilde)
    strings = re.findall(rb'[ -~]{4,}', data)
    # Decode with errors ignored
    return [s.decode('ascii', errors='ignore') for s in strings]

def find_sql_fragments(strings):
    """Identify SQL SELECT statements."""
    sqls = []
    for s in strings:
        if 'SELECT' in s.upper() and 'FROM' in s.upper():
            # Heuristic: likely SQL
            sqls.append(s)
    return sqls

def find_table_references(strings):
    """Guess table names (uppercase, contains underscore, no spaces)."""
    tables = set()
    for s in strings:
        # Look for patterns like SGDGROUP.TABLE_NAME or TABLE_NAME
        # Simple: uppercase words with underscores
        candidates = re.findall(r'\b([A-Z][A-Z0-9_]{2,})\b', s)
        for cand in candidates:
            if '_' in cand and not cand.startswith('RPRT_'):
                tables.add(cand)
    return sorted(tables)

def guess_report_title(strings):
    """First string that looks like a title (no SQL, not too long)."""
    for s in strings:
        if len(s) < 100 and 'SELECT' not in s.upper() and 'FROM' not in s.upper():
            # Might be title
            return s
    return ''

def scan_rdf(rdf_path):
    """Scan a single RDF file."""
    with open(rdf_path, 'rb') as f:
        data = f.read()
    
    strings = extract_strings(data)
    sqls = find_sql_fragments(strings)
    tables = find_table_references(strings)
    title = guess_report_title(strings)
    
    return {
        'filename': rdf_path.name,
        'title': title,
        'sql_fragments': sqls,
        'tables_referenced': tables,
        'raw_strings_sample': strings[:50],
        'note': 'Extracted via binary scan. Full XML requires Oracle rwconverter.'
    }

def to_markdown(report):
    """Generate Markdown summary."""
    lines = []
    lines.append(f"# Report: {report['filename']}")
    if report['title']:
        lines.append(f"**Title:** {report['title']}")
    lines.append("")
    lines.append("## SQL Fragments")
    if report['sql_fragments']:
        for sql in report['sql_fragments']:
            lines.append(f"```sql\n{sql}\n```")
    else:
        lines.append("*(No SQL fragments detected)*")
    lines.append("")
    lines.append("## Tables Referenced")
    if report['tables_referenced']:
        for table in report['tables_referenced']:
            lines.append(f"- `{table}`")
    else:
        lines.append("*(No tables detected)*")
    lines.append("")
    lines.append("## Notes")
    lines.append(report['note'])
    return "\n".join(lines)

def main():
    rdf_files = list(RDF_SOURCE.glob('*.rdf'))
    print(f"Found {len(rdf_files)} RDF files")
    
    index = []
    for rdf_path in rdf_files:
        print(f"Scanning {rdf_path.name}...")
        report = scan_rdf(rdf_path)
        
        base = rdf_path.stem.lower().replace(' ', '_')
        json_path = KNOWLEDGE_REPORTS / f"{base}.json"
        md_path = KNOWLEDGE_REPORTS / f"{base}.md"
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(to_markdown(report))
        
        index.append({
            'filename': report['filename'],
            'title': report['title'],
            'tables': report['tables_referenced'],
            'json': json_path.name,
            'md': md_path.name
        })
    
    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print(f"Generated {len(rdf_files)} reports + INDEX.json")

if __name__ == '__main__':
    main()