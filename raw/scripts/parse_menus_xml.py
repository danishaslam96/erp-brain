#!/usr/bin/env python3
"""
Parse Oracle Forms Menu XML files (MMB) into structured JSON + Markdown.
Input: raw/menus_xml/*.xml
Output: knowledge/menus/<menu_name>.json + .md
"""
import os
import sys
import json
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {'f': 'http://xmlns.oracle.com/Forms'}

def safe_str(s):
    """Return a safe string, replacing None with empty string."""
    return s if s is not None else ''

def write_json_md(data, to_markdown_fn, json_path, md_path):
    """Write JSON and Markdown files."""
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(to_markdown_fn(data))

def parse_menu_xml(xml_path):
    """Parse a single menu XML file."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    # Find MenuModule
    menu_module = root.find('f:MenuModule', NS)
    if menu_module is None:
        print(f"WARNING: No MenuModule found in {xml_path}")
        return None
    
    menu_name = menu_module.get('Name', 'UNKNOWN')
    main_menu = menu_module.get('MainMenu', '')
    
    result = {
        'name': menu_name,
        'main_menu': main_menu,
        'source_file': Path(xml_path).name,
        'menus': []
    }
    
    # Collect all menus
    for menu_elem in menu_module.findall('f:Menu', NS):
        menu = {
            'name': menu_elem.get('Name', ''),
            'items': []
        }
        
        for item_elem in menu_elem.findall('f:MenuItem', NS):
            item = {
                'name': item_elem.get('Name', ''),
                'label': safe_str(item_elem.get('Label', '')),
                'type': item_elem.get('MenuItemType', 'Command'),
                'command_type': item_elem.get('CommandType', ''),
                'submenu': item_elem.get('SubMenuName', ''),
                'menu_item_code': safe_str(item_elem.get('MenuItemCode', '')),
                'visible_in_menu': item_elem.get('VisibleInMenu', 'true') == 'true',
                'enabled': item_elem.get('Enabled', 'true') == 'true',
                'icon_filename': item_elem.get('IconFilename', ''),
                'keyboard_accelerator': item_elem.get('KeyboardAccelerator', ''),
                'magic_item': item_elem.get('MagicItem', ''),
                'display_no_priv': item_elem.get('DisplayNoPriv', 'false') == 'true',
                'visible_in_vertical_toolbar': item_elem.get('VisibleInVerticalMenuToolbar', 'false') == 'true',
                'visible_in_horizontal_toolbar': item_elem.get('VisibleInHorizontalMenuToolbar', 'false') == 'true',
            }
            menu['items'].append(item)
        
        result['menus'].append(menu)
    
    return result

def menu_to_markdown(data):
    """Convert parsed menu data to Markdown."""
    lines = []
    lines.append(f"# Menu Module: {data['name']}")
    lines.append(f"**Source:** `{data['source_file']}`")
    if data['main_menu']:
        lines.append(f"**Main Menu:** `{data['main_menu']}`")
    lines.append("")
    
    for menu in data['menus']:
        lines.append(f"## Menu: `{menu['name']}`")
        lines.append("")
        if menu['items']:
            lines.append("| Name | Label | Type | Submenu | Command | Visible |")
            lines.append("|------|-------|------|---------|---------|---------|")
            for item in menu['items']:
                label = item['label'].replace('|', '\\|')
                submenu = item['submenu'] if item['submenu'] else ''
                cmd_type = item['command_type'] if item['command_type'] else ''
                visible = '✓' if item['visible_in_menu'] else '✗'
                lines.append(f"| `{item['name']}` | {label} | {item['type']} | `{submenu}` | {cmd_type} | {visible} |")
        else:
            lines.append("*(No items)*")
        lines.append("")
    
    return "\n".join(lines)

def main():
    raw_dir = Path(__file__).parent.parent / 'menus_xml'
    knowledge_dir = Path(__file__).parent.parent.parent / 'knowledge' / 'menus'
    knowledge_dir.mkdir(parents=True, exist_ok=True)
    
    xml_files = list(raw_dir.glob('*.xml'))
    if not xml_files:
        print(f"No XML files found in {raw_dir}")
        return
    
    print(f"Found {len(xml_files)} menu XML files")
    
    for xml_path in xml_files:
        print(f"Processing {xml_path.name}...")
        data = parse_menu_xml(xml_path)
        if data is None:
            continue
        
        base_name = data['name'].lower().replace(' ', '_')
        json_path = knowledge_dir / f"{base_name}.json"
        md_path = knowledge_dir / f"{base_name}.md"
        
        write_json_md(data, menu_to_markdown, json_path, md_path)
        print(f"  → {json_path.name}, {md_path.name}")
    
    print("Done.")

if __name__ == '__main__':
    main()