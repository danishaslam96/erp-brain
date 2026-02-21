#!/usr/bin/env python3
"""
Extract SGDGROUP schema from Oracle DB via HTTP query service.
Output: knowledge/tables/sgdgroup_schema.json
"""
import os
import sys
import json
import time
import requests
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent.parent
KNOWLEDGE_TABLES = WORKSPACE / 'projects' / 'erp_brain' / 'knowledge' / 'tables'
KNOWLEDGE_TABLES.mkdir(parents=True, exist_ok=True)

OUTPUT_JSON = KNOWLEDGE_TABLES / 'sgdgroup_schema.json'

ENDPOINT = 'http://76.13.17.186:3000/query'
API_KEY = 'ShahzadTex_Secure_2026'

HEADERS = {
    'x-api-key': API_KEY,
    'Content-Type': 'application/json'
}

def query(sql):
    """Execute SQL via HTTP service."""
    payload = {'sql': sql}
    try:
        resp = requests.post(ENDPOINT, headers=HEADERS, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Query failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text[:200]}")
        raise

def fetch_table_list(owner='SGDGROUP', limit=None):
    """Fetch all table names for owner."""
    sql = f"""
    SELECT table_name
    FROM all_tables
    WHERE owner = '{owner}'
    """
    if limit:
        sql += f" AND ROWNUM <= {limit}"
    sql += " ORDER BY table_name"
    rows = query(sql)
    return [r['TABLE_NAME'] for r in rows]

def fetch_columns(owner, table_name):
    """Fetch column definitions for a table."""
    sql = f"""
    SELECT
        column_name,
        data_type,
        data_length,
        data_precision,
        data_scale,
        nullable,
        column_id
    FROM all_tab_columns
    WHERE owner = '{owner}' AND table_name = '{table_name}'
    ORDER BY column_id
    """
    return query(sql)

def fetch_constraints(owner, table_name):
    """Fetch primary key, unique, foreign key constraints."""
    # Primary/Unique
    sql = f"""
    SELECT
        c.constraint_name,
        c.constraint_type,
        cc.column_name,
        cc.position
    FROM all_constraints c
    JOIN all_cons_columns cc ON c.owner = cc.owner
        AND c.constraint_name = cc.constraint_name
        AND c.table_name = cc.table_name
    WHERE c.owner = '{owner}'
        AND c.table_name = '{table_name}'
        AND c.constraint_type IN ('P', 'U')
    ORDER BY c.constraint_name, cc.position
    """
    pkuk = query(sql)
    # Foreign keys (referencing)
    sql = f"""
    SELECT
        c.constraint_name,
        cc.column_name,
        cc.position,
        r.owner AS r_owner,
        r.table_name AS r_table_name,
        rc.column_name AS r_column_name
    FROM all_constraints c
    JOIN all_cons_columns cc ON c.owner = cc.owner
        AND c.constraint_name = cc.constraint_name
        AND c.table_name = cc.table_name
    JOIN all_constraints r ON c.r_owner = r.owner
        AND c.r_constraint_name = r.constraint_name
    JOIN all_cons_columns rc ON r.owner = rc.owner
        AND r.constraint_name = rc.constraint_name
        AND r.table_name = rc.table_name
        AND rc.position = cc.position
    WHERE c.owner = '{owner}'
        AND c.table_name = '{table_name}'
        AND c.constraint_type = 'R'
    ORDER BY c.constraint_name, cc.position
    """
    fks = query(sql)
    return {'primary_unique': pkuk, 'foreign_keys': fks}

def build_schema(owner='SGDGROUP', table_limit=None):
    """Build full schema JSON."""
    print(f"Fetching table list for {owner}...")
    tables = fetch_table_list(owner, limit=table_limit)
    print(f"Found {len(tables)} tables.")
    
    schema = {
        'generated_at_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'owner': owner,
        'tables': {}
    }
    
    for i, table in enumerate(tables, 1):
        print(f"[{i}/{len(tables)}] Processing {table}...")
        try:
            columns = fetch_columns(owner, table)
            constraints = fetch_constraints(owner, table)
            schema['tables'][table] = {
                'columns': columns,
                'constraints': constraints
            }
        except Exception as e:
            print(f"  Error: {e}")
            schema['tables'][table] = {'error': str(e)}
        time.sleep(0.1)  # gentle throttle
    
    return schema

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--owner', default='SGDGROUP', help='Schema owner')
    parser.add_argument('--limit', type=int, help='Limit number of tables')
    parser.add_argument('--output', default=str(OUTPUT_JSON), help='Output JSON path')
    args = parser.parse_args()
    
    schema = build_schema(args.owner, args.limit)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)
    
    print(f"Schema written to {args.output}")
    print(f"Total tables: {len(schema['tables'])}")

if __name__ == '__main__':
    main()