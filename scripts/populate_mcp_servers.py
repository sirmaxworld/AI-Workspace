#!/usr/bin/env python3
"""
Populate MCP Servers Database from Cursor Configuration
Reads ~/.cursor/mcp.json and populates Railway PostgreSQL
"""
import os
import json
import psycopg2
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('/Users/yourox/AI-Workspace/.env')

def load_mcp_config():
    """Load MCP configuration from Cursor"""
    config_path = Path.home() / '.cursor' / 'mcp.json'
    with open(config_path, 'r') as f:
        return json.load(f)

def populate_mcp_servers():
    """Populate MCP servers from configuration"""
    print("="*80)
    print(" "*20 + "POPULATING MCP SERVERS DATABASE")
    print("="*80)

    config = load_mcp_config()
    servers = config.get('mcpServers', {})

    print(f"\nFound {len(servers)} MCP servers in configuration")

    conn = psycopg2.connect(os.getenv('RAILWAY_DATABASE_URL'))
    cursor = conn.cursor()

    inserted = 0
    updated = 0

    for server_name, server_config in servers.items():
        try:
            # Extract configuration
            config_type = server_config.get('type', 'unknown')

            # Determine source type
            if config_type == 'http':
                source_type = 'http'
                source_url = server_config.get('url', '')
            elif config_type == 'stdio':
                command = server_config.get('command', '')
                args = server_config.get('args', [])

                if command == 'npx' and '@smithery/cli' in ' '.join(args):
                    source_type = 'smithery'
                    # Extract smithery package name
                    for i, arg in enumerate(args):
                        if arg == 'run' and i + 1 < len(args):
                            source_url = f"smithery:{args[i+1]}"
                            break
                elif command == 'python3' and args:
                    source_type = 'custom'
                    source_url = args[0]
                else:
                    source_type = 'custom'
                    source_url = f"{command} {' '.join(args)}"
            else:
                source_type = 'unknown'
                source_url = ''

            # Categorize based on name
            category = 'general'
            if 'database' in server_name.lower() or 'postgres' in server_name.lower():
                category = 'database'
            elif 'search' in server_name.lower() or 'exa' in server_name.lower():
                category = 'search'
            elif 'automation' in server_name.lower() or 'playwright' in server_name.lower():
                category = 'automation'
            elif 'intelligence' in server_name.lower() or 'business' in server_name.lower():
                category = 'ai'
            elif 'memory' in server_name.lower() or 'neo4j' in server_name.lower():
                category = 'memory'
            elif 'browser' in server_name.lower():
                category = 'web'

            # Check if exists
            cursor.execute("SELECT id FROM mcp_servers WHERE server_name = %s;", (server_name,))
            existing = cursor.fetchone()

            if existing:
                # Update
                cursor.execute("""
                    UPDATE mcp_servers SET
                        config_type = %s,
                        source_type = %s,
                        source_url = %s,
                        category = %s,
                        config_template = %s,
                        server_metadata = %s,
                        last_updated = %s
                    WHERE server_name = %s;
                """, (
                    config_type,
                    source_type,
                    source_url,
                    category,
                    json.dumps(server_config),
                    json.dumps(server_config),
                    datetime.now(),
                    server_name
                ))
                updated += 1
            else:
                # Insert
                cursor.execute("""
                    INSERT INTO mcp_servers (
                        server_name,
                        display_name,
                        config_type,
                        source_type,
                        source_url,
                        category,
                        config_template,
                        server_metadata,
                        last_updated,
                        verified
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    );
                """, (
                    server_name,
                    server_name,
                    config_type,
                    source_type,
                    source_url,
                    category,
                    json.dumps(server_config),
                    json.dumps(server_config),
                    datetime.now(),
                    True  # Verified since it's from actual config
                ))
                inserted += 1

            print(f"  ✅ {server_name} ({category})")

        except Exception as e:
            print(f"  ⚠️  Error processing {server_name}: {e}")

    conn.commit()

    # Verify
    cursor.execute("SELECT COUNT(*) FROM mcp_servers;")
    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    print(f"\n{'='*80}")
    print(f"✅ MCP Servers Population Complete!")
    print(f"   Inserted: {inserted}")
    print(f"   Updated: {updated}")
    print(f"   Total in database: {total}")
    print(f"{'='*80}")

if __name__ == "__main__":
    populate_mcp_servers()
