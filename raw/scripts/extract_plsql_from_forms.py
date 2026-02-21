#!/usr/bin/env python3
"""
Extract PL/SQL code from parsed Forms JSON files.
Creates initial knowledge/procedures/ directory with PL/SQL found in forms.
"""
import json
import re
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[2]  # projects/erp_brain
FORMS_DIR = ROOT / 'knowledge' / 'forms'
PROCEDURES_DIR = ROOT / 'knowledge' / 'procedures'

# Create procedures directory
PROCEDURES_DIR.mkdir(parents=True, exist_ok=True)

def extract_plsql_from_form(form_json_path: Path):
    """Extract PL/SQL code from a form JSON file."""
    try:
        with open(form_json_path, 'r', encoding='utf-8') as f:
            form_data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"  ERROR reading {form_json_path.name}: {e}")
        return []
    
    form_name = form_data.get('form_name', form_json_path.stem)
    plsql_units = []
    
    # Extract triggers
    for trigger in form_data.get('triggers', []):
        if trigger.get('code'):
            plsql_units.append({
                'name': f"{form_name}.{trigger['name']}",
                'type': 'TRIGGER',
                'form': form_name,
                'trigger_type': trigger.get('type', ''),
                'code': trigger['code'],
                'source': f"Form: {form_name}"
            })
    
    # Extract program units
    for unit in form_data.get('program_units', []):
        if unit.get('code'):
            plsql_units.append({
                'name': f"{form_name}.{unit['name']}",
                'type': unit.get('type', 'PROGRAM_UNIT'),
                'form': form_name,
                'code': unit['code'],
                'source': f"Form: {form_name}"
            })
    
    return plsql_units

def analyze_plsql_code(plsql_code: str):
    """Analyze PL/SQL code to find referenced tables."""
    # Simple regex to find table references
    table_refs = set()
    
    # Look for FROM clauses
    from_matches = re.findall(r'\bFROM\s+([a-zA-Z0-9_$.]+)', plsql_code, re.IGNORECASE)
    for match in from_matches:
        # Clean up table name
        table = match.strip().upper()
        if '.' in table:
            table = table.split('.')[-1]  # Remove schema prefix
        table_refs.add(table)
    
    # Look for INSERT INTO
    insert_matches = re.findall(r'\bINSERT\s+INTO\s+([a-zA-Z0-9_$.]+)', plsql_code, re.IGNORECASE)
    for match in insert_matches:
        table = match.strip().upper()
        if '.' in table:
            table = table.split('.')[-1]
        table_refs.add(table)
    
    # Look for UPDATE
    update_matches = re.findall(r'\bUPDATE\s+([a-zA-Z0-9_$.]+)', plsql_code, re.IGNORECASE)
    for match in update_matches:
        table = match.strip().upper()
        if '.' in table:
            table = table.split('.')[-1]
        table_refs.add(table)
    
    # Look for DELETE FROM
    delete_matches = re.findall(r'\bDELETE\s+FROM\s+([a-zA-Z0-9_$.]+)', plsql_code, re.IGNORECASE)
    for match in delete_matches:
        table = match.strip().upper()
        if '.' in table:
            table = table.split('.')[-1]
        table_refs.add(table)
    
    return sorted(list(table_refs))

def main():
    print(f"Extracting PL/SQL from forms in: {FORMS_DIR}")
    print(f"Output directory: {PROCEDURES_DIR}")
    
    if not FORMS_DIR.exists():
        print(f"ERROR: Forms directory not found: {FORMS_DIR}")
        return
    
    json_files = list(FORMS_DIR.glob('*.json'))
    print(f"Found {len(json_files)} form JSON files")
    
    all_plsql_units = []
    for json_file in json_files:
        print(f"  Processing: {json_file.name}")
        plsql_units = extract_plsql_from_form(json_file)
        all_plsql_units.extend(plsql_units)
    
    print(f"\nFound {len(all_plsql_units)} PL/SQL units in forms")
    
    # Group by type for statistics
    type_counts = {}
    for unit in all_plsql_units:
        unit_type = unit['type']
        type_counts[unit_type] = type_counts.get(unit_type, 0) + 1
    
    print("PL/SQL unit types:")
    for unit_type, count in type_counts.items():
        print(f"  {unit_type}: {count}")
    
    # Save each PL/SQL unit as JSON
    for i, unit in enumerate(all_plsql_units):
        # Analyze code for table references
        unit['tables_referenced'] = analyze_plsql_code(unit['code'])
        
        # Create safe filename
        safe_name = re.sub(r'[^\w\.-]', '_', unit['name'])
        json_file = PROCEDURES_DIR / f"{safe_name}.json"
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(unit, f, indent=2, ensure_ascii=False)
    
    # Create index file
    index_data = {
        'total_plsql_units': len(all_plsql_units),
        'source': 'extracted_from_forms',
        'units_by_type': type_counts,
        'unit_list': [{'name': u['name'], 'type': u['type'], 'form': u['form']} for u in all_plsql_units]
    }
    
    index_file = PROCEDURES_DIR / 'INDEX.md'
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write("# PL/SQL Procedures Index\n\n")
        f.write(f"**Total PL/SQL units:** {len(all_plsql_units)}\n")
        f.write(f"**Source:** Extracted from parsed Oracle Forms\n\n")
        
        f.write("## By Type\n")
        for unit_type, count in type_counts.items():
            f.write(f"- **{unit_type}:** {count}\n")
        
        f.write("\n## Units\n")
        for unit in all_plsql_units:
            f.write(f"\n### {unit['name']} ({unit['type']})\n")
            f.write(f"- **Form:** {unit['form']}\n")
            if unit.get('trigger_type'):
                f.write(f"- **Trigger Type:** {unit['trigger_type']}\n")
            if unit['tables_referenced']:
                f.write(f"- **Tables Referenced:** {', '.join(unit['tables_referenced'])}\n")
            f.write(f"- **Source File:** {unit['name'].replace('.', '_')}.json\n")
    
    print(f"\nSaved {len(all_plsql_units)} PL/SQL units to: {PROCEDURES_DIR}")
    print(f"Created index: {index_file}")

if __name__ == '__main__':
    main()