#!/usr/bin/env python3
"""
Parse Oracle Forms XML files into structured JSON + Markdown.
Outputs directly to knowledge/forms/ directory.
"""
import os
import json
import xml.etree.ElementTree as ET
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]  # projects/erp_brain
XML_DIR = ROOT / 'raw' / 'forms_xml'
OUTPUT_DIR = ROOT / 'knowledge' / 'forms'

# Create output directory
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def parse_form_xml(xml_path: Path):
    """Parse a single Forms XML file."""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"  ERROR parsing {xml_path.name}: {e}")
        return None
    
    form_name = xml_path.stem.replace('_fmb', '')
    
    # Extract basic information
    result = {
        "form_name": form_name,
        "source_file": xml_path.name,
        "blocks": [],
        "items": [],
        "data_sources": [],
        "triggers": [],
        "program_units": []
    }
    
    # Look for blocks
    for block in root.findall('.//BLOCK'):
        block_info = {
            "name": block.get('Name', ''),
            "type": block.get('BlockType', ''),
            "items": []
        }
        
        # Get items in this block
        for item in block.findall('.//ITEM'):
            item_info = {
                "name": item.get('Name', ''),
                "type": item.get('ItemType', ''),
                "prompt": item.get('Prompt', ''),
                "data_type": item.get('Datatype', ''),
                "width": item.get('Width', ''),
                "height": item.get('Height', '')
            }
            block_info["items"].append(item_info)
            result["items"].append(item_info)
        
        result["blocks"].append(block_info)
    
    # Look for data sources (queries)
    for query in root.findall('.//QUERY'):
        query_info = {
            "name": query.get('Name', ''),
            "sql": query.get('SQL', '')
        }
        result["data_sources"].append(query_info)
    
    # Look for triggers
    for trigger in root.findall('.//TRIGGER'):
        trigger_info = {
            "name": trigger.get('Name', ''),
            "type": trigger.get('TriggerType', ''),
            "code": trigger.text.strip() if trigger.text else ""
        }
        result["triggers"].append(trigger_info)
    
    # Look for program units
    for unit in root.findall('.//PROGRAM_UNIT'):
        unit_info = {
            "name": unit.get('Name', ''),
            "type": unit.get('Type', ''),
            "code": unit.text.strip() if unit.text else ""
        }
        result["program_units"].append(unit_info)
    
    return result

def generate_markdown(form_data):
    """Generate Markdown documentation from parsed form data."""
    md = f"""# Form: {form_data['form_name']}

**Source:** {form_data['source_file']}

## Overview
- **Blocks:** {len(form_data['blocks'])}
- **Items:** {len(form_data['items'])}
- **Data Sources:** {len(form_data['data_sources'])}
- **Triggers:** {len(form_data['triggers'])}
- **Program Units:** {len(form_data['program_units'])}

## Blocks
"""
    
    for block in form_data['blocks']:
        md += f"\n### {block['name']} ({block['type']})\n"
        if block['items']:
            md += "| Item | Type | Prompt | Data Type |\n"
            md += "|------|------|--------|-----------|\n"
            for item in block['items']:
                md += f"| {item['name']} | {item['type']} | {item['prompt']} | {item['data_type']} |\n"
        else:
            md += "*No items*\n"
    
    if form_data['data_sources']:
        md += "\n## Data Sources\n"
        for ds in form_data['data_sources']:
            md += f"\n### {ds['name']}\n"
            if ds['sql']:
                md += f"```sql\n{ds['sql']}\n```\n"
    
    if form_data['triggers']:
        md += "\n## Triggers\n"
        for trigger in form_data['triggers']:
            md += f"\n### {trigger['name']} ({trigger['type']})\n"
            if trigger['code']:
                md += f"```plsql\n{trigger['code']}\n```\n"
    
    if form_data['program_units']:
        md += "\n## Program Units\n"
        for unit in form_data['program_units']:
            md += f"\n### {unit['name']} ({unit['type']})\n"
            if unit['code']:
                md += f"```plsql\n{unit['code']}\n```\n"
    
    return md

def main():
    print(f"Parsing Forms XML files from: {XML_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    
    if not XML_DIR.exists():
        print(f"ERROR: XML directory not found: {XML_DIR}")
        return
    
    xml_files = list(XML_DIR.glob('*.xml'))
    print(f"Found {len(xml_files)} XML files")
    
    parsed_count = 0
    for xml_file in xml_files:
        print(f"  Parsing: {xml_file.name}")
        form_data = parse_form_xml(xml_file)
        
        if form_data:
            # Save JSON
            json_file = OUTPUT_DIR / f"{xml_file.stem}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(form_data, f, indent=2, ensure_ascii=False)
            
            # Save Markdown
            md_file = OUTPUT_DIR / f"{xml_file.stem}.md"
            md_content = generate_markdown(form_data)
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            parsed_count += 1
        else:
            print(f"  SKIPPED: {xml_file.name} (parse error)")
    
    print(f"\nSuccessfully parsed {parsed_count}/{len(xml_files)} forms")
    print(f"Output files saved to: {OUTPUT_DIR}")

if __name__ == '__main__':
    main()