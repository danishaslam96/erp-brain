#!/usr/bin/env python3
"""
Parse Oracle Forms Library XML files (OLB) into structured JSON + Markdown.
Input: raw/olb_xml/*.xml
Output: knowledge/libs/<library_name>.json + .md
"""
import os
import sys
import json
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {'f': 'http://xmlns.oracle.com/Forms'}

def safe_str(s):
    return s if s is not None else ''

def write_json_md(data, to_markdown_fn, json_path, md_path):
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(to_markdown_fn(data))

def parse_olb_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    obj_lib = root.find('f:ObjectLibrary', NS)
    if obj_lib is None:
        print(f"WARNING: No ObjectLibrary found in {xml_path}")
        return None
    
    lib_name = obj_lib.get('Name', 'UNKNOWN')
    obj_count = obj_lib.get('ObjectCount', '0')
    
    result = {
        'name': lib_name,
        'object_count': int(obj_count),
        'source_file': Path(xml_path).name,
        'tabs': []
    }
    
    for tab_elem in obj_lib.findall('f:ObjectLibraryTab', NS):
        tab = {
            'name': tab_elem.get('Name', ''),
            'label': safe_str(tab_elem.get('Label', '')),
            'object_count': int(tab_elem.get('ObjectCount', '0')),
            'items': [],
            'program_units': [],
            'triggers': []
        }
        
        # Items (UI widgets)
        for item_elem in tab_elem.findall('f:Item', NS):
            item = {
                'name': item_elem.get('Name', ''),
                'item_type': item_elem.get('ItemType', ''),
                'label': safe_str(item_elem.get('Label', '')),
                'canvas': item_elem.get('CanvasName', ''),
                'column_name': safe_str(item_elem.get('ColumnName', '')),
                'data_type': item_elem.get('DataType', ''),
                'width': item_elem.get('Width', ''),
                'height': item_elem.get('Height', ''),
                'x': item_elem.get('XPosition', ''),
                'y': item_elem.get('YPosition', ''),
            }
            # Triggers inside items
            for trig_elem in item_elem.findall('f:Trigger', NS):
                trigger = {
                    'name': trig_elem.get('Name', ''),
                    'trigger_text': safe_str(trig_elem.get('TriggerText', ''))
                }
                item.setdefault('triggers', []).append(trigger)
            tab['items'].append(item)
        
        # ProgramUnits (PL/SQL procedures, functions, packages)
        for pu_elem in tab_elem.findall('f:ProgramUnit', NS):
            pu = {
                'name': pu_elem.get('Name', ''),
                'type': pu_elem.get('ProgramUnitType', ''),
                'text': safe_str(pu_elem.get('ProgramUnitText', ''))
            }
            tab['program_units'].append(pu)
        
        # Standalone triggers (outside items)
        for trig_elem in tab_elem.findall('f:Trigger', NS):
            trigger = {
                'name': trig_elem.get('Name', ''),
                'trigger_text': safe_str(trig_elem.get('TriggerText', ''))
            }
            tab['triggers'].append(trigger)
        
        result['tabs'].append(tab)
    
    return result

def olb_to_markdown(data):
    lines = []
    lines.append(f"# Object Library: {data['name']}")
    lines.append(f"**Source:** `{data['source_file']}`")
    lines.append(f"**Object Count:** {data['object_count']}")
    lines.append("")
    
    for tab in data['tabs']:
        lines.append(f"## Tab: `{tab['name']}`")
        if tab['label']:
            lines.append(f"**Label:** {tab['label']}")
        lines.append(f"**Objects:** {tab['object_count']}")
        lines.append("")
        
        if tab['program_units']:
            lines.append("### Program Units")
            for pu in tab['program_units']:
                lines.append(f"#### `{pu['name']}` ({pu['type']})")
                lines.append("```plsql")
                # Show first 10 lines
                text = pu['text'].replace('&amp;#10;', '\n').replace('&amp;#x9;', '\t')
                lines.append(text[:500] + ('...' if len(text) > 500 else ''))
                lines.append("```")
                lines.append("")
        
        if tab['triggers']:
            lines.append("### Triggers")
            for trig in tab['triggers']:
                lines.append(f"#### `{trig['name']}`")
                lines.append("```plsql")
                text = trig['trigger_text'].replace('&amp;#10;', '\n').replace('&amp;#x9;', '\t')
                lines.append(text[:300] + ('...' if len(text) > 300 else ''))
                lines.append("```")
                lines.append("")
        
        if tab['items']:
            lines.append("### Items")
            lines.append("| Name | Type | Label | Canvas | Column |")
            lines.append("|------|------|-------|--------|--------|")
            for item in tab['items']:
                label = item['label'].replace('|', '\\|')
                lines.append(f"| `{item['name']}` | {item['item_type']} | {label} | `{item['canvas']}` | `{item['column_name']}` |")
            lines.append("")
    
    return "\n".join(lines)

def main():
    raw_dir = Path(__file__).parent.parent / 'olb_xml'
    knowledge_dir = Path(__file__).parent.parent.parent / 'knowledge' / 'libs'
    knowledge_dir.mkdir(parents=True, exist_ok=True)
    
    xml_files = list(raw_dir.glob('*.xml'))
    if not xml_files:
        print(f"No XML files found in {raw_dir}")
        return
    
    print(f"Found {len(xml_files)} OLB XML files")
    
    for xml_path in xml_files:
        print(f"Processing {xml_path.name}...")
        data = parse_olb_xml(xml_path)
        if data is None:
            continue
        
        base_name = data['name'].lower().replace(' ', '_')
        json_path = knowledge_dir / f"{base_name}.json"
        md_path = knowledge_dir / f"{base_name}.md"
        
        write_json_md(data, olb_to_markdown, json_path, md_path)
        print(f"  → {json_path.name}, {md_path.name}")
    
    print("Done.")

if __name__ == '__main__':
    main()