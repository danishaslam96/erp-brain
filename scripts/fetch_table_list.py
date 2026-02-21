#!/usr/bin/env python3
"""
Fetch SGDGROUP table list via HTTP service.
"""
import json
import requests
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent
OUTPUT = WORKSPACE / 'knowledge' / 'tables' / 'sgdgroup_schema.json'

ENDPOINT = 'http://76.13.17.186:3000/query'
API_KEY = 'ShahzadTex_Secure_2026'

def query(sql):
    payload = {'sql': sql}
    resp = requests.post(ENDPOINT, headers={'x-api-key': API_KEY, 'Content-Type': 'application/json'}, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()

def main():
    sql = "SELECT table_name FROM all_tables WHERE owner = 'SGDGROUP' ORDER BY table_name"
    rows = query(sql)
    tables = [r['TABLE_NAME'] for r in rows]
    
    schema = {
        'generated_at_utc': '2026-02-21T21:55:00Z',  # placeholder
        'owner': 'SGDGROUP',
        'total_tables': len(tables),
        'tables': {table: {'columns': [], 'constraints': {}} for table in tables}
    }
    
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)
    
    print(f"Written {len(tables)} tables to {OUTPUT}")

if __name__ == '__main__':
    main()